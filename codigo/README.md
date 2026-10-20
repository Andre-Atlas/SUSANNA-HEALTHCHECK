# Código-Fonte da Aplicação — SUSANA

O código funcional da solução **SUSANA (SUS Digital — Meu SUS Brasília)** está versionado neste mesmo repositório, nas pastas abaixo. Esta página é o mapa entre os entregáveis da Residência e o código.

* **Repositório:** [github.com/Andre-Atlas/SUSANNA-HEALTHCHECK](https://github.com/Andre-Atlas/SUSANNA-HEALTHCHECK)

---

## 📦 Estrutura

| Pasta | Conteúdo |
| :--- | :--- |
| [`susana_rag_backend/`](../susana_rag_backend/) | API FastAPI, pipeline RAG, guardrails, cadastro, agenda, vacinas, unidades, monitoramento e testes |
| [`susana-ui/`](../susana-ui/) | Interface Next.js 16 (App Router) com React 19 e Tailwind CSS v4 |
| [`scripts/`](../scripts/) | Scripts de análise, geração de documentos/notebooks e implantação (`deploy_oci.sh`) |
| [`docs/`](../docs/) | Arquitetura, MLOps, build e execução, guia de implantação na Oracle Cloud |
| [`docker-compose.yml`](../docker-compose.yml), [`Caddyfile`](../Caddyfile) | Orquestração dos contêineres e proxy HTTPS |

### Backend (`susana_rag_backend/app/`)

| Módulo | Responsabilidade |
| :--- | :--- |
| `rag/` | NLU e toponímia do DF, `ChromaRetriever` (busca vetorial, filtro por RA, casamento lexical e reordenação por regras), guardrails clínicos, cache semântico e busca online restrita a domínios oficiais |
| `llm/` | Adaptador do Ollama (Llama 3.1 8B), prompts e contexto de perfil sem dados identificáveis |
| `routers_stream.py` | Chat em streaming NDJSON, incluindo propostas de agenda confirmadas pelo cidadão |
| `citizen/` | Cadastro opcional, login por CPF e senha, sessões persistentes, perfil e exclusão de conta |
| `chat_sessions/` | Histórico de conversas por titular |
| `agenda/` | Eventos, lembretes, interpretação de datas em português e detecção de pedidos de agendamento |
| `vaccines/` | Guia do PNI e cálculo de vacinas pendentes por perfil |
| `units/` | Diretório de 383 unidades de saúde do DF (servidas por `/api/units`), construído a partir do diretório por região e das unidades especializadas, com deduplicação |
| `surveillance/` | Monitoramento epidemiológico com dados oficiais |
| `ingestion/` | Webhook autenticado de ingestão contínua de documentos |

### Frontend (`susana-ui/src/`)

* `app/page.tsx`: casca da aplicação (landing, navegação por abas e assistente).
* `components/Auth/`: cadastro em etapas, login e perfil. `components/Agenda/`: calendário, lembretes e vacinas pendentes. `components/Chat/`: cartão de confirmação de lembretes. `components/UnitsMap/` e `components/Surveillance/`: mapa de unidades e painel epidemiológico.
* `context/`: estado de autenticação, agenda e localização (as coordenadas ficam só no aparelho).

---

## 🧪 Comandos de Execução e Teste

### Execução Automática Unificada (Recomendado)
```bash
# Configura Python .venv, .env, Guardrail, ChromaDB, npm install e sobe Backend (:8000) + Frontend (:3000)
bash setup.sh --start

# Executa os 237 testes do Backend + build de produção do Frontend
bash setup.sh --test
```

### Execução Manual Passo a Passo
```bash
# Backend: ambiente, testes (237) e servidor
cd susana_rag_backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest tests/
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend: compilação de produção e servidor de desenvolvimento
cd ../susana-ui
npm install
npm run build
npm run dev
```

* O LLM precisa do Ollama em execução (`ollama pull llama3.1:8b`). Sem ele, o chat devolve os trechos oficiais recuperados.
* Benchmarks de recuperação e de modelos ficam em `susana_rag_backend/ml/` (ex.: `ml/retrieval/eval_honest_benchmark.py`).
* Detalhes de setup, portas e variáveis de ambiente: [`docs/BUILD_E_EXECUCAO.md`](../docs/BUILD_E_EXECUCAO.md).
* Implantação na Oracle Cloud (Docker Compose + HTTPS): [`docs/GUIA_DEPLOY_ORACLE_CLOUD.md`](../docs/GUIA_DEPLOY_ORACLE_CLOUD.md).
