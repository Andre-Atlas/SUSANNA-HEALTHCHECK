# 10. Problemas conhecidos e riscos

Levantamento inicial em 08/10/2026 (leitura do código, perguntas reais e `pytest`), **atualizado no mesmo dia** depois da primeira rodada de correções.

**Estado dos testes:** `pytest` → **38 passaram, 0 falharam** (antes: 13 passaram, 1 falhou).

O plano de ação para os itens em aberto está em [PROXIMOS-PASSOS.md](PROXIMOS-PASSOS.md).

---

## ✅ Resolvidos em 08/10/2026

Detalhes de cada correção em [registro/2026-10-08-correcoes-guardrail-corpus-limiar-rotas.md](registro/2026-10-08-correcoes-guardrail-corpus-limiar-rotas.md).

| # | Problema | Como foi resolvido |
| --- | --- | --- |
| P1 | O guardrail de ML deixava passar perguntas clínicas (recall 0,40) e **substituía** as regras | Regras e ML agora somam proteção; rótulos do dataset corrigidos; dataset ampliado para 111 frases; gate real (recall ≥ 0,98, precisão admin ≥ 0,95, admin liberadas ≥ 0,80). Versão 4: recall **0,987** |
| P2 | Dados fictícios exibidos como "Fonte Oficial" | Mock retirado do corpus (agora em `data/mock/`, não indexado); `collect_opendata.py` falha em vez de inventar; o índice remove blocos que saíram do corpus |
| P3 | Mensagem de bloqueio do frontend sem encaminhamento | Constante única `BLOCKED_MESSAGE` com UBS e SAMU 192, nas duas rotas |
| P4 | Limiar de relevância 1,2 não filtrava nada | Calibrado em **0,70** por script (aceita 100% do tema, recusa 55% de fora) |
| P5 | Rotas de chat divergentes (streaming sem cache/MLflow) | Toda a lógica em `RAGPipeline.query_stream`; as rotas só formatam a saída |
| P6 | Fonte exibida ≠ trecho citado | `pick_source` usa o trecho citado; sem fonte quando o LLM recusa |
| P8 | Override administrativo liberava clínica ("onde posso comprar antibiótico sem receita") | Regras fortes rodam **antes** do override |
| P9 | Texto das perguntas gravado no MLflow (LGPD) | Por padrão grava só hash + tamanho (`MLFLOW_LOG_QUERY_TEXT=false`) |
| P12 | Blocos editados/removidos continuavam no ChromaDB | `index(prune=True)` sincroniza o índice com o corpus |
| P13 (parcial) | `top_k` declarado e não usado | `TOP_K` agora é usado pelo pipeline |
| P14 | Dependências dos scripts de coleta fora do requirements | `beautifulsoup4`, `pyyaml` e `requests` adicionados |
| P15 (parcial) | 6 de 11 páginas fora do corpus | URLs atualizadas: 12 de 15 páginas raspadas, 52 blocos (antes 20) |
| P20 | `if True:` temporário no startup | Removido; a sincronização do índice é o comportamento oficial |
| — | Siglas (UBS, HRAN) levavam a buscas erradas | Glossário de siglas expande a pergunta antes da busca |

---

## 🔴 Prioridade alta — em aberto

### A1. Blocos da raspagem com rótulo enganoso

- **Onde:** [collect_corpus.py `chunk`](../susana_rag_backend/ml/corpus/collect_corpus.py)
- **O quê:** a página do SAMU contém uma lista de telefones das equipes de Atenção Domiciliar, que vira o bloco `[EMERGENCIA] SAMU 192 (parte 5)`. O LLM chegou a responder "o telefone do SAMU é (61) 2017-1145", que é o número de uma equipe de Atenção Domiciliar.
- **Situação:** a expansão de siglas fez a busca trazer o bloco certo ("SAMU parte 1", que diz 192), mas o bloco enganoso continua no índice.
- **Correção sugerida:** dividir os blocos pelos subtítulos (`h2`/`h3`) da página e usar o subtítulo no cabeçalho, ex. `[EMERGENCIA] SAMU 192 — Contatos da Atenção Domiciliar`.

