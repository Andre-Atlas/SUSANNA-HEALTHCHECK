# 3. Backend e API (`susana_rag_backend/app/`)

## 3.1 FastAPI e Uvicorn

O backend é uma aplicação **FastAPI** servida pelo **Uvicorn**. O comando de execução é `uvicorn app.main:app --port 8000`: "no módulo `app.main`, use o objeto `app`".

- **FastAPI** define rotas com funções Python e valida entradas e saídas com **Pydantic**. Gera documentação interativa em `/docs`.
- **Uvicorn** é o servidor **ASGI**: recebe as conexões HTTP e chama o FastAPI.

## 3.2 Configuração ([config.py](../susana_rag_backend/app/config.py))

A classe `Settings` herda de `BaseSettings` (pydantic-settings). Cada atributo pode ser sobrescrito por uma variável de ambiente de mesmo nome em maiúsculas, ou por um arquivo `.env` na pasta do backend. **Não existe arquivo `.env` neste projeto**, então valem os padrões:

| Parâmetro | Valor | Significado |
|---|---|---|
| `ollama_base_url` | `http://localhost:11434` | Endereço do Ollama |
| `ollama_model` | `llama3.1:8b` | Modelo de linguagem |
| `llm_timeout_s` | 12.0 | Tempo máximo de espera do Ollama |
| `llm_keep_alive` | `30m` | Quanto tempo o Ollama mantém o modelo na memória |
| `llm_num_predict` | 350 | Máximo de tokens gerados por resposta |
| `embedding_model` | `paraphrase-multilingual-MiniLM-L12-v2` | Modelo de embeddings |
| `similarity_threshold` | 1.2 | Distância máxima para aceitar o melhor trecho |
| `top_k` | 3 | Declarado, mas **não é lido**: o `k=3` está fixo no código |
| `docs_dir` | `data/corpus` | Pasta dos `.txt` indexados |
| `chroma_dir` | `data/chroma_db` | Pasta do banco vetorial |
| `guardrail_model_uri` | `models:/susana-guardrail@champion` | Qual modelo do MLflow carregar |
| `guardrail_enabled_ml` | `True` | Se `False`, usa só regex |
| `mlflow_tracking_uri` | `sqlite:///.../mlflow.db` | Onde o MLflow grava |
| `mlflow_log_requests` | `True` | Registrar cada pergunta no MLflow |

`get_settings()` usa `@lru_cache`, então a configuração é lida uma vez e reaproveitada.

## 3.3 Inicialização ([main.py](../susana_rag_backend/app/main.py))

Duas coisas acontecem **na importação do módulo**, antes de o servidor aceitar conexões:

```python
settings = get_settings()
guardrails = GuardrailsClassifier()   # carrega o modelo do MLflow
pipeline: RAGPipeline | None = None
```

Depois, o FastAPI executa a função `lifespan`, que é o gancho de inicialização e encerramento:

| Passo | O que faz | Tempo aproximado observado |
|---|---|---|
| 1 | Configura o MLflow e o experimento `susana-rag` | < 1 s |
| 2 | Carrega o modelo de embeddings | 2 a 5 s |
| 3 | Abre o ChromaDB em `data/chroma_db` | < 1 s |
| 4 | Cria o `OllamaAdapter` | imediato |
| 5 | Cria o `SemanticCache` (distância máxima 0,08) | imediato |
| 6 | Monta o `RAGPipeline` com as peças acima | imediato |
| 7 | Lê os `.txt` do corpus e indexa os blocos novos | imediato se nada mudou |
| 8 | Se o Ollama tiver o modelo, faz *warm-up* | < 1 s se já carregado |

Tudo que vem antes do `yield` roda na subida; o que vem depois roda no desligamento.

O **warm-up** envia ao Ollama um prompt vazio só para forçar o carregamento do modelo na memória. Sem isso, a primeira pergunta de um usuário pagaria o custo de carregar 4,9 GB (*cold start*).

A indexação está dentro de `if True:` com o comentário "forçar re-indexação". Na prática ela não reindexa tudo: só acrescenta blocos cujo id ainda não existe (ver [04](04-rag.md)). No log desta máquina: `Indexação: 0 novos / 27 total`.

Enquanto o `lifespan` não termina, `pipeline` vale `None` e as rotas de chat respondem **503**.

## 3.4 Rotas

### `GET /health`

Devolve `{"status": "ok", "pipeline_ready": true}`. Serve para saber se a inicialização terminou. Não verifica se o Ollama está respondendo.

### `POST /api/chat` (resposta completa, sem streaming)

Entrada, validada por Pydantic:

```json
{"message": "texto entre 1 e 2000 caracteres"}
```

Saída:

```json
{"response": "...", "source": "... ou null", "is_blocked": false, "latency_ms": 3446}
```

