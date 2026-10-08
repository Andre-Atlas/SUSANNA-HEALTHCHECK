# 08/10/2026 — Análise de todas as branches e integração das ideias

**Pedido:** "analise todas as branchs do projeto e use para melhorar a branch develop_gui2", com a regra de **não alterar as outras branches**. Análise completa: [13-todas-as-branches.md](../13-todas-as-branches.md).

**Garantia sobre as outras branches:** foram só lidas (`git show origin/<branch>:<arquivo>` e uma cópia temporária desanexada da `develop_sam`, removida no final). Os commits delas continuam os mesmos (ex.: `develop_sam` em `4f29c1d`, `develop_gui_sam` em `a267606`).

## Passo a passo

| # | O que foi feito | Origem | Arquivos na `develop_gui2` |
| --- | --- | --- | --- |
| 1 | `git fetch --all`; contagem de commits exclusivos de cada branch | — | — |
| 2 | Leitura da `develop_gui` (outro escopo: desinformação), da `develop_sam` (PostgreSQL/pgvector + protótipo), da `docs` e da `analyses_ingrid` | — | — |
| 3 | Requisitos, escopo, produto/negócio e personas copiados (links do índice de personas corrigidos) | `docs` | `docs/projeto/` |
| 4 | Carta de Serviços 2026: extração da EDA guardada como origem; script de importação que limpa HTML/Markdown, corrige 2 rótulos (p. 7 e p. 14–23) e grava intervalo de páginas → 28 blocos | `docs` | `ml/corpus/import_carta_servicos.py`, `CORPUS/Arquivos/carta_servicos_sesdf_2026.json`, `CORPUS/nao_indexado/carta_servicos_2026_secoes.jsonl` |
| 5 | Carregador JSON: contexto da seção em **todos** os trechos e no cabeçalho (citação mostra o serviço) | ajuste | `app/rag/corpus.py` |
| 6 | **Diretório de unidades** (tipo + região → lista completa como trecho [1]); filtro "SIM" para farmácia/vacina; unidade numerada sozinha; lista compacta | `develop_sam` (StructuredSearchService) | `app/rag/unit_directory.py` |
| 7 | **Emergência** (RNF06): sinal grave + "agora/comigo" → SAMU 192; suicídio → CVV 188; roda antes do guardrail. 12/12 casos de teste manuais | `docs` (requisitos) + `develop_sam` (estados) | `app/rag/emergency.py` |
| 8 | **Filtro de instruções** nos trechos (fail-closed) e **detector de links** escritos pelo LLM (inclui "clicando aqui", visto numa resposta real) | `develop_gui` (answer_policy) | `app/rag/answer_policy.py` |
| 9 | Pipeline: emergência → guardrail → cache → busca + diretório + filtro → LLM; **`status`** no `done` (emergency/out_of_scope/no_evidence/answered/fallback); aviso `generated_link` | `develop_sam` + `develop_gui` | `app/rag/pipeline.py` |
| 10 | `GET /health/dependencies`; `status` na rota `/api/chat` | `develop_sam` | `app/main.py` |
| 11 | Prompt: regra 6 (sem links/"clique aqui"), regra 7 (listas de unidades), exceção de tamanho para listas | `develop_gui` + ajuste | `app/llm/prompts.py` |
| 12 | Frontend: selo "Possível emergência — ligue 192" | ajuste | `susana-ui/src/…` |
| 13 | 40 perguntas curadas copiadas (35 usadas; F = multi-turno, não suportado) | `develop_sam` (prototipo-integrado/eval) | `ml/eval/curated_develop_sam.json` |
| 14 | Gerador: categorias `curado`, `persona` (10), `emergencia` (6); `--refresh-fixed` (sem Ollama). Banco: 441 perguntas | `develop_sam` + `docs` | `ml/eval/generate_questions.py`, `ml/eval/question_bank.jsonl` |
| 15 | Avaliador: `EMERGENCIA_NAO_DETECTADA`, `EMERGENCIA_INDEVIDA`, `LINK_GERADO`, `FATO_AUSENTE`, `NAO_PEDIU_ESCLARECIMENTO` | — | `ml/eval/run_eval.py` |
| 16 | **Revisor de fidelidade** opcional (`--grounding`), com modelo revisor diferente do gerador (`qwen2.5:7b`) | `develop_gui` (verify_grounding) | `ml/eval/grounding_judge.py` |
| 17 | 18 testes novos (emergência, diretório, política, status, health) + 3 ajustados ao comportamento novo | — | `tests/test_rag.py` |
| 18 | Recalibração: limiar segue **0,74** (aceita 100% do tema, recusa 35% de fora; antes 30%) | — | — |
| 19 | Documentação: docs 13 e 14 (novos), 01–07, 10, 11, README, PRÓXIMOS-PASSOS | — | `docs/` |

## Verificação

```text
pytest: 86 passed (antes desta rodada: 68)
/health/dependencies: llm ready, 1.979 blocos, 340 unidades, guardrail ML carregado
```

Respostas reais conferidas:

- "Qual o telefone do SAMU?" → "O telefone do SAMU é 192. [2]", citando a Carta de Serviços (seção SAMU-DF 192);
- "Tem UPA no Gama?" → cita o diretório;
- "minha mãe desmaiou agora" → `status: emergency`.

## Não trazido (e por quê)

- Revisão de fidelidade **em tempo real** (`develop_gui`): dobraria o tempo de resposta e não combina com streaming. Ficou na avaliação.
- PostgreSQL/pgvector/Alembic/Docker (`develop_sam`): infraestrutura bem maior sem ganho imediato para o piloto.
- Busca na internet e túnel público (`develop_gui`): contrários ao escopo on-premise.
- Histórico de conversa (`develop_sam`/`develop_gui`): mudança maior de arquitetura; fica como próximo passo (RF12).

## Resultado da avaliação

Rodada com o banco atualizado (`--seed 0 --limit 20`) em andamento no momento deste registro; o resultado será acrescentado em [avaliacoes/](../avaliacoes/) e neste arquivo.

**Próximo passo:** passo 1 de [PROXIMOS-PASSOS.md](../PROXIMOS-PASSOS.md) (bloqueio indevido do guardrail) e passo 2c (RF07, RF06, RF11).
