# 10. Problemas conhecidos e riscos

Levantamento inicial em 08/10/2026 (leitura do código, perguntas reais e `pytest`), **atualizado no mesmo dia** depois da primeira rodada de correções.

**Estado dos testes:** `pytest` → **86 passaram, 0 falharam** (antes: 13 passaram, 1 falhou).
**Avaliação do chat:** 49% das perguntas sem problemas ([avaliacoes/2026-10-08-1512.md](avaliacoes/2026-10-08-1512.md)).

O plano de ação para os itens em aberto está em [PROXIMOS-PASSOS.md](PROXIMOS-PASSOS.md).

---

## ✅ Resolvidos em 08/10/2026

Detalhes de cada correção em [registro/2026-10-08-correcoes-guardrail-corpus-limiar-rotas.md](registro/2026-10-08-correcoes-guardrail-corpus-limiar-rotas.md).

| # | Problema | Como foi resolvido |
| --- | --- | --- |
| P1 | O guardrail de ML deixava passar perguntas clínicas (recall 0,40) e **substituía** as regras | Regras e ML agora somam proteção; rótulos do dataset corrigidos; dataset ampliado para 111 frases; gate real (recall ≥ 0,98, precisão admin ≥ 0,95, admin liberadas ≥ 0,80). Versão 4: recall **0,987** |
| P2 | Dados fictícios exibidos como "Fonte Oficial" | Mock retirado do corpus (agora em `data/mock/`, não indexado); `collect_opendata.py` falha em vez de inventar; o índice remove blocos que saíram do corpus |
| P3 | Mensagem de bloqueio do frontend sem encaminhamento | Constante única `BLOCKED_MESSAGE` com UBS e SAMU 192, nas duas rotas |
| P4 | Limiar de relevância 1,2 não filtrava nada | Calibrado por script com a busca de produção: **0,74** no corpus de 1.948 blocos (aceita 100% do tema, recusa 30% de fora) |
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
| A1 | Blocos "SAMU 192" eram conteúdo da Atenção Domiciliar | Fonte trocada para `/samu-192-df` (conteúdo real do SAMU) — integração `develop_gui_sam` |
| A7 | Blocos cortados em 128 tokens | `EMBEDDING_MAX_SEQ_LENGTH=256` (da `develop_gui_sam`) |
| A8 | Corpus sem dados por unidade | `CORPUS/Arquivos/` (182 UBS, UPAs, hospitais, CAPS…) + busca híbrida |
| P13 | `langchain`/`redis` sem uso no requirements | Removidos (da `develop_gui_sam`) |
| P7 (parcial) | Fonte aparecia só como texto | Citações estruturadas exibidas como links |
| — | Emergência recebia a recusa clínica genérica | `emergency.py`: SAMU 192 / CVV 188, status `emergency` (RNF06, da branch `docs`) |
| — | "Quais UBS em Samambaia?" só podia trazer 3 trechos | Diretório de unidades por tipo + região (ideia da `develop_sam`) |
| — | Sem como saber se o LLM/corpus estavam prontos | `/health/dependencies` (da `develop_sam`) |
| A2 (parcial) | Sem medida de fidelidade | `run_eval --grounding` (revisor da `develop_gui`); regra no prompt contra links; aviso `generated_link` |

---

## 🔴 Prioridade alta — em aberto

### A1b. Divisão das páginas em blocos

- O caso grave (SAMU) foi resolvido trocando a URL, mas o raspador continua escolhendo "a área com mais texto" da página e dividindo por tamanho, não por subtítulo. Páginas com listas longas (telefones da Atenção Domiciliar) viram blocos sem contexto.
- **Plano:** dividir por `h2`/`h3` e usar o subtítulo no cabeçalho do bloco.

### A2. O LLM acrescenta informação que não está nos trechos

- **Exemplo:** para "Quais serviços a UBS oferece?", o `llama3.1:8b` citou "exames laboratoriais e radiológicos", que não aparecem no trecho usado. Para o SAMU, escreveu "(61) 192".
- **Correção sugerida:** uma checagem automática de fidelidade (números e termos da resposta precisam existir nos trechos), testar outros modelos com o benchmark e reforçar o prompt. O gerador de perguntas de teste vai ajudar a medir isso.

### A3. Guardrail bloqueia perguntas não clínicas que ele nunca viu

- **Evidência:** na [1ª avaliação](avaliacoes/2026-10-08-1512.md), 29 de 72 perguntas não clínicas foram bloqueadas, 27 pelo ML ("Me conta uma piada", "Como a Atenção Domiciliar pode me ajudar?").
- **Causa:** para textos diferentes do treino, o modelo devolve p ≈ 0,5, acima do limiar 0,40. A validação cruzada estimava só 17% de bloqueio indevido porque testava com frases parecidas com as do treino.
- **Plano:** passo 1 de [PROXIMOS-PASSOS.md](PROXIMOS-PASSOS.md). O problema foi movido para prioridade **alta**, por afetar quase metade das perguntas legítimas.

