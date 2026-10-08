# 08/10/2026 — Integração da `develop_gui_sam` na `develop_gui2`

**Objetivo:** trazer para a `develop_gui2` o que a análise ([12-comparacao-develop_gui_sam.md](../12-comparacao-develop_gui_sam.md)) apontou como bom na branch do Sam. **Somente a `develop_gui2` foi alterada.**

**Resultado:**

- testes de 38 para **68**, todos passando;
- corpus de 52 para **1.948 blocos**;
- perguntas por unidade ("UBS 2 de Planaltina"): de 0/4 para **4/4**;
- conjunto de 16 perguntas de recuperação: **16/16** (a busca só vetorial acertava 10/16).

## Passo a passo

| # | O que foi feito | Arquivos |
| --- | --- | --- |
| 1 | Copiados da branch do Sam (`git checkout origin/develop_gui_sam -- <caminho>`, estando na `develop_gui2`): corpus curado, plano de produção, benchmark de corpus, +7 casos do benchmark de LLM, 3 arquivos de teste | `CORPUS/Arquivos/`, `docs/production-readiness-plan.md`, `ml/retrieval/benchmark_corpus.py`, `ml/llm/benchmark_dataset.json`, `tests/test_corpus_ingestion.py`, `tests/test_retriever.py`, `tests/test_pipeline_citations.py` |
| 2 | Matéria do Jornal de Brasília tirada da indexação; log de exportação renomeado para `.log` | `CORPUS/nao_indexado/`, `CORPUS/Arquivos/relatorio_exportacao.log` |
| 3 | Carregador multiformato do Sam + cabeçalho legível para CSV ("Unidade Básica de Saúde (arquivo.csv, registro N)") | `app/rag/corpus.py`, `app/ports.py` (campo `url`) |
| 4 | Pastas do corpus em `Settings.corpus_roots` (`data/corpus/` + `CORPUS/Arquivos/`); scripts de calibração, geração e avaliação usam a mesma lista | `app/config.py`, `app/main.py`, `ml/eval/*.py`, `ml/retrieval/calibrate_threshold.py` |
| 5 | `EMBEDDING_MAX_SEQ_LENGTH` do Sam. Comparado 128 × 256 × 512 no `benchmark_corpus`: Recall@1 0,943 / 0,946 / 0,946; Recall@3 1,0 nos três → **256** | `app/rag/embeddings.py`, `app/config.py` |
| 6 | Busca híbrida do Sam integrada; a busca textual dele diferenciava maiúsculas ("dipirona" não era achada) | `app/rag/retriever.py` |
| 7 | Medição revelou que a ordenação "palavras primeiro" do Sam **piorava perguntas gerais** (13/16): "Quando devo ligar para o 192?" trazia "Saúde Mental". Testadas 3 alternativas: modo por maiúsculas (13/16), peso por raridade/IDF (13/16), **rankings intercalados + IDF (16/16)** ✅ | `app/rag/retriever.py` |
| 8 | **Descoberta:** os 7 blocos "SAMU 192" eram conteúdo da Atenção Domiciliar (a página `/samu` tem pouco texto próprio e o raspador pegou um menu). Fonte trocada para `/samu-192-df` (5 blocos reais, "telefone 192") | `ml/corpus/sources.yaml`, `data/corpus/sesdf_public.txt` |
| 9 | `is_relevant` usa a menor distância entre os 3 trechos (o 1º pode vir do ranking por palavras) | `app/rag/retriever.py` |
| 10 | Calibração refeita **com a busca de produção** (índice temporário) e 15 perguntas novas (unidades, FAQ, medicamentos) → limiar **0,74** (aceita 100% do tema, recusa 30% de fora) | `ml/retrieval/calibrate_threshold.py`, `ml/retrieval/threshold_set.jsonl`, `app/config.py` |
| 11 | Citações estruturadas do Sam levadas ao streaming, ao cache e à rota `/api/chat` | `app/rag/pipeline.py`, `app/main.py` |
| 12 | **Risco encontrado:** "UBS 1" e "UBS 2" de Candangolândia ficam a 0,025 de distância → o cache devolveria o endereço errado. O cache agora exige os mesmos números | `app/rag/pipeline.py` |
| 13 | Frontend mostra as citações como links | `susana-ui/src/app/page.tsx`, `susana-ui/src/components/Chat/MessageBubble.tsx` |
| 14 | `requirements.txt`: sai `langchain*` e `redis`, entra `pypdf` | `requirements.txt` |
| 15 | 5 testes novos (unidade por número, cache × números, citações) | `tests/test_rag.py` |
| 16 | Avaliação `--seed 0` no banco v1: 49% → 37% sem problemas. Causas: lentidão (mediana 10,6 → 14,7 s) e 3 timeouts de 12 s → `LLM_TIMEOUT_S` 12 → 30 | `app/config.py`, `.env.example` |
| 17 | Banco v1 guardado (`question_bank_v1.jsonl`); gerador ganhou `--blocks-per-source` e gerou o banco v2 (390 perguntas, 133 blocos de todas as origens); avaliador ganhou `--bank` | `ml/eval/generate_questions.py`, `ml/eval/run_eval.py` |
| 18 | Avaliação no banco v2 (112 perguntas): **52% sem problemas, 0 fallback** | [avaliacoes/2026-10-08-1653.md](../avaliacoes/2026-10-08-1653.md) |

## Leitura dos números da avaliação

- No banco v1, ignorando lentidão: 52% → 49%. A diferença de 2 perguntas está dentro da variação do LLM, e 3 dos "erros" novos eram falsos alarmes (o banco v1 esperava a página `/samu`, que tinha o texto errado).
- O ganho principal (perguntas por unidade, FAQ, medicamentos) **não aparece no banco v1**, que foi gerado só do corpus antigo. Por isso existe o banco v2.
- O problema dominante continua sendo o **guardrail bloqueando perguntas administrativas** (passo 1 de [PROXIMOS-PASSOS.md](../PROXIMOS-PASSOS.md)): 26 casos no banco v2.

**Próximo registro:** [2026-10-08-analise-todas-as-branches.md](2026-10-08-analise-todas-as-branches.md)
