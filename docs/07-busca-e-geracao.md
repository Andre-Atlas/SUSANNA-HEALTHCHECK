# 7. Busca e geração — RAG em detalhe

RAG (*Retrieval-Augmented Generation*) significa: **primeiro buscar** os trechos relevantes, **depois gerar** a resposta usando só esses trechos. Este documento detalha cada peça depois que o guardrail liberou a pergunta.

## 1. Expansão de siglas

[glossary.py](../susana_rag_backend/app/rag/glossary.py)

O modelo de embeddings não conhece siglas locais: "UBS" fica longe de "Unidade Básica de Saúde" no espaço vetorial. Antes de virar vetor, a pergunta recebe o significado das siglas que contém:

```text
"Onde fica o HRAN?"  →  "Onde fica o HRAN? (HRAN: Hospital Regional da Asa Norte)"
```

Siglas cobertas: UBS, UPA, SAMU, CEAF, SES, SES-DF, CNS, SISREG, HRAN, HRT, HRC, HRG, HRL, HRS, HRSM, EMAD, NRAD. A expansão afeta **só a busca**; o LLM recebe a pergunta original.

| Pergunta | Melhor trecho **sem** expansão | Melhor trecho **com** expansão |
| --- | --- | --- |
| Quais serviços a UBS oferece? | SAMU 192 (0,55) ❌ | Unidades Básicas de Saúde (0,52) ✅ |
| Qual o telefone do SAMU? | Atenção Domiciliar (0,42) ❌ | SAMU 192 parte 1 (0,42) ✅ |
| Onde fica o HRAN? | SAMU 192 (0,67) ❌ | Hospitais Regionais (0,43) ✅ |
| Como retirar remédio no CEAF? | CEAF (0,28) ✅ | CEAF (0,25) ✅ |

## 2. Busca vetorial

