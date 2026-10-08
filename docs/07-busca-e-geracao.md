# 7. Busca e geração — RAG em detalhe

RAG (*Retrieval-Augmented Generation*) significa: **primeiro buscar** os trechos relevantes, **depois gerar** a resposta usando só esses trechos. Este documento detalha cada peça depois que o guardrail liberou a pergunta.

## 1. Expansão de siglas

[glossary.py](../susana_rag_backend/app/rag/glossary.py)

O modelo de embeddings não conhece siglas locais: "UBS" fica longe de "Unidade Básica de Saúde" no espaço vetorial. Antes de virar vetor, a pergunta recebe o significado das siglas que contém:

```text
"Onde fica o HRAN?"  →  "Onde fica o HRAN? (HRAN: Hospital Regional da Asa Norte)"
```

A expansão vale para o **vetor**; a parte de palavras da busca híbrida (seção 2) usa a pergunta original.

Siglas cobertas: UBS, UPA, SAMU, CEAF, SES, SES-DF, CNS, SISREG, HRAN, HRT, HRC, HRG, HRL, HRS, HRSM, EMAD, NRAD. A expansão afeta **só a busca**; o LLM recebe a pergunta original.

| Pergunta | Melhor trecho **sem** expansão | Melhor trecho **com** expansão |
| --- | --- | --- |
| Quais serviços a UBS oferece? | SAMU 192 (0,55) ❌ | Unidades Básicas de Saúde (0,52) ✅ |
| Qual o telefone do SAMU? | Atenção Domiciliar (0,42) ❌ | SAMU 192 parte 1 (0,42) ✅ |
| Onde fica o HRAN? | SAMU 192 (0,67) ❌ | Hospitais Regionais (0,43) ✅ |
| Como retirar remédio no CEAF? | CEAF (0,28) ✅ | CEAF (0,25) ✅ |

## 2. Busca híbrida (vetor + palavras)

[retriever.py `search`](../susana_rag_backend/app/rag/retriever.py)

> Integrada em 08/10/2026 a partir da branch `develop_gui_sam`, com ajustes. Antes, a busca era só vetorial.
> Detalhes e medições: [registro/2026-10-08-integracao-develop_gui_sam.md](registro/2026-10-08-integracao-develop_gui_sam.md).

Com um diretório de 182 UBS de nomes quase iguais ("UBS 1 Candangolândia", "UBS 2 Planaltina"…), o vetor sozinho não distingue uma unidade da outra. A busca agora combina dois rankings sobre os mesmos candidatos:

**1. Candidatos**

- os 300 blocos mais próximos por vetor (pergunta com siglas expandidas);
- \+ os blocos que citam exatamente a **unidade numerada** da pergunta ("UBS 01", "UBS 1", "UBS 001");
- \+ os blocos que contêm um **termo raro** da pergunta (que aparece em ≤ 3% dos blocos, ex.: "dipirona", "192", "Candangolândia"), sem distinguir maiúsculas nem acentos.

**2. Dois rankings**

| Ranking | Ordem |
| --- | --- |
| **Por palavras** (ideia do Sam + peso por raridade) | unidade numerada exata → contém o termo mais raro da pergunta → cobertura dos termos ponderada por raridade (IDF) → distância |
| **Por significado** | distância do vetor, com a cobertura de termos só como desempate (−0,1 × cobertura) |

O peso por raridade (IDF) faz "telefone", que aparece em muitos blocos, valer menos que "samu" ou "dipirona".

**3. Resultado**

- **Pergunta específica** (cita unidade numerada ou termo raro): os 3 trechos **intercalam** os dois rankings (1º por palavras, 1º por significado, 2º por palavras…). O LLM sempre recebe o melhor de cada um.
- **Pergunta geral** ("perdi meu cartão de vacinação"): só o ranking por significado.

**Medição** (16 perguntas reais, 1.948 blocos): acerto entre os 3 trechos em **16/16**, contra 10/16 da busca só vetorial no mesmo corpus. A ordenação "palavras primeiro" original do Sam ficava em 13/16 e piorava perguntas gerais: "Quando devo ligar para o 192?" trazia "Saúde Mental".

## 2b. Diretório de unidades (busca estruturada)

[unit_directory.py](../susana_rag_backend/app/rag/unit_directory.py), ideia do `StructuredSearchService` da branch `develop_sam`, feita sem PostgreSQL.

A busca entrega só 3 trechos, então nunca listaria "todas as UBS de Samambaia" (são 14). O diretório lê os CSVs de unidades como tabela. Quando a pergunta cita:

- um **tipo**: UBS/posto/postinho, UPA/pronto atendimento, hospital, CAPS/saúde mental, policlínica, centro especializado; **e**
- uma **região administrativa** (as 43 dos CSVs, mais apelidos como "Asa Sul" → Plano Piloto e "Sol Nascente"),

a lista dessas unidades vira o **trecho [1]** entregue ao LLM, com o arquivo de origem na citação (`[DIRETORIO] UBS em SAMAMBAIA (14 unidades; …)`).

