# 🛠️ Guia de Build, Execução e Testes — SUS Digital (Projeto Suzanna)

---

## 📋 1. Pré-Requisitos de Ambiente

Para executar e testar todos os módulos da plataforma, certifique-se de que o ambiente local possui:
- **Python:** Versão `3.9` ou superior (testado e homologado no Python 3.9.6 no macOS/Linux).
- **Node.js:** Versão `18.17` ou superior (suporte nativo ao Next.js 16).
- **Gerenciador de Pacotes:** `npm` versão `9+`.
- **Git:** Versão `2.30+`.
- **Ollama (Opcional para Fallback Local):** `ollama run llama3.1:8b` (o backend possui gerador inteligente interno e fallback RAG mesmo sem Ollama ativo).

---

## ⚙️ 2. Execução do Backend (FastAPI + RAG Pipeline)

### 2.1. Configuração do Ambiente Virtual Python
Navegue até a pasta do backend e crie o ambiente virtual:
```bash
cd susana_rag_backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.2. Variáveis de Ambiente (`.env`)
Copie o arquivo de exemplo se necessário:
```bash
cp .env.example .env
```

Configurações principais suportadas:
```ini
# Configuração do Gateway FastAPI
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Limiar de Relevância Semântica
RELEVANCE_CONFIDENT_THRESHOLD=0.35

# ChromaDB
CHROMA_PERSIST_DIRECTORY=data/chroma_db

# Chave Secreta para Webhooks de Ingestão
INGESTION_SECRET_KEY=chave_secreta_homologacao_sus_2026
```

### 2.3. Inicialização do Servidor FastAPI
Execute o Uvicorn na porta 8000:
```bash
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- **URL da API:** `http://localhost:8000`
- **Documentação Interativa Swagger:** `http://localhost:8000/docs`
- **Verificação de Saúde (Health Check):** `http://localhost:8000/health`

---

## 🌐 3. Execução do Frontend (Next.js 16 + Turbopack)

### 3.1. Instalação de Dependências
Navegue até a pasta do frontend e instale os pacotes:
```bash
cd susana-ui
npm install
```

### 3.2. Execução em Modo de Desenvolvimento
Inicie o servidor de desenvolvimento com hot-reload na porta 3000:
```bash
npm run dev
```
Acesse no navegador: **`http://localhost:3000`**

### 3.3. Compilação para Produção (Build)
Para verificar a tipagem TypeScript e compilar os pacotes otimizados:
```bash
npm run build
```
*Tempo típico de compilação Turbopack: ~500ms.*

---

## 🧪 4. Execução de Testes Automatizados

### 4.1. Suíte Completa de Testes do Backend (81 Testes)
A suíte abrange testes unitários, de integração, concorrência, personas multi-turn reais, guardrails e busca online:
```bash
source susana_rag_backend/.venv/bin/activate
pytest susana_rag_backend/tests/ -v
```

Para uma execução rápida e silenciosa:
```bash
pytest susana_rag_backend/tests/ -q
```

#### Detalhamento das Suítes de Testes:
| Arquivo de Teste | Quantidade | Foco da Validação |
| :--- | :--- | :--- |
| `test_citizen_units_vaccines.py` | 7 testes | Cadastro de cidadão (CPF/CNS Módulo 11), catálogo das 346 unidades e guia PNI. |
| `test_nlu_clustering_personas_real.py` | 10 testes | Personas reais (Idoso, Gestante, Recém-Nascido, Criança e Dengue) com dados 100% reais do DF. |
| `test_personas_multiturn_real.py` | 7 testes | Conversação encadeada multi-turn e inferência de contexto demográfico. |
| `test_online_search_scoped.py` | 7 testes | Busca externa assíncrona, proteção contra SSRF, circuit breaker e persistência. |
| `test_concurrency_robustness.py` | 4 testes | Thread-safety no `SemanticCache` com 50 threads e rajadas concorrentes de webhook. |
| `test_ingestion_pipeline.py` | 10 testes | Ingestão com verificação TLS, idempotência e substituição atômica de chunks por URL. |
| `test_rag.py` | 16 testes | Contrato de citações, streaming NDJSON e formatação de resposta. |
| `test_retriever.py` | 12 testes | Busca vetorial ChromaDB, expansão de plurais e limiares semânticos. |
| `test_pipeline_citations.py` | 8 testes | Rastreabilidade de proveniência de fontes públicas da SES-DF. |

---

## 🚨 5. Diagnóstico e Resolução de Problemas (Troubleshooting)

### 5.1. Erro `Address already in use` (Portas 8000 ou 3000 travadas)
Se o servidor estiver rodando em segundo plano e a porta estiver ocupada, use os comandos abaixo para forçar o encerramento dos processos órfãos:
```bash
# Encerrar backend na porta 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Encerrar frontend na porta 3000
lsof -ti:3000 | xargs kill -9 2>/dev/null
```

### 5.2. Erro de Conexão com o ChromaDB
Caso o ChromaDB apresente erro de bloqueio de lock, certifique-se de que apenas uma instância do backend acesse a pasta `data/chroma_db/`. O modo WAL do SQLite em `data/susana_app.db` já previne conflitos de concorrência automaticamente.

### 5.3. Cache do Next.js
Se notar discrepâncias de layout após alterações em componentes, limpe a pasta de build temporária:
```bash
rm -rf susana-ui/.next
npm --prefix susana-ui run dev
```

---

*Documento de Build e Execução Homologado · Projeto Suzanna (SUS Digital).*