[retriever.py `search`](../susana_rag_backend/app/rag/retriever.py#L55)

O Chroma usa um índice **HNSW** (grafo de vizinhança aproximada) no espaço de **cosseno** e devolve os `TOP_K` (3) trechos mais próximos, cada um com:

- `distance = 1 − similaridade_cosseno`, que vai de **0** (mesmo sentido) a **2** (sentido oposto);
- `source = "<header> — <url>"`.

## 3. Limiar de relevância (calibrado)

```python
if not results or results[0].distance > similarity_threshold:   # 0.70
    → "Não encontrei informação suficiente nas fontes oficiais…"   (sem chamar o LLM)
```

O valor **0,70** vem de [calibrate_threshold.py](../susana_rag_backend/ml/retrieval/calibrate_threshold.py), que mede a distância do melhor trecho para 45 perguntas de [threshold_set.jsonl](../susana_rag_backend/ml/retrieval/threshold_set.jsonl) (25 dentro do tema e 20 fora):

| Grupo | Distância mínima | Mediana | Máxima |
| --- | --- | --- | --- |
| Dentro do tema | 0,233 | 0,415 | 0,696 |
| Fora do tema | 0,481 | 0,733 | 0,979 |

Critério: entre os limiares que **aceitam 100% das perguntas do tema**, escolher o que mais recusa perguntas de fora. Com 0,70, 55% das perguntas fora do tema são recusadas antes do LLM (com 1,2, eram 0%). As outras 45% (ex.: "Quem é o presidente do Brasil?", "Como funciona o Bolsa Família?") chegam ao LLM, que deve recusá-las pela regra 2 do prompt.

Os dois grupos se sobrepõem entre 0,48 e 0,70, então nenhum limiar separa tudo. Recusar uma pergunta válida é pior do que deixar o prompt recusar uma de fora. **Sempre que o corpus mudar, rode a calibração de novo.**

## 4. Cache semântico

[retriever.py `SemanticCache`](../susana_rag_backend/app/rag/retriever.py) e [pipeline.py](../susana_rag_backend/app/rag/pipeline.py)

Guarda pares (vetor da pergunta → resposta + fonte) **em memória**, e vale para **as duas rotas**:

- **Busca:** se a pergunta mais parecida já respondida tiver distância **≤ 0,08**, devolve a resposta guardada sem busca nem LLM (`"cached": true` no `done`).
- **Validade:** 1 hora; **capacidade:** 512 itens (remove o mais antigo).
- Guarda respostas normais e "não encontrei". **Não guarda** respostas do fallback, porque na próxima vez o LLM pode estar de volta.
- Perde tudo quando o servidor reinicia. O `redis` está no requirements.txt para uma futura versão persistente, mas ainda não é usado.

## 5. O prompt

[prompts.py](../susana_rag_backend/app/llm/prompts.py)

```text
[system]
Você é a Susana, assistente virtual ADMINISTRATIVA da Secretaria de Saúde do Distrito Federal (SUS-DF).

REGRAS OBRIGATÓRIAS:
1. Responda SOMENTE com base nos TRECHOS OFICIAIS fornecidos. Nunca use conhecimento externo.
2. Se os trechos não contêm a resposta, diga exatamente: "Não encontrei essa informação nas fontes oficiais disponíveis."
3. NUNCA dê orientação clínica: não sugira medicamentos, doses, diagnósticos ou tratamentos. Se a pergunta pedir isso, oriente procurar uma UBS ou ligar para o SAMU 192.
4. Responda em português do Brasil, de forma clara, cordial e objetiva, com no máximo 120 palavras.
5. Ao final, indique o número do trecho usado entre colchetes, por exemplo [1].

[user]
TRECHOS OFICIAIS:
[1] <texto completo do bloco 1, incluindo o cabeçalho [TAG] Título>

[2] <bloco 2>

[3] <bloco 3>

PERGUNTA DO CIDADÃO: <pergunta>
```

O que cada regra resolve:

| Regra | Objetivo |
| --- | --- |
| 1 | *Grounding*: evitar que o LLM invente (alucinação) |
| 2 | Frase padrão de recusa, fácil de detectar e testar |
| 3 | Segunda barreira clínica, para o que passar pelo guardrail |
| 4 | Respostas curtas, em português |
| 5 | Citação do trecho usado |

A URL (`Fonte:`) **não** vai para o prompt, porque o parser a retira do texto do bloco. O LLM vê só o cabeçalho e o corpo.

## 6. Chamada ao LLM (Ollama)

[ollama_adapter.py](../susana_rag_backend/app/llm/ollama_adapter.py)

| Método | Endpoint Ollama | Uso |
| --- | --- | --- |
| `is_ready()` | `GET /api/tags` | No startup: o modelo configurado está baixado? |
| `warm_up()` | `POST /api/generate` (prompt vazio) | No startup: carrega o modelo na RAM/GPU |
| `stream()` | `POST /api/chat` com `stream: true` | Rota `/api/chat/stream`: devolve pedaços via `yield` |
| `generate()` | `POST /api/chat` com `stream: false` | Rota `/api/chat`: devolve o texto inteiro + latência |

Opções enviadas: `temperature 0.1`, `seed 42`, `num_ctx 4096`, `num_predict 350`, `keep_alive 30m`.

Timeouts: **2 s** para conectar e **12 s** para leitura (`LLM_TIMEOUT_S`). No streaming, os 12 s valem para o intervalo **entre pedaços**, não para a resposta inteira. No `generate()`, valem para a resposta inteira: um modelo lento ou uma resposta longa dá timeout e cai no fallback.

Erros (conexão recusada, timeout, HTTP ≠ 2xx, JSON inválido, resposta vazia) viram `LLMUnavailable`.

## 7. Fallback extrativo

Se o LLM falhar (fora do ar, timeout ou qualquer erro inesperado), a Susana não fica sem resposta. As duas rotas devolvem o mesmo texto:

```text
⚠️ [Aviso: O gerador de texto está indisponível. Abaixo constam trechos diretos dos documentos oficiais.]

<texto do trecho 1>

<texto do trecho 2>

<texto do trecho 3>
```

O `done` vem com `"error": true`. Se a falha acontecer **no meio** da geração, o aviso é anexado ao texto parcial.

## 8. Fonte exibida

[pipeline.py `pick_source`](../susana_rag_backend/app/rag/pipeline.py#L53)

| Situação | Fonte enviada no `done` |
| --- | --- |
| O LLM citou um trecho (`[2]`) | A do trecho **citado** (o último número válido do texto) |
| O LLM não citou nada, ou citou um número inexistente | A do trecho mais próximo |
| O LLM respondeu "Não encontrei essa informação…" | **Nenhuma** (a tela mostra "Informação Ausente") |

Antes de 08/10/2026, a fonte era sempre a do trecho mais próximo, mesmo quando o LLM citava outro.

## 9. Registro no MLflow (as duas rotas)

[pipeline.py `_log`](../susana_rag_backend/app/rag/pipeline.py#L181)

Cada pergunta gera um run `query` no experimento `susana-rag`, gravado **depois** do `done`, para não atrasar a resposta:

| Tipo | Nome | Conteúdo |
| --- | --- | --- |
| param | `outcome` | `answered`, `blocked`, `cache_hit`, `no_result` ou `fallback` |
| param | `guardrail_reason` | Motivo do bloqueio, ex. `regex:prescricao`, `ml:p=0.71` |
| param | `llm_used`, `cached` | Se o LLM respondeu; se veio do cache |
| param | `source` | Fonte exibida |
| param | `query_sha256`, `query_chars` | Hash (16 caracteres) e tamanho da pergunta |
| param | `query` | **Só se `MLFLOW_LOG_QUERY_TEXT=true`** (primeiros 200 caracteres) |
| metric | `latency_s`, `llm_latency_ms`, `top_distance` | Tempos e distância do melhor trecho |

**LGPD:** por padrão o texto da pergunta **não** é gravado, porque o cidadão pode digitar nome, CPF ou sintomas. O hash permite contar perguntas repetidas sem guardar o conteúdo.