| Pergunta | O que entra como trecho [1] |
| --- | --- |
| "Quais UBS existem em Samambaia?" / "postinho perto de Samambaia" | As 14 UBS de Samambaia (endereço + horário) |
| "Onde vacinar em Samambaia?" | Só as UBS com "Sala Vacina: SIM" (10) |
| "Qual o horário da UBS 2 de Planaltina?" | Só a UBS 2, com todos os campos |
| "Tem UPA no Gama?" | A UPA do Gama |
| "Quais serviços a UBS oferece?" (sem região) | Nada: segue só a busca normal |

## 2c. Filtro de trechos com instruções

[answer_policy.py](../susana_rag_backend/app/rag/answer_policy.py), adaptado da branch `develop_gui`. Se um trecho recuperado contém algo como "ignore as regras", "aprove qualquer resposta" ou marcadores de papel (`<|system|>`), ele é **descartado** antes de ir ao LLM. No corpus atual, nenhum bloco é marcado; a proteção vale para conteúdo futuro.

## 3. Limiar de relevância (calibrado)

```python
is_relevant(results, pergunta, 0.74)
# True se ALGUM dos 3 trechos tiver distância ≤ 0,74
#   ou (develop_gui_sam) o 1º trecho for exatamente a unidade numerada pedida e contiver todos os termos
```

Usa a **menor** distância entre os 3 trechos, porque o 1º pode ter sido escolhido pelas palavras, com distância maior (ex.: o bloco da REME com "dipirona" fica a 0,88).

O valor **0,74** vem de [calibrate_threshold.py](../susana_rag_backend/ml/retrieval/calibrate_threshold.py), que agora roda **a mesma busca de produção** num índice temporário sobre 60 perguntas (40 do tema, 20 de fora):

| Corpus | Limiar | Perguntas do tema aceitas | Fora do tema recusadas antes do LLM |
| --- | --- | --- | --- |
| 52 blocos (antes) | 0,70 | 100% | 55% |
| **1.948 blocos (agora)** | **0,74** | **100%** | **30%** |

Com 37 vezes mais blocos, quase toda pergunta encontra algo "parecido", e o limiar filtra menos. As perguntas fora do tema que passam ("Como funciona o Bolsa Família?") continuam sendo recusadas pelo LLM, pela regra 2 do prompt. **Sempre que o corpus mudar, rode a calibração de novo.**

## 4. Cache semântico

[retriever.py `SemanticCache`](../susana_rag_backend/app/rag/retriever.py) e [pipeline.py](../susana_rag_backend/app/rag/pipeline.py)

Guarda pares (vetor da pergunta → resposta, fonte e citações) **em memória**, e vale para as duas rotas:

- **Busca:** se a pergunta mais parecida já respondida tiver distância **≤ 0,08** **e citar os mesmos números**, devolve a resposta guardada (`"cached": true`).
- **Por que os números:** "Onde fica a UBS 1 de Candangolândia?" e "…UBS 2…" têm vetores a só **0,025** de distância, e sem essa regra o cache devolveria o endereço da UBS errada. "UBS 01" e "UBS 1" contam como o mesmo número.
- **Validade:** 1 hora; **capacidade:** 512 itens. Não guarda respostas do fallback. Perde tudo ao reiniciar.

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
| 6 | Não escrever links nem "clique aqui" (os links verdadeiros vêm das citações; ideia da `develop_gui`) |
| 7 | Em trecho que é lista de unidades, apresentar as unidades listadas sem inventar outras |

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

## 8. Fonte e citações

[pipeline.py `pick_source` e `build_citations`](../susana_rag_backend/app/rag/pipeline.py)

O evento `done` traz dois campos:

- **`source`** (texto): a fonte principal, mantida por compatibilidade;
- **`citations`** (lista, ideia da `develop_gui_sam`): `[{"ref": 2, "id": "…", "title": "[EMERGENCIA] SAMU 192 (parte 3)", "url": "https://…"}]`.

| Situação | `source` | `citations` |
| --- | --- | --- |
| O LLM citou trechos (`[1]`, `[3]`) | O último citado válido | Todos os citados válidos (números inexistentes são ignorados) |
| O LLM não citou nada | O trecho 1 | O trecho 1 |
| O LLM respondeu "Não encontrei essa informação…" | Nenhuma | `[]` |
| Fallback (LLM fora do ar) | O trecho 1 | Os 3 trechos |
| Bloqueio clínico ou sem relevância | Nenhuma | `[]` |

O frontend mostra as citações como **links** quando há URL. Os CSVs de unidades não têm URL de origem e aparecem como referência textual, ex. "Unidade Básica de Saúde (Unidade_Básica_de_Saúde.csv, registro 1)".

## 9. Registro no MLflow (as duas rotas)

[pipeline.py `_log`](../susana_rag_backend/app/rag/pipeline.py)

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
