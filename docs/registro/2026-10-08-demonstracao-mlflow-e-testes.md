# 08/10/2026 — Demonstração: MLflow e testes no Terminal

**Objetivo:** abrir o MLflow e os testes de forma visível, para apresentar à equipe.

## Passo a passo

| Passo | O que foi feito |
| --- | --- |
| 1 | Interface do MLflow iniciada em **http://localhost:5001** (a porta 5000 é usada pelo AirPlay do macOS):<br>`cd susana_rag_backend && .venv/bin/mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5001` |
| 2 | 8 perguntas enviadas ao chat para gerar execuções de todos os desfechos no experimento `susana-rag`: respondida, bloqueada (`regex:prescricao`, `regex:dosagem`), sem fonte (bolo de chocolate) e cache |
| 3 | `python -m ml.retrieval.benchmark_embeddings`: **primeira execução** do benchmark de embeddings |
| 4 | `python -m ml.retrieval.calibrate_threshold`: nova calibração (confirmou 0,70) |
| 5 | Criado `susana_rag_backend/rodar_testes.command`: abre o Terminal e roda `pytest -v` com cores. Funciona com duplo clique no Finder ou com `open rodar_testes.command`. Foi preciso porque o macOS bloqueou o controle do Terminal por AppleScript (erro -1712, permissão de automação) |

## O que mostrar no MLflow

| Experimento | Execuções | O que mostra |
| --- | --- | --- |
| `susana-guardrails-train` | 4 | Evolução do guardrail: compare as métricas `cv_hybrid_recall_clinical` e `cv_hybrid_admin_allowed` e o parâmetro `gate_passed` (v2 reprovada; v3 e v4 aprovadas) |
| Aba **Models** → `susana-guardrail` | v1–v4 | Registro de modelos com o alias `@champion` na versão 4 |
| `susana-rag` | 184 | Uma execução por pergunta: `outcome`, `guardrail_reason`, `latency_s`, `top_distance`, `source`, só o hash da pergunta (LGPD) |
| `susana-threshold-calibration` | 4 | Limiar sugerido e % aceitas/recusadas |
| `susana-embeddings-benchmark` | 2 | Comparação entre dois modelos de embedding |

Dica para a apresentação: em `susana-rag`, selecione várias execuções → **Compare**, ou agrupe pela coluna `outcome`.

## Achado do benchmark de embeddings

| Modelo | Hit rate top-3 |
| --- | --- |
| `all-MiniLM-L6-v2` (inglês) | **1,00** |
| `paraphrase-multilingual-MiniLM-L12-v2` (atual, multilíngue) | 0,67 |

O resultado é surpreendente, mas **ainda não justifica trocar o modelo**. O conjunto de avaliação tem só 6 perguntas, o critério é frouxo (acertar a *tag* do bloco) e o benchmark lê só o `sesdf_public.txt`. Isso virou um item em [PROXIMOS-PASSOS.md](../PROXIMOS-PASSOS.md) (passo 2): ampliar o `eval_set.jsonl` usando as perguntas `corpus` do banco de avaliação (que têm a URL esperada) e repetir a comparação.
