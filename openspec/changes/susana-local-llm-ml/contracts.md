# Contratos — Susana RAG Local (change `susana-local-llm-ml`)

> Fonte de verdade das interfaces. Nenhum código de produção deve divergir deste documento sem atualizá-lo.

## 1. Ports (arquitetura hexagonal)

```python
@dataclass(frozen=True)
class RetrievedChunk:
    id: str
    text: str
    source: str        # ex: "[UNIDADE] UBS 1 Asa Sul"
    distance: float    # distância (menor = mais similar)

@dataclass(frozen=True)
class LLMAnswer:
    text: str
    model: str
    latency_ms: int

class LLMPort(Protocol):
    model_name: str
    def generate(self, question: str, contexts: Sequence[RetrievedChunk]) -> LLMAnswer: ...
    # Lança LLMUnavailable (conexão/timeout/resposta inválida)

class IntentClassifierPort(Protocol):
    version: str
    def predict_clinical_proba(self, texts: Sequence[str]) -> List[float]: ...
```

Regras:
- `LLMPort.generate` tem timeout duro configurável (`LLM_TIMEOUT_S`, default 12 s).
- Em `LLMUnavailable`, o pipeline devolve **fallback extrativo** (texto do melhor chunk) com `fallback_used=true`.
- Guardrail final = `regex_bloqueia OR proba >= threshold`. Classificador indisponível ⇒ regex-only (fail-closed) e `guardrail_version="regex-only"`.
- Guardrail aplicado também à **saída** do LLM; saída clínica ⇒ resposta de bloqueio.

## 2. API HTTP

`POST /api/chat`
```json
// request
{"message": "string (1..2000)"}
// response 200
{
  "response": "string",
  "source": "string|null",          // fonte principal (compatível com a UI atual)
  "sources": ["string"],            // todas as fontes citadas
  "is_blocked": false,
  "latency_ms": 0,
  "cached": false,
  "fallback_used": false,
  "model_versions": {"llm": "llama3.1:8b", "embedding": "...", "guardrail": "..."}
}
```
`422` validação; `500` erro genérico sem stack trace.

`POST /api/chat/stream` (SSE, opcional): eventos `meta` (sources, is_blocked), `token` (texto), `done` (latency_ms, fallback_used).

`GET /health` → `{"status":"ok","pipeline_ready":bool,"llm_ready":bool,"guardrail_version":str}`.

## 3. Data contract — dataset do guardrail

| coluna | tipo | regra |
|---|---|---|
| `text` | str | 3..300 chars, sem PII, único após normalização (lower, sem acento, espaços colapsados) |
| `label` | int | 0 = administrativo, 1 = clínico |
| `source` | str | `seed` \| `synthetic` \| `public` |
| `group` | str | id da família (frase-seed de origem); split agrupado por esta coluna |
| `slice` | str | `formal` \| `informal` \| `typo` \| `misto` \| `medicamento` |

Split: 70/15/15 agrupado por `group`, estratificado por `label`, `seed=42`. Pré-processamento ajustado somente no treino. Test set usado uma única vez por iteração.

## 4. Gates de promoção (fail-closed)

| Modelo | Métrica | Gate |
|---|---|---|
| Guardrail | `test_recall_clinico` | ≥ 0,98 |
| Guardrail | `test_precision_admin` | ≥ 0,95 |
| Guardrail | `p95_latency_ms` (1 frase) | ≤ 20 |
| Embedding | `recall_at_3` | ≥ 0,85 |
| Embedding | `p95_embed_ms` | ≤ 150 |
| E2E | `p95_latency_s` | ≤ 15 |
| E2E | `clinical_block_rate` (golden set) | = 1,0 |

## 5. Telemetria (MLflow / logs)
Nunca registrar a pergunta completa. Registrar `query_sha256[:12]`, `latency_ms`, `distance`, `cached`, `fallback_used`, `is_blocked`, versões de modelo.
