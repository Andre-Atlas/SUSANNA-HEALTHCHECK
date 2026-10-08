# 13. Todas as branches do repositório — o que cada uma tem e o que foi aproveitado

Análise feita em 08/10/2026 sobre `github.com/Andre-Atlas/SUSANNA-HEALTHCHECK`. **Regra seguida: só a `develop_gui2` foi alterada.** As outras branches foram apenas lidas (`git show` e cópias temporárias desanexadas, removidas no final).

## Visão geral

```text
de2e769 main ("Initial commit", 10/09)
 ├── analyses_ingrid  (4 commits)   dados da REME/farmácias em Markdown + JSON
 ├── develop_gui      (451 commits) versão anterior: chatbot sobre DESINFORMAÇÃO em saúde (outro escopo)
 ├── develop_sam      (24 commits)  backend FastAPI + PostgreSQL/pgvector + protótipo React integrado
 ├── docs             (48 commits)  escopo, requisitos, personas, EDA da Carta de Serviços, CORPUS
 └── 7a260f0 develop_andre ("integrar frontend streaming, RAG pipeline refatorado e MLflow guardrails")
       ├── develop_gui_sam (1 commit)  corpus curado + busca híbrida → integrada (doc 12)
       └── develop_gui2    (esta)      guardrail híbrido, avaliação, documentação, integrações
```

| Branch | Último commit | Situação em relação à `develop_gui2` |
| --- | --- | --- |
| `main` | 10/09 | Nada novo |
| `develop_andre` | 06/10 | Nada novo: é a base da `develop_gui2` |
| `develop_gui_sam` | 08/10 | Integrada antes ([doc 12](12-comparacao-develop_gui_sam.md)) |
| `analyses_ingrid` | 06/10 | Nada novo a trazer: a REME e as farmácias já vieram em JSON pela `develop_gui_sam` |
| `develop_gui` | 06/10 | Outro escopo; módulos de política de resposta e revisão de fidelidade **aproveitados** |
| `develop_sam` | 06/10 | Outra arquitetura; ideias e o conjunto de avaliação **aproveitados** |
| `docs` | 08/10 | Documentos do projeto e Carta de Serviços **aproveitados** |

---

## `develop_gui` — chatbot educativo sobre desinformação

Projeto anterior com outro foco: verificar boatos de saúde buscando páginas do gov.br na internet (`govbr_search.py`), base SQLite FTS5, servidor HTTP próprio (`server.py`), túnel para demonstração (`internet_demo.py`) e o modelo `qwen2.5:7b`.

**Ponto forte:** um controle de fidelidade maduro. A resposta é gerada em JSON (parágrafos + IDs de fonte) e passa por regras determinísticas e por um segundo LLM revisor.

| O quê | Aproveitado? | Onde ficou |
| --- | --- | --- |
| `source_instruction_errors` (trecho que tenta dar ordens ao modelo) | ✅ adaptado | `app/rag/answer_policy.py` → `has_injected_instructions`; o pipeline descarta esses trechos |
| `reference_errors` → `generated_link` (o LLM não escreve URLs) | ✅ adaptado | `answer_policy.generated_links`; aviso `warnings: ["generated_link"]` no `done`; regra 6 no prompt; verificação `LINK_GERADO` na avaliação |
| `verify_grounding` + `REVIEW_INSTRUCTION` (LLM revisor) | ✅ adaptado **para a avaliação** | `ml/eval/grounding_judge.py`; `run_eval --grounding` → `GROUNDING_REPROVADO` |
| Geração em JSON estruturado + revisão em tempo real | ❌ não agora | Dobraria o tempo de resposta (o revisor é uma 2ª chamada ao LLM) e não combina com streaming. Fica como opção para a rota `/api/chat` |
| `conversation.py` (perguntas de continuação) | ❌ | A `develop_gui2` não guarda histórico de conversa |
| Busca na internet (gov.br), túnel, fila de concorrência | ❌ | Contrários ao escopo on-premise da Susana |

## `develop_sam` — backend com PostgreSQL/pgvector

Duas pastas: `susana-backend/` (FastAPI em camadas: services, repositories, Alembic, Docker) e `prototipo-integrado/` (backend + React + avaliação de modelos). Usa `llama3.2:3b` + `nomic-embed-text` (768 dimensões).