Fluxo: guardrail → `pipeline.query(msg)` → resposta. Um erro inesperado vira **500** com mensagem genérica, sem expor o *stack trace*.

**Esta rota não é usada pelo frontend.** Ela é usada pelos testes automatizados.

### `POST /api/chat/stream` (streaming, usada pela tela)

Definida em [routers_stream.py](../susana_rag_backend/app/routers_stream.py). Mesma entrada. A saída é NDJSON com três desfechos possíveis:

| Situação | Linhas enviadas |
|---|---|
| Pergunta clínica | `chunk` com a recusa + `done` com `is_blocked: true` |
| Nenhum trecho, ou distância do melhor > 1,2 | `chunk` "Não encontrei informação suficiente..." + `done` com `source: null` |
| Contexto encontrado | Um `chunk` por pedaço gerado pelo LLM + `done` com `source` |
| LLM falha no meio | `chunk` "[Fallback Extrativo]" + texto do melhor trecho + `done` com `error: true` |

A resposta usa `StreamingResponse` do Starlette, que recebe um **gerador** Python e envia cada `yield` assim que ele ocorre.

### Códigos de status

| Código | Quando |
|---|---|
| 200 | Resposta normal, **inclusive pergunta bloqueada** (o bloqueio vem no campo `is_blocked`) |
| 422 | Corpo inválido: campo ausente, vazio ou com mais de 2000 caracteres |
| 500 | Erro interno em `/api/chat` |
| 503 | Pipeline ainda inicializando |

## 3.5 As duas rotas não fazem a mesma coisa

Este é um dos pontos mais importantes do backend. A lógica de RAG existe **duas vezes**: uma em `RAGPipeline.query` (usada por `/api/chat`) e outra escrita à mão dentro da rota de streaming.

| Recurso | `/api/chat` | `/api/chat/stream` |
|---|---|---|
| Guardrail | Sim | Sim |
| Cache semântico | Sim | **Não** |
| Registro no MLflow | Sim | **Não** |
| Fallback extrativo se o LLM cair | Sim, os 3 trechos | Sim, só o melhor trecho |
| Mensagem de recusa | Versão longa (cita UBS e SAMU 192) | Versão curta |
| Usada pelo frontend | Não | Sim |
| Coberta pelos testes | Sim | **Não** |

Consequência: **o que o usuário usa na tela não passa pelo cache, não é registrado no MLflow e não é testado.** O cache semântico e a telemetria funcionam, mas só no caminho que a interface não usa.

## 3.6 Assíncrono na assinatura, síncrono por dentro

As rotas são declaradas com `async def`, mas chamam código **bloqueante**: o cálculo do embedding (PyTorch), a busca no ChromaDB e, em `/api/chat`, a chamada HTTP ao Ollama feita com `httpx.Client` síncrono.

Em um servidor ASGI, uma função `async def` roda no laço de eventos. Código bloqueante dentro dela **trava o laço**: enquanto uma pergunta é processada, o servidor não atende mais ninguém, nem o `/health`.

No streaming a situação é parcialmente melhor: o gerador é síncrono, e o Starlette executa geradores síncronos em uma *thread* separada. A geração de tokens não trava o laço, mas o embedding e a busca, que ficam no corpo da função `async`, travam.

Para um protótipo com um usuário, isso não aparece. Para vários usuários simultâneos, seria preciso declarar as rotas com `def` simples (o FastAPI as joga para um *pool* de threads), ou usar `httpx.AsyncClient` e `run_in_threadpool`.

## 3.7 CORS

```python
allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
```

Qualquer site pode chamar a API. É necessário algum CORS porque o frontend (porta 3000) e o backend (porta 8000) são origens diferentes. Liberar `*` é aceitável em desenvolvimento; em produção o correto é listar só o domínio do frontend.

## 3.8 Importação circular

`routers_stream.py` faz `import app.main` para ler as variáveis globais `pipeline` e `guardrails`. E `main.py` importa `routers_stream` **na última linha do arquivo**. É uma dependência circular que só funciona por causa da ordem: quando `routers_stream` é importado, `main` já definiu tudo.

O acesso é feito por `app.main.pipeline` a cada requisição, e não por `from app.main import pipeline`, porque `pipeline` começa como `None` e é reatribuída no `lifespan`; um `from ... import` copiaria o `None`.

A forma idiomática no FastAPI seria usar `Depends(...)` ou guardar o pipeline em `app.state`.

## 3.9 O que a API não tem

- Autenticação e autorização.
- Limite de requisições por cliente (*rate limiting*).
- Histórico de conversa (cada pergunta é isolada).
- Registro estruturado de auditoria.

São ausências esperadas em uma prova de conceito, mas necessárias antes de qualquer uso real.
