# 4. Backend — a API (`susana_rag_backend/app/`)

## Tecnologias

| Biblioteca | Para que |
| --- | --- |
| FastAPI + Uvicorn | Servidor HTTP assíncrono e rotas |
| Pydantic / pydantic-settings | Validação das requisições e leitura do `.env` |
| sentence-transformers | Modelo de embeddings (texto → vetor) |
| ChromaDB | Banco vetorial persistido em disco |
| httpx | Chamadas HTTP para o Ollama |
| MLflow | Registro de experimentos e do modelo do guardrail |
| scikit-learn | Executa o modelo do guardrail (Regressão Logística) |

## Estrutura

```text
app/
├── main.py            → cria o FastAPI, startup (lifespan), /health e /api/chat
├── routers_stream.py  → /api/chat/stream (a rota usada pelo frontend)
├── config.py          → Settings (todas as configurações, lidas do .env)
├── ports.py           → interfaces e tipos compartilhados (arquitetura hexagonal)
├── llm/
│   ├── ollama_adapter.py → implementação do LLMPort falando com o Ollama
│   └── prompts.py        → prompt de sistema + montagem das mensagens
└── rag/
    ├── corpus.py      → lê os .txt e quebra em blocos [TAG] Título
    ├── embeddings.py  → Embedder (sentence-transformers)
    ├── retriever.py   → ChromaRetriever + SemanticCache
    ├── glossary.py    → expansão de siglas (UBS, SAMU, CEAF...) antes da busca
    ├── guardrails.py  → decide() + GuardrailsClassifier (regras + ML)
    └── pipeline.py    → RAGPipeline: guardrail → cache → busca → LLM → fonte → MLflow (usado pelas 2 rotas)
```

## Arquitetura hexagonal (Ports & Adapters)

A ideia: o núcleo (pipeline) depende de **interfaces**, não de implementações concretas. Assim dá para trocar o Ollama por outro LLM, ou usar um LLM falso nos testes, sem mexer no pipeline.

[ports.py](../susana_rag_backend/app/ports.py) define:

| Tipo | O que é |
| --- | --- |
| `RetrievedChunk` | Um trecho devolvido pela busca: `id`, `text`, `source`, `distance` |
| `LLMAnswer` | Resposta completa do LLM: `text`, `model`, `latency_ms` |
| `LLMUnavailable` | Exceção lançada quando o LLM não responde (conexão, timeout, resposta vazia) |
| `LLMPort` | Interface de LLM: `generate()`, `stream()`, `is_ready()` |
| `IntentClassifierPort` | Interface de classificador de intenção. **Declarada, mas não usada**: o `GuardrailsClassifier` não a implementa |

`OllamaAdapter` é o único adaptador de `LLMPort` hoje. `ChromaRetriever`, `Embedder` e `GuardrailsClassifier` são classes concretas, sem interface.

```text
                  ┌───────────────── núcleo ─────────────────┐
  FastAPI  ──►    │ RAGPipeline ──► LLMPort (interface)      │ ──► OllamaAdapter ──► Ollama :11434
  (rotas)         │      │                                   │
                  │      ├──► Embedder ──► sentence-transformers
                  │      ├──► ChromaRetriever ──► ChromaDB (data/chroma_db/)
                  │      └──► SemanticCache (memória)
                  └──────────────────────────────────────────┘
  GuardrailsClassifier ──► MLflow Model Registry (mlflow.db + mlruns/)
```

## `config.py` — configurações

