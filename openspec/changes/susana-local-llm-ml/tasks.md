# Tarefas: Implementação ML e LLM Local

- [x] **Fase 0:** Configuração e Adaptação dos Portos
  - [x] Instalar dependências (`httpx`, `pydantic-settings`, etc.).
  - [x] Criar infraestrutura `LLMPort` e `IntentClassifierPort` no arquivo `app/ports.py`.
  - [x] Criar `OllamaAdapter` em `app/llm/ollama_adapter.py`.
  - [x] Refatorar prompts.
  - [x] Definir contratos em `openspec/changes/susana-local-llm-ml/contracts.md`.

- [x] **Fase 1:** Construção do Motor de RAG Local
  - [x] Implementar extração de blocos (`app/rag/corpus.py`).
  - [x] Encapsular embeddings usando `sentence-transformers` (`app/rag/embeddings.py`).
  - [x] Integrar ChromaDB ao Retriever e implementar o Semantic Cache (`app/rag/retriever.py`).
  - [x] Extrair dados oficiais da SES-DF e salvá-los usando script automatizado.
  - [x] **Ação Pendente:** Refatorar `app/rag/pipeline.py` e `app/main.py` para usar as implementações acima via Injeção de Dependências.

- [x] **Fase 2:** Avaliação de Modelos de Embeddings Locais
  - [x] Criar dataset de validação `ml/retrieval/eval_set.jsonl`.
  - [x] Escrever script de benchmark para testar e selecionar o melhor embedding (avaliando `all-MiniLM-L6-v2`, `multilingual-e5-small`, etc.).

- [x] **Fase 3:** Treinamento do Classificador ML Guardrail
  - [x] Gerar dataset estático e sintético para Intents Clínicos e Administrativos (sem scraping externo).
  - [x] Implementar classe de Guardrails no backend.
  - [x] Treinar modelo `scikit-learn` com Regressão Logística e TF-IDF.

- [x] **Fase 4:** Integração DVC e MLflow
  - [x] Inicializar o DVC e configurar versionamento do dataset.
  - [x] Inicializar e registrar experimentos no MLflow local com SQLite.
  - [x] Configurar sistema de aliasing (`@champion`) para promotion gates.

- [x] **Fase 5:** Implementação e Testes E2E
  - [x] Escrever testes unitários e de integração mockando os adaptadores do LLM.
  - [x] Validar o RAG e o Guardrail localmente.

- [x] **Fase 6:** Finalização e UI
  - [x] Assegurar streaming da resposta HTTP no Frontend via API local.
  - [x] Gerar documentos (Docs de Design de Software - SDD).
