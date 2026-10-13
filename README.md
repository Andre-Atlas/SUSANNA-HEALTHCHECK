# 💙 SUS Digital — Assistente Virtual Inteligente Suzanna (SUS-DF)
> **Plataforma Unificada de Inteligência em Saúde Pública para o Distrito Federal**  
> *RAG Semântico · NLU em Português · Governança Clínica · 33 Regiões Administrativas · Liquid Glassmorphism*

---

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js 16](https://img.shields.io/badge/Next.js-16_Turbopack-black?logo=next.js&logoColor=white)](https://nextjs.org)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-orange)](https://www.trychroma.com)
[![MLflow](https://img.shields.io/badge/MLflow-Experiment_Tracking-blue?logo=mlflow&logoColor=white)](https://mlflow.org)
[![Pytest](https://img.shields.io/badge/Tests-81_passed-brightgreen?logo=pytest&logoColor=white)](https://pytest.org)
[![Acessibilidade](https://img.shields.io/badge/WCAG-2.1_AA-success)](https://www.w3.org/WAI/standards-guidelines/wcag/)

---

## 📖 Visão Geral

O **SUS Digital (Projeto Suzanna)** é uma plataforma desenvolvida para modernizar e humanizar o acesso aos serviços públicos de saúde do Distrito Federal (SES-DF). O sistema combina:

1. **Assistente Virtual Humanizada (Suzanna):** Mascote 3D interativa guiando o cidadão com acolhimento, linguagem acessível e empatia.
2. **Motor RAG com NLU Integrado:** Inferência de linguagem natural ultrarrápida (< 2ms) com resolução de entidades geográficas em 100% das **33 Regiões Administrativas (RAs)** do DF.
3. **Segurança Clínica Estrita (Guardrails):** Detecção fail-closed de perguntas que solicitam diagnóstico ou posologia médica, direcionando o paciente com segurança para a UBS ou SAMU 192.
4. **Catálogo Geográfico de 346 Unidades:** Mapa interativo em SVG com projeção de coordenadas e informações oficiais de horário, procedimentos e emergência.
5. **Ciclo Vacinal Personalizado (PNI):** Recomendações e histórico vacinal adaptados à faixa etária e perfil clínico (Idosos, Crianças, Gestantes, Recém-nascidos e Adultos).
6. **Pesquisa Online Assíncrona & Anti-SSRF:** Busca complementar em tempo real restrita a portais governamentais seguros (`saude.df.gov.br`, `gov.br`, `fiocruz.br`).

---

## 📚 Documentação Técnica Completa

Toda a engenharia, modelagem e design do projeto estão detalhados na suíte de documentação oficial:

| Documento | Caminho no Repositório | Descrição |
| :--- | :--- | :--- |
| **🏛️ Arquitetura e Funcionamento** | [`docs/ARQUITETURA_E_FUNCIONAMENTO.md`](docs/ARQUITETURA_E_FUNCIONAMENTO.md) | Fluxo ponta a ponta, diagramas C4/Mermaid, NLU, streaming NDJSON e persistência SQLite WAL. |
| **🔬 MLOps e Modelagem** | [`docs/MLOPS_E_MODELAGEM.md`](docs/MLOPS_E_MODELAGEM.md) | Classificador clínico, 5-Fold Stratified CV, MLflow, Honest Benchmark e partições congeladas DEV/TEST. |
| **🛠️ Guia de Build e Execução** | [`docs/BUILD_E_EXECUCAO.md`](docs/BUILD_E_EXECUCAO.md) | Setup passo a passo, portas, variáveis de ambiente, troubleshooting e suíte de 81 testes. |
| **🎨 Design System e Identidade Visual** | [`susana-ui/docs/DESIGN_SYSTEM_IDENTIDADE_VISUAL.md`](susana-ui/docs/DESIGN_SYSTEM_IDENTIDADE_VISUAL.md) | Tokens CSS Liquid Blue, atmosfera de orbes, Liquid Glassmorphism e ativos da mascote Suzanna em 3D. |

---

## 🚀 Quickstart — Como Executar Localmente

### 1. Parar Processos Anteriores (Se portas ocupadas)
```bash
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null
```

---

### 2. Executar o Backend (API FastAPI)
```bash
cd susana_rag_backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- API ativa em: **`http://localhost:8000`**
- Swagger interativo: **`http://localhost:8000/docs`**

---

### 3. Executar o Frontend (Next.js 16)
Em outro terminal:
```bash
cd susana-ui
npm install
npm run dev
```
- Acesse a interface web em: **`http://localhost:3000`**

---

## 🧪 Suíte de Testes Automatizados

Para executar a validação de regressão do backend (81 testes passando sem dados mockados):
```bash
cd susana_rag_backend
source .venv/bin/activate
pytest tests/ -v
```

Para validar a compilação de produção do frontend Next.js:
```bash
cd susana-ui
npm run build
```

---

## 📁 Estrutura de Diretórios do Repositório

```text
EDA/
├── docs/                                # Suíte oficial de documentação viva
│   ├── ARQUITETURA_E_FUNCIONAMENTO.md   # Arquitetura detalhada do sistema
│   ├── MLOPS_E_MODELAGEM.md             # Engenharia de ML, MLflow e Honest Benchmark
│   ├── BUILD_E_EXECUCAO.md              # Setup, portas e troubleshooting
│   └── ...                              # Relatórios e análises técnicas
├── susana_rag_backend/                  # Backend assíncrono em FastAPI
│   ├── app/
│   │   ├── main.py                      # Gateway da API FastAPI
│   │   ├── config.py                    # Configurações e limiares semânticos
│   │   ├── citizen/                     # Cadastro, perfis e validadores de CPF/CNS
│   │   ├── chat_sessions/               # Gerenciador de multi-sessões e histórico
│   │   ├── units/                       # Catálogo das 346 unidades de saúde do DF
│   │   ├── vaccines/                    # Guia e calendário de vacinação PNI
│   │   ├── ingestion/                   # Webhook de ingestão contínua com TLS/SHA-256
│   │   └── rag/                         # NLU, Retriever Scoped, Guardrails, Cache e Busca Online
│   ├── data/                            # Corpus, partições congeladas DEV/TEST e SQLite WAL
│   ├── ml/                              # Scripts de treino de guardrails, corpus e benchmarks
│   └── tests/                           # Suíte de 81 testes automatizados (100% verde)
├── susana-ui/                           # Frontend em Next.js 16 (App Router + Turbopack)
│   ├── public/images/                   # Ativos gráficos oficiais da mascote Suzanna em 3D
│   ├── docs/                            # Documentação canônica do Design System
│   └── src/
│       ├── app/
│       │   ├── globals.css              # Tokens Liquid Blue e estilos Glassmorphism (#L e #A)
│       │   ├── layout.tsx               # Root layout com fonte Inter
│       │   └── page.tsx                 # Aplicação completa integrada com chat e módulos
│       └── components/                  # Componentes modulares de visualização
└── README.md                            # Porta de entrada do repositório
```

---

## 🏛️ Governança e Integridade

- **Dados 100% Reais:** Diretório oficial de saúde cobrindo 346 unidades do DF com endereços, horários e coordenadas reais.
- **Fail-Closed:** Proteção defensiva de IA contra automedicação e orientações clínicas inseguras.
- **Desacoplamento Hexagonal:** Regra de negócio isolada de detalhes de persistência e transporte.

---
*SUS Digital · Ministério da Saúde / Secretaria de Saúde do Distrito Federal (SES-DF).*
