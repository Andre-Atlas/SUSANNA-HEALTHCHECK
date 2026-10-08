# 08/10/2026 — Análise da branch `develop_gui_sam`

**Objetivo:** analisar a branch `develop_gui_sam` (o pedido citou "branch_gui_sam"; no remoto o nome é `origin/develop_gui_sam`), comparar com a `develop_gui2` e identificar o que aproveitar. **Nenhum código foi integrado nesta rodada.**

Resultado completo: [12-comparacao-develop_gui_sam.md](../12-comparacao-develop_gui_sam.md).

## Passo a passo

| Passo | O que foi feito | Resultado |
| --- | --- | --- |
| 1 | `git fetch --all` e comparação de históricos | Base comum `7a260f0`; a do Sam tem 1 commit (`a267606`), a `develop_gui2` tem 37 |
| 2 | Leitura do diff de código (`app/`, `requirements.txt`, `.env.example`) | Carregador multiformato, busca híbrida, `max_seq_length`, citações estruturadas, limpeza de dependências |
| 3 | Leitura do `docs/production-readiness-plan.md` do Sam | Plano de 309 linhas com gates de produto e fases F0–F8; recomenda deixar as bases de análise fora do MVP |
| 4 | `git worktree add` da branch do Sam em pasta temporária | Permitiu inspecionar e rodar sem tocar na `develop_gui2` |
| 5 | Inventário de `CORPUS/Arquivos/` | 28 arquivos (14 CSV de unidades sem URL, 13 JSON com URL oficial, 1 matéria de jornal) |
| 6 | `pytest` dos 3 arquivos novos do Sam (com o venv da `develop_gui2` + `pypdf`) | **25 passed in 2.23s** |
| 7 | Contagem de blocos com o carregador dele | `CORPUS/Arquivos`: 1.910 blocos (1.232 da REME); `CORPUS/` inteiro: 105.859 blocos |
| 8 | Teste comparativo de busca em 1.962 blocos | Perguntas por unidade numerada: só vetor 0/4, híbrida **4/4**; "losartana" falhou nas duas |
| 9 | Medição do truncamento dos embeddings na `develop_gui2` | `max_seq_length` = 128; **41 de 52 blocos cortados** (mediana 188 tokens) |
| 10 | Documentação | Criado o doc 12; atualizados `README.md`, `PROXIMOS-PASSOS.md` (novo passo 2), `06-corpus-e-indexacao.md` e `10-problemas-conhecidos.md` (A7, A8) |

Dependência instalada no venv: `pypdf`, necessária para rodar os testes do Sam. Ela ainda não está no `requirements.txt` da `develop_gui2`; entra no passo 2.

## Decisões

- **Trazer:** `CORPUS/Arquivos/`, carregador multiformato, busca híbrida, `EMBEDDING_MAX_SEQ_LENGTH`, os 25 testes, limpeza de dependências e o plano de produção.
- **Adaptar:** citações estruturadas (levar para o streaming), `benchmark_corpus.py` (unificar com o `run_eval`), REME (avaliar o efeito na busca), CSVs sem URL (descobrir a origem).
- **Não trazer sem decisão da equipe:** indexação das bases de análise (~104 mil blocos), a mudança das pastas de dados para `CORPUS/`, a matéria de jornal como "Fonte Oficial", e o guardrail/pipeline antigos da branch dele.
- Integração **à mão, por partes**, porque as duas branches alteraram os mesmos arquivos centrais a partir do mesmo ponto.

**Próximo passo:** passo 2 de [PROXIMOS-PASSOS.md](../PROXIMOS-PASSOS.md), depois de conversar com o Sam sobre as 4 perguntas do fim do doc 12.