---

### A9. Respostas mais lentas com o corpus integrado

- **Evidência:** mediana das respostas com LLM subiu de 10,6 s para 14,7 s; 3 respostas caíram no fallback por timeout de 12 s (o LLM recebe trechos maiores: tabelas, listas de telefones).
- **Feito:** `LLM_TIMEOUT_S` 12 → 30. **Falta:** reduzir o tamanho dos trechos enviados (ex.: cortar blocos de tabela), medir tempo até o 1º token, avaliar modelo menor.

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
- **Correção sugerida:** checar `res.ok`; manter um buffer da última linha incompleta; desabilitar o envio durante a resposta; `scrollIntoView`

### A10. Ranking por palavras ainda escolhe trechos piores em alguns casos

- **Exemplos:** "Preciso de receita para retirar insulina na farmácia de alto custo?" traz o JSON das UBS em 1º e não traz o CEAF; "Onde tomo a segunda dose da vacina de HPV?" traz o FAQ do Meu SUS Digital em 1º.
- **Plano:** calibrar quando a pergunta é "específica" (hoje: unidade numerada ou termo em ≤ 3% dos blocos), testar fusão por pontuação (RRF) e aumentar os casos do `check` de recuperação.

### A11. Medicamentos da REME com concentração na resposta

- **Exemplo:** "A farmácia da UBS tem dipirona?" → "…dipirona solução oral 500 mg/mL… disponível na UBS". É informação administrativa (o que a rede oferece), mas o avaliador marca `CONTEUDO_CLINICO`, e o LLM pode transformar isso em orientação de uso.
- **Plano:** decidir em equipe se a resposta deve citar só o nome e o local de retirada; ajustar o prompt.

### A12. Citações com título "técnico" e CSVs sem URL

- Os títulos vêm do cabeçalho do bloco ("[CSV] Unidade Básica de Saúde (Unidade_Básica_de_Saúde.csv, registro 12)"); os 414 blocos de CSV não têm URL de origem.
- **Plano:** confirmar a origem com o Sam; gerar título amigável para o cidadão.

### A4. Perguntas fora do tema que passam pelo limiar

- **Exemplos:** "Quem é o presidente do Brasil?", "Como funciona o Bolsa Família?".
- **Situação:** com o corpus de 1.948 blocos, o limiar calibrado (0,74) recusa 30% das perguntas fora do tema antes do LLM (eram 55% com 52 blocos). O restante é recusado pelo LLM (regra 2 do prompt), mas isso custa uma chamada ao LLM e depende do modelo obedecer.
- **Correção sugerida:** ampliar o `threshold_set.jsonl` e avaliar um modelo de embeddings maior (benchmark de embeddings).

---

### A13. Qualidade dos dados de origem

- **Carta de Serviços:** a EDA juntou páginas 14–23 numa seção só (Centros Especializados + CAPS + SAMU + UPAs + Hospitais); os rótulos foram corrigidos, mas os trechos continuam misturando serviços. Ideal: reextrair por página/título.
- **CSVs de unidades:** há caracteres corrompidos em alguns endereços (ex.: "QUADRA 302 CONJUNTO 5 N�" na UBS 07 de Samambaia).
- **Plano:** reextrair a Carta e revisar a codificação dos CSVs com quem os exportou.

---

## 🟡 Prioridade baixa — em aberto

| # | Problema | Onde |
| --- | --- | --- |
| P10 | CORS `allow_origins=["*"]` com `allow_credentials=True` | [main.py](../susana_rag_backend/app/main.py) |
| P11 | URL do backend fixa no frontend (`http://localhost:8000`) | [page.tsx:36](../susana-ui/src/app/page.tsx#L36) |
| P13 | `IntentClassifierPort` declarado mas não implementado; `dvc` no requirements sem uso | `ports.py`, `requirements.txt` |
| P15 | 3 páginas sem texto útil (Vacinação de rotina, Antirrábica, Serviços ao Cidadão) | `sources.yaml` |
| P16 | Release notes e PDF descrevem coisas não implementadas (DVC, TTFT, embedding `all-MiniLM-L6-v2`) | veja [08-mlops.md §4](08-mlops.md#4-notas-de-release-vs-código) |
| P17 | `samu_2022.parquet` contém 2015–2026 e 46% das linhas com região "Desconhecida" | veja [09-analise-de-dados.md](09-analise-de-dados.md) |
| P18 | `npm audit`: 5 vulnerabilidades altas, só na ferramenta de lint, sem correção sem downgrade | `susana-ui/package-lock.json` |
| P19 | Duas paletas de azul no frontend | [page.tsx](../susana-ui/src/app/page.tsx) |
| A5 | Cache semântico em memória, não thread-safe e perdido a cada reinício | [retriever.py](../susana_rag_backend/app/rag/retriever.py) |
| A6 | API de dados abertos do DF (CKAN) responde HTTP 404 | `collect_opendata.py` |
