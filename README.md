# Susana - Assistente RAG do SUS-DF

Assistente virtual administrativa para consultar informações públicas sobre os serviços do SUS-DF.

## Estrutura do repositório

- `susana-ui/`: interface Next.js.
- `susana_rag_backend/`: API FastAPI, RAG, testes e avaliações de ML.
- `CORPUS/`: documentos de origem usados pelo projeto.
- `data/` e `models/`: dados processados e artefatos locais de análise/modelos.
- `notebooks/`: notebooks e módulos auxiliares de análise.
- `scripts/analysis/`: análises exploratórias e correlações.
- `scripts/notebooks/`: geradores de notebooks.
- `scripts/documents/`: geradores de documentos.
- `docs/`: documentação, arquitetura, MLOps e notas de versão.
- `openspec/`: propostas e especificações de mudanças.

## Pré-requisitos

- Python 3.11 ou superior.
- Node.js 20.9 ou superior e npm.
- Ollama instalado e em execução para respostas com o modelo local.

Na primeira inicialização, o backend baixa o modelo de embeddings e indexa o corpus. Para geração de respostas, baixe também o modelo Ollama configurado:

```bash
ollama pull llama3.1:8b
```

## Rodar localmente

No primeiro terminal, prepare e inicie a API:

```bash
cd susana_rag_backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

No segundo terminal, a partir da raiz do repositório, inicie a interface:

```bash
cd susana-ui
npm ci
npm run dev
```

Abra `http://localhost:3000`. A API fica em `http://localhost:8000`; seu estado pode ser conferido em `/health` e a documentação interativa em `/docs`.

## Testes e avaliações

Para executar os testes automatizados do backend, ative o ambiente virtual e rode, dentro de `susana_rag_backend/`:

```bash
pytest
```

Os benchmarks de embeddings, LLMs e guardrails estão em `susana_rag_backend/ml/`. O MLflow local usa `susana_rag_backend/mlflow.db`; instruções de avaliação ficam em [docs/mlops/llm_evaluation_playbook.md](docs/mlops/llm_evaluation_playbook.md).

## Documentação

- [Relatório técnico](docs/relatorio_tecnico.md)
- [Plano de prontidão para produção](docs/production-readiness-plan.md)
- [Visão arquitetural em PDF](docs/architecture/Projeto_Susana_Visao_Geral.pdf)
- [Notas de versão MLOps](docs/releases/RELEASE_NOTES_MLOPS.md)