Uma classe `Settings` (pydantic-settings) com valores padrão. Ela lê `susana_rag_backend/.env` e variáveis de ambiente, sem diferenciar maiúsculas e minúsculas. `get_settings()` tem `@lru_cache`, então as configurações são lidas **uma vez por processo**. A lista completa de variáveis está em [01-como-rodar.md](01-como-rodar.md#variáveis-de-ambiente-do-backend).

## `main.py` — inicialização

### Na importação do módulo (antes do servidor aceitar conexões)

```python
settings = get_settings()
guardrails = GuardrailsClassifier()   # já tenta carregar o modelo do MLflow aqui
pipeline = None
```

### `lifespan` — roda uma vez no startup

| Passo | Código | Observação |
| --- | --- | --- |
| 1 | `mlflow.set_tracking_uri` + `set_experiment("susana-rag")` | Falha só gera warning |
| 2 | `Embedder(settings.embedding_model)` | Baixa o modelo do HuggingFace na 1ª vez (~470 MB) |
| 3 | `ChromaRetriever(embedder, chroma_dir)` | Abre/cria a coleção, que tem o nome do modelo |
| 4 | `OllamaAdapter(...)` | Só cria o cliente HTTP, ainda não conecta |
| 5 | `SemanticCache(max_distance=0.08)` | Cache em memória |
| 6 | `RAGPipeline(...)` | Junta tudo |
| 7 | Sincroniza o índice com `data/corpus/*.txt` | Adiciona blocos novos e remove os que saíram do corpus |
| 8 | `llm.is_ready()` → `llm.warm_up()` | Se o modelo não estiver no Ollama, só registra um aviso; a API sobe mesmo assim |

Se o Ollama estiver fora do ar, a API **sobe normalmente**. Cada pergunta cai então no fallback extrativo (texto bruto do trecho).

### CORS

```python
allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
```

Libera qualquer origem, o que é adequado para desenvolvimento e **não deve ir para produção** assim.

## Rotas

### `GET /health`

```json
{"status": "ok", "pipeline_ready": true}
```

`pipeline_ready` fica `false` enquanto o lifespan não terminou. Não verifica se o Ollama está no ar.

### `POST /api/chat/stream` — usada pelo frontend

**Entrada:** `{"message": "<1 a 2000 caracteres>"}`
**Saída:** `application/x-ndjson`, uma linha JSON por evento:

| Evento | Campos | Quando |
| --- | --- | --- |
| `chunk` | `content` | Cada pedaço de texto |
| `done` | `is_blocked`, `source` (opcional), `error` (opcional) | Sempre a última linha |

Os desfechos possíveis:

| Desfecho | Linhas enviadas |
| --- | --- |
| Bloqueio clínico | 1 `chunk` com a recusa + `done {is_blocked: true}` |
| Resposta do cache | 1 `chunk` com a resposta guardada + `done {source, cached: true}` |
| Sem trecho relevante (distância > 0,70) | 1 `chunk` "Não encontrei…" + `done {source: null}` |
| Resposta normal | N `chunk`s do LLM + `done {source: "<trecho citado>"}` (`source: null` se o LLM disse "não encontrei") |
| LLM falhou (antes ou no meio) | `chunk`s até a falha + `chunk` com aviso ⚠️ e os 3 trechos + `done {error: true}` |

Erros HTTP: **422** (mensagem inválida) e **503** (pipeline inicializando). Uma exceção inesperada no meio do stream vira `chunk` "Erro interno…" + `done {error: true}`.

### `POST /api/chat` — sem streaming

**Entrada:** a mesma.
**Saída:**

```json
{"response": "...", "source": "... ou null", "is_blocked": false, "latency_ms": 1234}
```

Usa `RAGPipeline.query()`, que percorre o **mesmo fluxo** da rota de streaming (`query_stream` com `stream_llm=False`) e junta os eventos. Erros: 422, 503 e **500** (exceção no pipeline).

## `routers_stream.py` — como ele acessa o pipeline

```python
import app.main
...
pipeline = app.main.pipeline
```

O roteador lê a variável global de `main.py` **no momento de cada requisição**, porque `pipeline` só é atribuído dentro do lifespan. Depois só transforma cada evento de `pipeline.query_stream()` em uma linha JSON. Não há lógica de negócio na rota.

> Até 08/10/2026 esta rota reimplementava a busca e por isso não tinha cache, MLflow nem a mesma mensagem de bloqueio. Veja [registro/2026-10-08-correcoes-guardrail-corpus-limiar-rotas.md](registro/2026-10-08-correcoes-guardrail-corpus-limiar-rotas.md).

## Logs

Formato: `data | NÍVEL | módulo | mensagem`. Loggers principais:

| Logger | O que registra |
| --- | --- |
| `susana` | Etapas do startup; `BLOCKED`/`ANSWERED` (rota `/api/chat`) |
| `susana.guardrails` | Carregamento do modelo; `BLOCKED by ML Classifier (p=…)` / `BLOCKED by Regex rule` |
| `susana.retriever` | `Indexação: N novos / M total` |
| `susana.llm` | Warm-up; `Ollama indisponível` |
| `susana.rag` | `CACHE HIT`, `LOW RELEVANCE`, `LLM falhou, ativando fallback` (as duas rotas) |
| `susana.stream` | Erros durante o streaming |

## Testes — `tests/test_rag.py`

Testes com `TestClient`, que roda o lifespan de verdade: carrega os modelos, indexa e chama o Ollama. **38 testes, todos passando** em 08/10/2026.

| Classe | Verifica |
| --- | --- |
| `TestHealthcheck` | `/health` responde ok |
| `TestGuardrails` | Bloqueios e liberações pela API, incluindo 4 perguntas clínicas que antes vazavam |
| `TestGuardrailRules` | Regras **sem** ML: bloqueios, exceções administrativas (vacina, "o que tenho que levar"), ML somando proteção |
| `TestStreaming` | Rota do frontend: mensagem de bloqueio com UBS/SAMU 192, `done` com fonte, recusa fora do tema, cache |
| `TestPickSource` | Fonte = trecho citado; sem citação → mais próximo; recusa do LLM → sem fonte |
| `TestGlossary` | Expansão de siglas |
| `TestRAGRetrieval` | "SAMU 192" acha fonte com "SAMU"; vacinação e farmácia acham fonte; "bolo de chocolate" fica sem fonte |
| `TestSemanticCache` | A 2ª chamada da mesma pergunta leva menos de 2 s |
| `TestInputValidation` | Mensagem vazia ou ausente → 422 |
| `TestLatencyTracking` | `latency_ms` presente e ≥ 0 |

```bash
cd susana_rag_backend && .venv/bin/pytest -q
```
