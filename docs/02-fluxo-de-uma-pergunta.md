# 2. O caminho completo de uma pergunta

Este documento acompanha **uma pergunta real** desde o momento em que o cidadão aperta "Enviar" até a resposta terminar de aparecer na tela. Cada etapa aponta o arquivo e a linha onde ela acontece.

Exemplo usado: **"Qual o telefone do SAMU?"**

> Atualizado em 08/10/2026, depois da unificação das rotas, do guardrail híbrido, do limiar calibrado e da expansão de siglas.
> O que mudou e por quê: [registro/2026-10-08-correcoes-guardrail-corpus-limiar-rotas.md](registro/2026-10-08-correcoes-guardrail-corpus-limiar-rotas.md).

---

## Antes de tudo: o que já foi preparado no startup

Quando o backend sobe (`uvicorn app.main:app`), a função `lifespan` em [main.py:45-104](../susana_rag_backend/app/main.py#L45-L104) deixa tudo pronto **uma única vez**, para que cada pergunta seja rápida:

1. **Guardrail carregado.** Já na importação do módulo ([main.py:37](../susana_rag_backend/app/main.py#L37)), o `GuardrailsClassifier` busca no MLflow o modelo `susana-guardrail@champion` (hoje a versão 4). Se não achar, as regras continuam funcionando sozinhas.
2. **MLflow configurado** com o experimento `susana-rag`.
3. **Modelo de embeddings carregado** (`paraphrase-multilingual-MiniLM-L12-v2`, 384 dimensões), que transforma texto em vetor.
4. **ChromaDB aberto** em `data/chroma_db/`.
5. **Corpus sincronizado.** Os arquivos `data/corpus/*.txt` são lidos e quebrados em blocos `[TAG] Título`; blocos novos viram vetores e blocos que **saíram** do corpus são removidos do índice. Hoje são **52 blocos**, todos de páginas oficiais.
6. **LLM aquecido.** Uma chamada vazia ao Ollama carrega o `llama3.1:8b` na memória.
7. **Pipeline montado** (`RAGPipeline`) com guardrail, LLM, embedder, retriever e cache semântico.

Depois disso, `/health` passa a responder `pipeline_ready: true`.

---

## Etapa 1 — O cidadão digita e envia (frontend)

**Arquivo:** [susana-ui/src/app/page.tsx](../susana-ui/src/app/page.tsx)

1. O texto digitado fica no estado `input`.
2. Ao apertar Enter ou clicar em "Enviar", roda `sendMessage()` ([page.tsx:25](../susana-ui/src/app/page.tsx#L25)):
   - ignora mensagem vazia;
   - adiciona o balão do usuário à lista `messages`;
   - adiciona **um balão vazio da Susana**, que será preenchido aos poucos;
   - liga `isLoading`, que mostra o "skeleton" (três barrinhas pulsando).
3. Faz a requisição ([page.tsx:36-40](../susana-ui/src/app/page.tsx#L36-L40)):

```http
POST http://localhost:8000/api/chat/stream
Content-Type: application/json

{"message": "Qual o telefone do SAMU?"}
```

---

## Etapa 2 — A API recebe e valida

**Arquivo:** [routers_stream.py](../susana_rag_backend/app/routers_stream.py)

1. O FastAPI valida o corpo com o modelo Pydantic `ChatRequest`: `message` precisa ter de 1 a 2000 caracteres. Fora disso, responde **422** automaticamente.
2. Se o pipeline ainda não terminou o startup, responde **503 "Pipeline inicializando."**
3. Remove espaços das pontas e chama `pipeline.query_stream(msg)`. **Toda a lógica a partir daqui está em [pipeline.py](../susana_rag_backend/app/rag/pipeline.py)**, que é compartilhado pelas duas rotas. A rota só transforma cada evento em uma linha JSON.

---

## Etapa 3 — Guardrail: a pergunta é clínica?

**Arquivos:** [pipeline.py:111-118](../susana_rag_backend/app/rag/pipeline.py#L111-L118) → [guardrails.py `decide`](../susana_rag_backend/app/rag/guardrails.py#L73) (detalhes em [05-guardrails.md](05-guardrails.md))

A primeira regra que se aplica decide:

```text
1. Regra clínica FORTE? (me prescreva, que remédio devo tomar, sem receita, dose de...) → BLOQUEIA
2. Termo administrativo? (horário, endereço, telefone, agendar, onde fica...)            → LIBERA
3. Regra clínica FRACA? (estou com, estou sentindo, como tratar...)                     → BLOQUEIA
4. Modelo de ML: p(clínica) ≥ 0,40?                                                     → BLOQUEIA
5. Nenhuma das anteriores                                                               → LIBERA
```

**No exemplo:** "Qual o telefone do SAMU?" não tem regra forte e contém "telefone", então é liberada no passo 2.

**Se fosse bloqueada** (ex.: "Me prescreva um remédio para dor de cabeça", regra `prescricao`), a resposta sai imediatamente, sem busca nem LLM:

```json
{"type": "chunk", "content": "Desculpe, não posso ajudar com essa questão. A Susana fornece apenas informações administrativas e institucionais da SES-DF. Para orientações clínicas, procure uma Unidade Básica de Saúde (UBS) ou ligue para o SAMU 192."}
{"type": "done", "source": null, "is_blocked": true}
```

---

## Etapa 4 — Expansão de siglas e vetor da pergunta

**Arquivos:** [glossary.py](../susana_rag_backend/app/rag/glossary.py) e [pipeline.py:120-121](../susana_rag_backend/app/rag/pipeline.py#L120-L121)

O modelo de embeddings não conhece siglas locais. Por isso, antes de virar vetor, a pergunta recebe o significado das siglas que contém:

```text
"Qual o telefone do SAMU?"
→ "Qual o telefone do SAMU? (SAMU: SAMU 192, Serviço de Atendimento Móvel de Urgência)"
```

O texto expandido vira um vetor de **384 números** que representa o significado da frase. A expansão só afeta a **busca**: o LLM recebe a pergunta original.

Efeito medido: "Quais serviços a UBS oferece?" trazia blocos do SAMU (distância 0,55). Com a expansão, traz a página das UBS. "Onde fica o HRAN?" passou de 0,67 (bloco errado) para 0,43 (Hospitais Regionais).

---

## Etapa 5 — Cache semântico

**Arquivo:** [pipeline.py:122-129](../susana_rag_backend/app/rag/pipeline.py#L122-L129)

Se uma pergunta quase idêntica (distância ≤ 0,08) foi respondida na última hora, a resposta guardada volta na hora, sem busca nem LLM, com `"cached": true` no `done`. Respostas do fallback (LLM fora do ar) **não** são guardadas.

---

## Etapa 6 — Busca dos 3 trechos mais parecidos

**Arquivo:** [retriever.py `search`](../susana_rag_backend/app/rag/retriever.py#L55)

O ChromaDB compara o vetor com os 52 blocos e devolve os 3 mais próximos (`TOP_K`), cada um com o texto do bloco, a fonte (`[TAG] Título — URL`) e a **distância de cosseno** (0 = idêntico, 2 = oposto).

**No exemplo:** o melhor trecho foi `[EMERGENCIA] SAMU 192 (parte 1)`, com distância **0,42**.

---

## Etapa 7 — Filtro de relevância

**Arquivo:** [pipeline.py:131-140](../susana_rag_backend/app/rag/pipeline.py#L131-L140)

```python
if not results or results[0].distance > self.similarity_threshold:   # 0.70, calibrado
```

Se nem o melhor trecho estiver perto o bastante, a Susana **não chama o LLM**:

```json
{"type": "chunk", "content": "Não encontrei informação suficiente nas fontes oficiais disponíveis para responder a essa pergunta. Tente reformular ou pergunte sobre unidades de saúde, vacinação, ou serviços da SES-DF."}
{"type": "done", "source": null, "is_blocked": false}
```

O limiar 0,70 foi calibrado por [calibrate_threshold.py](../susana_rag_backend/ml/retrieval/calibrate_threshold.py): aceita 100% das 25 perguntas de teste do tema e recusa 55% das 20 de fora do tema. Exemplo: "Como fazer bolo de chocolate?" (distância ≈ 1,0) é recusada aqui. As perguntas fora do tema que passam ainda são recusadas pelo LLM (regra 2 do prompt).

**No exemplo:** 0,42 < 0,70, então a pergunta segue.

---

## Etapa 8 — Montagem do prompt

**Arquivo:** [prompts.py](../susana_rag_backend/app/llm/prompts.py)

O LLM recebe duas mensagens:

**Sistema**, com as regras fixas:

> Você é a Susana, assistente virtual ADMINISTRATIVA da SES-DF.
> 1. Responda SOMENTE com base nos TRECHOS OFICIAIS fornecidos. 2. Se os trechos não contêm a resposta, diga exatamente: "Não encontrei essa informação nas fontes oficiais disponíveis." 3. NUNCA dê orientação clínica… 4. Português, no máximo 120 palavras. 5. Indique o número do trecho usado, ex. [1].

**Usuário**, com os trechos numerados e a pergunta **original**:

```text
TRECHOS OFICIAIS:
[1] [EMERGENCIA] SAMU 192 (parte 1)
...texto do bloco...

[2] ...

[3] ...

PERGUNTA DO CIDADÃO: Qual o telefone do SAMU?
```

---

## Etapa 9 — O LLM gera a resposta, token a token

**Arquivos:** [pipeline.py:142-161](../susana_rag_backend/app/rag/pipeline.py#L142-L161) → [ollama_adapter.py `stream`](../susana_rag_backend/app/llm/ollama_adapter.py#L57-L73)

O backend chama o Ollama em `POST http://localhost:11434/api/chat` com `stream: true`:

| Parâmetro | Valor | Efeito |
| --- | --- | --- |
| `temperature` | 0,1 | Respostas quase determinísticas |
| `seed` | 42 | Reprodutibilidade |
| `num_ctx` | 4096 | Tamanho da janela de contexto |
| `num_predict` | 350 | Máximo de tokens gerados |
| `keep_alive` | 30m | Mantém o modelo carregado entre perguntas |

Cada pedaço gerado vira imediatamente um evento `chunk`.

**Se o LLM falhar** (fora do ar, timeout ou qualquer erro), o fallback extrativo envia um aviso e o texto bruto dos 3 trechos, e marca `"error": true` no `done`:

```text
⚠️ [Aviso: O gerador de texto está indisponível. Abaixo constam trechos diretos dos documentos oficiais.]

<trecho 1>

<trecho 2> ...
```

---

## Etapa 10 — Escolha da fonte e fim do stream

**Arquivo:** [pipeline.py `pick_source`](../susana_rag_backend/app/rag/pipeline.py#L53)

Com o texto completo em mãos, o backend escolhe a fonte:

- se o LLM citou um trecho (`[2]`), a fonte é **a desse trecho**;
- se não citou, é a do trecho mais próximo;
- se o LLM respondeu "Não encontrei essa informação…", **não há fonte** (a tela mostra o selo amarelo "Informação Ausente").

Saída real capturada para o exemplo:

```json
{"type": "chunk", "content": "O"}
{"type": "chunk", "content": " número"}
...
{"type": "done", "source": "[EMERGENCIA] SAMU 192 (parte 1) — https://www.saude.df.gov.br/samu", "is_blocked": false}
```

Texto final: **"O número do SAMU é (61) 192 [1]. Lembre-se de que o SAMU é uma emergência, por isso é importante ligar apenas em casos urgentes."**

Depois do `done`, ainda dentro do stream, a resposta vai para o cache e um registro é gravado no MLflow (desfecho, latência, distância, fonte e **hash** da pergunta, nunca o texto, por causa da LGPD).

---

## Etapa 11 — O frontend monta a resposta na tela

**Arquivo:** [page.tsx:44-87](../susana-ui/src/app/page.tsx#L44-L87)

1. Quando chega a resposta HTTP, o skeleton some.
2. Um `reader` lê o corpo aos pedaços; cada linha passa por `JSON.parse`.
3. **`chunk`**: o texto é acumulado e o último balão é reescrito, o que cria o efeito de "digitando".
4. **`done`**:
   - `is_blocked: true` → borda **vermelha** + "Fora de Escopo / Não Clínico";
   - sem `source` e não bloqueado → borda **amarela** + "Informação Ausente";
   - com `source` → rodapé **"Fonte Oficial: …"**.
5. Se o `fetch` falhar, o balão vira "Desculpe, não consegui conectar aos servidores no momento."

---

## Resumo em uma tabela

| # | Onde | O que acontece | Pode encerrar aqui? |
| --- | --- | --- | --- |
| 0 | `main.py` lifespan | Carrega modelos, sincroniza índice, aquece LLM | — |
| 1 | `page.tsx` | Usuário envia; balão vazio + skeleton | — |
| 2 | `routers_stream.py` | Validação, pipeline pronto? | Sim: 422 / 503 |
| 3 | `guardrails.py` | Forte → override → fraca → ML (≥ 0,40) | **Sim: bloqueio clínico** |
| 4 | `glossary.py` + `embeddings.py` | Expande siglas; pergunta → vetor 384-d | — |
| 5 | `pipeline.py` | Cache semântico | **Sim: resposta do cache** |
| 6 | `retriever.py` | Top-3 trechos no ChromaDB | — |
| 7 | `pipeline.py` | Melhor distância > 0,70? | **Sim: "não encontrei"** |
| 8 | `prompts.py` | Regras + trechos numerados + pergunta original | — |
| 9 | `ollama_adapter.py` | LLM gera token a token | Falha → fallback extrativo |
| 10 | `pipeline.py` | Fonte = trecho citado; cache; MLflow | — |
| 11 | `page.tsx` + `MessageBubble.tsx` | Texto aos poucos; borda/selo/fonte | — |

---

## E a rota `/api/chat` (sem streaming)?

[main.py `chat_endpoint`](../susana_rag_backend/app/main.py#L149) chama `pipeline.query()`, que **percorre exatamente o mesmo fluxo** (`query_stream` com `stream_llm=False`) e junta os eventos num JSON só:

```json
{"response": "...", "source": "...", "is_blocked": false, "latency_ms": 1234}
```

Antes de 08/10/2026 as duas rotas tinham lógicas separadas e divergentes: a de streaming não tinha cache nem MLflow e usava outra mensagem de bloqueio. Hoje elas só diferem no formato de saída.
