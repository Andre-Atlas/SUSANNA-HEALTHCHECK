# Código-Fonte da Aplicação — SUSANA

Área estruturada para a esteira e versionamento do código-fonte da solução **SUSANA (Meu SUS Brasília)**.

---

## 📦 Arquitetura dos Módulos

### 1. `backend/` (API FastAPI & Mecanismo de IA)
* **Framework:** FastAPI com suporte assíncrono e execução local em Python 3.11+.
* **Motor RAG Híbrido:** Integração vetorial densa (`paraphrase-multilingual-MiniLM-L12-v2` no **ChromaDB**) e busca léxica esparsa (**BM25 Okapi** com tokenizador em saúde e toponímia do DF).
* **Algoritmo de Fusão:** **RRF (Reciprocal Rank Fusion)** com constante $k=60$ e limiares de relevância semântica.
* **Salvaguardas Clínicas:** Guardrail supervisionado treinado via Scikit-Learn e governado no **MLflow** (`@champion`), complementado por regex emergencial para interceptação de risco em $< 10\text{ ms}$.
* **Validador Anti-Alucinação:** Sanitização pós-geração que bloqueia emissão de receitas médicas e restringe contatos telefônicos estritamente aos canais oficiais (160, 136, 192).
* **Persistência Relacional:** SQLite em modo **WAL (Write-Ahead Logging)** com concorrência thread-safe para gestão de cidadãos e multi-sessões.

### 2. `frontend/` (Interface Conversacional Next.js)
* **Framework:** Next.js 16 (App Router) empacotado via Turbopack com React 19 e TypeScript.
* **Estilização e Identidade Visual:** Tailwind CSS v4 com tokens de design *Liquid Blue* e *Liquid Glassmorphism*.
* **Streaming Fluido:** Renderização em tempo real de tokens via NDJSON/SSE com suporte a cancelamento de requisição (`AbortController`).
* **Componentes Especializados:**
  - Mascote visual acolhedora com micro-animações.
  - Dropdowns retráteis de citação de fontes oficiais governamentais com links resolvidos.
  - Chips de navegação rápida e opções contextuais para reduzir a barreira de digitação do cidadão.
  - Mapa interativo vetorial SVG das unidades de saúde por Região Administrativa.

### 3. `scripts/` (Automação, Avaliação e Ingestão)
* **`run_automated_eval.py`:** Bateria de testes automatizados ponta a ponta avaliando 18 cenários contra a API em execução (100% de aprovação).
* **`index_corpus.py`:** Script standalone para descoberta recursiva e indexação do corpus no ChromaDB e no índice BM25.
* **`train.py` (Guardrails):** Pipeline de treino e validação cruzada 5-Fold Stratified com logging automático de métricas no MLflow.

---

## 🧪 Comandos Rápidos de Execução e Testes

```bash
# Execução da suíte de 97 testes unitários do backend
cd susana_rag_backend
source .venv/bin/activate
pytest tests/ -v

# Execução do benchmark automatizado de homologação (18 cenários)
python scripts/run_automated_eval.py

# Build de produção do frontend Next.js
cd ../susana-ui
npm run build
```

*Nota: O código-fonte funcional e homologado encontra-se preservado na branch `homologacao` e será transferido progressivamente conforme validação da banca avaliadora.*
