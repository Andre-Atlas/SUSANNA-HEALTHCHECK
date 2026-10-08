# 14. Rastreabilidade dos requisitos

Situação da `develop_gui2` em 08/10/2026 frente aos requisitos da equipe ([projeto/requisitos-susana.md](projeto/requisitos-susana.md), vindo da branch `docs`).

Legenda: ✅ atende · 🟡 parcial · ❌ não atende

## Requisitos funcionais

| ID | Requisito | Situação | Como / onde | Evidência | Lacuna |
| --- | --- | --- | --- | --- | --- |
| RF01 | Entrada em linguagem natural | ✅ | `/api/chat/stream`, 1–2000 caracteres | `TestInputValidation`; categorias `variacao` e `persona` | — |
| RF02 | Recuperação na base oficial | ✅ | Busca híbrida em 1.979 blocos + diretório de 340 unidades | `test_retriever.py`, `TestUnitDirectoryLookup`, `benchmark_corpus` (Recall@3 = 1,0) | — |
| RF03 | Resposta só com o contexto recuperado | 🟡 | Prompt (regra 1); trechos com instruções são descartados | `--grounding` na avaliação | O LLM ainda acrescenta detalhes (A2); não há revisão em tempo real |
| RF04 | Escopo SUS-DF (unidades, vacinação, medicamentos, consultas, território) | ✅ | Corpus: páginas da SES-DF, diretórios de unidades, REME, Carta de Serviços, FAQ | Categorias `corpus`, `curado` | — |
| RF05 | Declarar ausência de informação | ✅ | Limiar 0,74 → "Não encontrei…" sem LLM; regra 2 do prompt; `status: no_evidence` | `TestStatusAndHealth`, categoria `fora_do_tema` | — |
| RF06 | Resposta parcial controlada | ❌ | — | — | Não há instrução nem verificação para responder só a parte sustentada |
| RF07 | Pedir esclarecimento em perguntas ambíguas | ❌ | — | Verificação `NAO_PEDIU_ESCLARECIMENTO` (categoria `curado` C) | Comportamento não implementado |
| RF08 | Tratar perguntas fora do escopo clínico | ✅ | Guardrail híbrido (regras + ML) + `status: out_of_scope` | `TestGuardrails`, `TestGuardrailRules`, categoria `clinica` (100%) | O guardrail bloqueia demais (A3) |
| RF09 | Vedação de diagnóstico/prescrição | 🟡 | Guardrail + regra 3 do prompt | `CONTEUDO_CLINICO` na avaliação | Respostas sobre a REME citam concentração (A11) |
| RF10 | Fontes utilizadas junto à resposta | ✅ | `citations` (título + URL) no `done`; links na tela | `TestPickSource`, `TestBuildCitations`, `test_pipeline_citations.py` | CSVs sem URL de origem (A12) |
| RF11 | "Ver mais" — consultar o trecho/fonte | 🟡 | Link para a página oficial | — | A tela não mostra o trecho em si |
| RF12 | Usar contexto informado (região, endereço) | 🟡 | Região na própria pergunta → diretório de unidades | `TestUnitDirectoryLookup`, categoria `persona` | Sem memória de conversa (a região precisa estar na mesma mensagem) |

## Requisitos não funcionais

| ID | Requisito | Situação | Como / onde | Lacuna |
| --- | --- | --- | --- | --- |
| RNF01 | Fidelidade à fonte | 🟡 | Prompt + filtro de injeção + avaliação `--grounding` | Revisão de fidelidade ainda é só offline |
| RNF02 | Rastreabilidade interna | ✅ | MLflow: desfecho, fonte, distância, motivo do bloqueio por pergunta; citações com `id` do bloco | — |
| RNF03 | Transparência (ver evidências) | 🟡 | Citações com link | Mostrar o trecho (RF11) |
| RNF04 | Conflito/atualização entre fontes | ❌ | — | Sem data de verificação por fonte nem política de prioridade |
| RNF05 | Privacidade (LGPD) | 🟡 | MLflow grava só hash da pergunta (`MLFLOW_LOG_QUERY_TEXT=false`); tudo local | CORS aberto (P10); sem política de retenção escrita |
| RNF06 | Segurança em emergências | ✅ | `app/rag/emergency.py`: SAMU 192 / CVV 188 antes do guardrail; selo na tela | Lista de sinais é por regras; avaliar com mais casos reais |
| RNF07 | Robustez a erros de digitação e informalidade | 🟡 | Busca por significado + glossário de siglas; guardrail com n-gramas de caracteres | Categoria `variacao` ainda com ~30% sem problemas, principalmente por causa do guardrail |
| RNF08 | Equidade entre regiões | 🟡 | O diretório cobre as 43 regiões dos CSVs | Não medido por região |
| RNF09 | Usabilidade / linguagem simples | 🟡 | Prompt (≤ 120 palavras, cordial) | Não avaliado com usuários; títulos de citação técnicos |
| RNF10 | Desempenho | 🟡 | Mediana ~15 s por resposta com LLM | Acima do confortável; meta p95 ≤ 15 s do plano de produção |
| RNF11 | Disponibilidade | ❌ | Um processo local | Sem supervisão, reinício automático ou monitoramento |
| RNF12 | Manutenibilidade / atualidade do corpus | 🟡 | Scripts de coleta e importação; índice sincroniza sozinho; limiar recalibrável | Sem atualização periódica automática nem data de verificação |
| RNF13 | Avaliação contínua | 🟡 | `pytest` (86), `run_eval` (9 categorias, 15 verificações), `calibrate_threshold`, `benchmark_corpus`, MLflow | Falta CI rodando a cada mudança |
| RNF14 | Custo / código aberto | ✅ | Ollama, ChromaDB, sentence-transformers, FastAPI, Next.js | — |

## Resumo

| | ✅ | 🟡 | ❌ |
| --- | --- | --- | --- |
| Funcionais (12) | 6 | 4 | 2 (RF06, RF07) |
| Não funcionais (14) | 3 | 9 | 2 (RNF04, RNF11) |

Os itens ❌ e 🟡 viraram passos em [PROXIMOS-PASSOS.md](PROXIMOS-PASSOS.md).
