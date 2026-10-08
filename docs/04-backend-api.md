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
    ├── corpus.py      → lê txt/md/csv/json/html/pdf (recursivo) e quebra em blocos
    ├── embeddings.py  → Embedder (sentence-transformers)
    ├── retriever.py   → ChromaRetriever (busca híbrida + is_relevant) + SemanticCache
    ├── glossary.py    → expansão de siglas (UBS, SAMU, CEAF...) antes da busca
    ├── emergency.py   → sinais de emergência → SAMU 192 / CVV 188 (RNF06)
    ├── unit_directory.py → lista unidades por tipo + região (CSVs de CORPUS/Arquivos)
    ├── answer_policy.py  → descarta trechos com instruções; detecta links escritos pelo LLM
    ├── guardrails.py  → decide() + GuardrailsClassifier (regras + ML)
    └── pipeline.py    → RAGPipeline: guardrail → cache → busca → LLM → fonte → MLflow (usado pelas 2 rotas)
```

## Arquitetura hexagonal (Ports & Adapters)

A ideia: o núcleo (pipeline) depende de **interfaces**, não de implementações concretas. Assim dá para trocar o Ollama por outro LLM, ou usar um LLM falso nos testes, sem mexer no pipeline.

[ports.py](../susana_rag_backend/app/ports.py) define:

| Tipo | O que é |
| --- | --- |
| `RetrievedChunk` | Um trecho devolvido pela busca: `id`, `text`, `source`, `distance`, `url` |
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
| 7 | Sincroniza o índice com `data/corpus/` + `CORPUS/Arquivos/` | 1.948 blocos (~28 s na 1ª vez); adiciona novos e remove os que saíram |
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

`pipeline_ready` fica `false` enquanto o lifespan não terminou. Não verifica se o Ollama está no ar; para isso, use a rota abaixo.

### `GET /health/dependencies` (ideia da `develop_sam`)

Separa **falha técnica** de **falta de conteúdo**:

```json
{"status": "ok", "pipeline_ready": true,
 "llm": {"model": "llama3.1:8b", "ready": true},
 "embeddings": {"model": "paraphrase-multilingual-MiniLM-L12-v2", "max_seq_length": 256},
 "corpus": {"indexed_blocks": 1979, "unit_directory": 340, "roots": ["…/data/corpus", "…/CORPUS/Arquivos"]},
 "guardrail": {"ml_model_loaded": true, "model_uri": "models:/susana-guardrail@champion", "threshold": 0.4},
 "similarity_threshold": 0.74}
```

`status` é `degraded` se o LLM não estiver pronto ou o índice estiver vazio.

### `POST /api/chat/stream` — usada pelo frontend

**Entrada:** `{"message": "<1 a 2000 caracteres>"}`
**Saída:** `application/x-ndjson`, uma linha JSON por evento:

| Evento | Campos | Quando |
| --- | --- | --- |
| `chunk` | `content` | Cada pedaço de texto |
| `done` | `status`, `is_blocked`, `source`, `citations` (lista `{ref, id, title, url}`), `cached`/`error`/`warnings` (opcionais) | Sempre a última linha |

Os desfechos possíveis:

| Desfecho | Linhas enviadas |
| --- | --- |
| Possível emergência | 1 `chunk` com SAMU 192 (ou CVV 188) + `done {status: "emergency"}` |
| Bloqueio clínico | 1 `chunk` com a recusa + `done {is_blocked: true, status: "out_of_scope"}` |
| Resposta do cache | 1 `chunk` com a resposta guardada + `done {source, cached: true}` |
| Sem trecho relevante (nenhum dos 3 com distância ≤ 0,74) | 1 `chunk` "Não encontrei…" + `done {source: null}` |
| Resposta normal | N `chunk`s do LLM + `done {source: "<trecho citado>"}` (`source: null` se o LLM disse "não encontrei") |
| LLM falhou (antes ou no meio) | `chunk`s até a falha + `chunk` com aviso ⚠️ e os 3 trechos + `done {error: true}` |

Erros HTTP: **422** (mensagem inválida) e **503** (pipeline inicializando). Uma exceção inesperada no meio do stream vira `chunk` "Erro interno…" + `done {error: true}`.

### `POST /api/chat` — sem streaming

**Entrada:** a mesma.
**Saída:**

```json
{"response": "...", "source": "... ou null",
 "citations": [{"ref": 1, "id": "…", "title": "[EMERGENCIA] SAMU 192 (parte 3)", "url": "https://…"}],
 "status": "answered", "is_blocked": false, "latency_ms": 1234}
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

**86 testes, todos passando** em 08/10/2026, em 4 arquivos:

- `test_rag.py` (61): integração com `TestClient`, que roda o lifespan de verdade (carrega modelos, indexa, chama o Ollama);
- `test_corpus_ingestion.py` (13), `test_retriever.py` (11) e `test_pipeline_citations.py` (1): vindos da `develop_gui_sam`, **rápidos (~2 s) e sem Ollama**.

Para rodar só os rápidos: `.venv/bin/pytest tests/test_corpus_ingestion.py tests/test_retriever.py tests/test_pipeline_citations.py`.

| Classe | Verifica |
| --- | --- |
| `TestHealthcheck` | `/health` responde ok |
| `TestGuardrails` | Bloqueios e liberações pela API, incluindo 4 perguntas clínicas que antes vazavam |
| `TestGuardrailRules` | Regras **sem** ML: bloqueios, exceções administrativas (vacina, "o que tenho que levar"), ML somando proteção |
| `TestStreaming` | Rota do frontend: mensagem de bloqueio com UBS/SAMU 192, `done` com fonte, recusa fora do tema, cache |
| `TestPickSource` | Fonte = trecho citado; sem citação → mais próximo; recusa do LLM → sem fonte |
| `TestGlossary` | Expansão de siglas |
| `TestUnitDirectory` | "Endereço da UBS 1 de Candangolândia" cita o diretório de UBS; o cache não mistura UBS 1 e UBS 2 |
| `TestBuildCitations` | Citações no fallback (todas), na recusa (nenhuma), título sem URL |
| `test_corpus_ingestion.py` | Descoberta recursiva, CSV (separador, agrupamento, um bloco por registro), SIA mensal, 3 esquemas de JSON, HTML/PDF, falha em arquivo corrompido |
| `test_retriever.py` | Remoção de blocos obsoletos, entidade exata à frente de nomes parecidos, "UBS 1" × "UBS 01", entidade fora dos candidatos vetoriais, `is_relevant` |
| `test_pipeline_citations.py` | Só citações reais (ignora `[99]`) |
| `TestEmergency` | SAMU 192 / CVV 188 nos relatos graves; perguntas administrativas sobre o SAMU não disparam |
| `TestUnitDirectoryLookup` | Lista completa por região, unidade numerada sozinha, filtro "farmácia: SIM", sem região → RAG |
| `TestAnswerPolicy` | Detecção de instruções escondidas e de links escritos pelo LLM |
| `TestStatusAndHealth` | `status` out_of_scope/no_evidence; `/health/dependencies` |
| `TestRAGRetrieval` | "SAMU 192" acha fonte com "SAMU"; vacinação e farmácia acham fonte; "bolo de chocolate" fica sem fonte |
| `TestSemanticCache` | A 2ª chamada da mesma pergunta leva menos de 2 s |
| `TestInputValidation` | Mensagem vazia ou ausente → 422 |
| `TestLatencyTracking` | `latency_ms` presente e ≥ 0 |

```bash
cd susana_rag_backend && .venv/bin/pytest -q
```