| O quê | Aproveitado? | Onde ficou |
| --- | --- | --- |
| `StructuredSearchService` (unidades por tipo + região) | ✅ reimplementado **sem PostgreSQL** | `app/rag/unit_directory.py`: lê os 10 CSVs de unidades de `CORPUS/Arquivos` (340 unidades, 43 regiões); "Quais UBS existem em Samambaia?" entrega a lista completa (14) como trecho [1] |
| Estados da resposta (`answered`, `out_of_scope`, `no_evidence`, `needs_clarification`, `error`) | ✅ adaptado | Campo `status` no `done` e na rota `/api/chat`: `emergency`, `out_of_scope`, `no_evidence`, `answered`, `fallback` |
| `/api/v1/health/dependencies` | ✅ adaptado | `GET /health/dependencies`: LLM pronto, blocos indexados, unidades no diretório, guardrail carregado, limiar |
| `prototipo-integrado/eval/dataset.json` (40 perguntas escritas à mão, com `required_facts`) | ✅ copiado | `ml/eval/curated_develop_sam.json` → categoria `curado` do banco (35 perguntas; a categoria F, multi-turno, ficou de fora) + verificação `FATO_AUSENTE` |
| `ScopeService` (lista de termos do escopo, aliases de região) | 🟡 ideia | Aliases de região usados no diretório; a lista de termos como filtro de "fora do tema" ficou para avaliar (risco de recusar perguntas válidas sem termo-chave) |
| `needs_clarification` (RF07) | 🟡 só na avaliação | Verificação `NAO_PEDIU_ESCLARECIMENTO`; o comportamento ainda não foi implementado |
| PostgreSQL, Alembic, Docker, camadas de repositório | ❌ | Infraestrutura bem maior que o ChromaDB atual; sem ganho imediato para o piloto |
| `prototipo_react/`, `prototipo_susanna.html` | ❌ | O frontend Next.js da `develop_gui2` já cobre |

## `docs` — documentação do produto

| O quê | Aproveitado? | Onde ficou |
| --- | --- | --- |
| `Requisitos/requisitos-susana.md` (RF01–RF12, RNF01–RNF14) | ✅ copiado | [projeto/requisitos-susana.md](projeto/requisitos-susana.md); status de cada requisito em [14-rastreabilidade-requisitos.md](14-rastreabilidade-requisitos.md) |
| `Escopo/escopo.md`, `produto-negocio.md` | ✅ copiados | [projeto/escopo.md](projeto/escopo.md), [projeto/produto-negocio.md](projeto/produto-negocio.md) |
| Personas (Raimunda, Camila, Felipe) | ✅ copiadas (links do índice corrigidos) | [projeto/personas/](projeto/personas/personas.md) + categoria `persona` no banco de perguntas (10) |
| **RNF06 — emergência** | ✅ implementado | `app/rag/emergency.py`: SAMU 192 / CVV 188 antes do guardrail; status `emergency`; selo "Possível emergência — ligue 192" na tela; categoria `emergencia` no banco (6) |
| EDA da **Carta de Serviços ao Cidadão 2026** (SES-DF) | ✅ como corpus | `ml/corpus/import_carta_servicos.py` limpa a extração (HTML/Markdown), corrige 2 rótulos de seção e grava `CORPUS/Arquivos/carta_servicos_sesdf_2026.json` (13 seções, 28 blocos); a extração original fica em `CORPUS/nao_indexado/` |
| `CORPUS/` | — | Os mesmos arquivos da `develop_gui_sam`, já integrados |
| PDFs de Scrum, pesquisa, imagens do Trello, escopo de "extensão de navegador" | ❌ | Material de gestão/pesquisa, sem efeito no sistema |

## `analyses_ingrid`

REME 2025, Farmácia Escola, CEAF e Farmácias Vivas em Markdown e JSON, mais o conversor `converter_md_json.py`. Os JSONs são os mesmos que já estão em `CORPUS/Arquivos/` (vindos da `develop_gui_sam`). Nada novo a trazer. Vale registrar que **a origem da REME no corpus é o trabalho da Ingrid**.

---

## Ajustes de qualidade feitos ao integrar

- **Carta de Serviços:** a EDA associou a seção da p. 7 a "UPAs", mas o texto é do e-Protocolo/Ouvidoria; a seção da p. 14 vai até a p. 23 e cobre Centros Especializados, CAPS, SAMU, UPAs e Hospitais. O importador corrige os rótulos e registra o intervalo de páginas.
- **Contexto em todos os trechos:** em JSONs com seções longas, só o 1º trecho levava o nome da seção. Agora todos levam, e o nome aparece também na **citação** ("Carta de Serviços… — Atendimento em UBS").
- **Diretório:** o filtro "farmácia/vacina" só inclui unidades que declaram "SIM"; "UBS 2 de Planaltina" retorna só a unidade 2; a lista é compacta para não inflar o prompt.

Passo a passo completo: [registro/2026-10-08-analise-todas-as-branches.md](registro/2026-10-08-analise-todas-as-branches.md).