### A2. O LLM acrescenta informação que não está nos trechos

- **Exemplo:** para "Quais serviços a UBS oferece?", o `llama3.1:8b` citou "exames laboratoriais e radiológicos", que não aparecem no trecho usado. Para o SAMU, escreveu "(61) 192".
- **Correção sugerida:** uma checagem automática de fidelidade (números e termos da resposta precisam existir nos trechos), testar outros modelos com o benchmark e reforçar o prompt. O gerador de perguntas de teste vai ajudar a medir isso.

---

## 🟠 Prioridade média — em aberto

### P7. Frontend: erros HTTP e linhas partidas

- **Onde:** [page.tsx:42-87](../susana-ui/src/app/page.tsx#L42-L87)
- **O quê:**
  - não verifica `res.ok`, então 503/422 viram um balão vazio;
  - uma linha NDJSON que chega dividida entre dois pacotes falha no `JSON.parse` e o texto se perde;
  - o botão Enviar continua ativo durante o streaming;
  - não há rolagem automática;
  - a fonte aparece como texto e não como link clicável.
- **Correção sugerida:** checar `res.ok`; manter um buffer da última linha incompleta; desabilitar o envio durante a resposta; `scrollIntoView`; separar título e URL da fonte.

### A3. Guardrail ainda bloqueia ~17% das perguntas administrativas

- **Exemplos:** "Tem paracetamol no posto?", "Quanto tempo de espera para pulseira verde?", "Como evitar a dengue?".
- **Correção sugerida:** mais frases administrativas com vocabulário de saúde no dataset; retreinar.

### A4. Perguntas fora do tema que passam pelo limiar

- **Exemplos:** "Quem é o presidente do Brasil?" (0,53), "Como funciona o Bolsa Família?" (0,56).
- **Situação:** o LLM recusa pela regra 2 do prompt, mas isso custa uma chamada ao LLM e depende do modelo obedecer.
- **Correção sugerida:** ampliar o `threshold_set.jsonl` e avaliar um modelo de embeddings maior (benchmark de embeddings).

---

## 🟡 Prioridade baixa — em aberto

| # | Problema | Onde |
| --- | --- | --- |
| P10 | CORS `allow_origins=["*"]` com `allow_credentials=True` | [main.py](../susana_rag_backend/app/main.py) |
| P11 | URL do backend fixa no frontend (`http://localhost:8000`) | [page.tsx:36](../susana-ui/src/app/page.tsx#L36) |
| P13 | `IntentClassifierPort` declarado mas não implementado; `redis` e `dvc` no requirements sem uso | `ports.py`, `requirements.txt` |
| P15 | 3 páginas sem texto útil (Vacinação de rotina, Antirrábica, Serviços ao Cidadão) | `sources.yaml` |
| P16 | Release notes e PDF descrevem coisas não implementadas (DVC, TTFT, embedding `all-MiniLM-L6-v2`) | veja [08-mlops.md §4](08-mlops.md#4-notas-de-release-vs-código) |
| P17 | `samu_2022.parquet` contém 2015–2026 e 46% das linhas com região "Desconhecida" | veja [09-analise-de-dados.md](09-analise-de-dados.md) |
| P18 | `npm audit`: 5 vulnerabilidades altas, só na ferramenta de lint, sem correção sem downgrade | `susana-ui/package-lock.json` |
| P19 | Duas paletas de azul no frontend | [page.tsx](../susana-ui/src/app/page.tsx) |
| A5 | Cache semântico em memória, não thread-safe e perdido a cada reinício | [retriever.py](../susana_rag_backend/app/rag/retriever.py) |
| A6 | API de dados abertos do DF (CKAN) responde HTTP 404 | `collect_opendata.py` |
