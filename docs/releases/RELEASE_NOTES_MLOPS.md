# Susana HealthCheck - MLOps & RAG Engine Release

## 1. Estado de Desenvolvimento (Development State)
O projeto **Susana (Assistente SUS-DF)** avançou da fase de Prova de Conceito (PoC) para uma Arquitetura Hexagonal robusta de RAG (Retrieval-Augmented Generation). 
- **Front-End:** Next.js configurado com Server-Sent Events (SSE) nativos para renderizar em streaming as respostas do LLM, implementando skeletons de carregamento e banners de mitigação de risco (Acessibilidade + UI Impeccable).
- **Back-End:** FastAPI refatorado para servir via streaming de chunks (NDJSON). Foi implementado fallback extrativo, injeção de dependência e desacoplamento do motor de Embeddings, Guardrails e Ollama LLM.
- **Integração de Dados:** Pipeline implementada (`collect_opendata.py`) simulando o portal CKAN governamental, indexando informações oficiais de unidades de saúde, distribuição de soros, SISREG e campanhas vacinais.

## 2. Estratégia e Governança de MLOps
O versionamento e controle dos modelos foi centralizado com **MLflow** local via SQLite.
- **Avaliação de LLMs (Benchmark):** Foram avaliados modelos como `Llama 3.1 8B`, `Phi 3.5`, e `Qwen 2.5 3B/7B`. O benchmark validou a *Latência* (TTFT), *Tokens por Segundo (TPS)* e principalmente a *Fidelidade (Groundedness)*, garantindo que o modelo não alucine prescrições.
- **Guardrails com Scikit-Learn:** O classificador de segurança pré-RAG foi movido para um pipeline híbrido. A intenção primária do paciente é avaliada via Regressão Logística. Se a inferência barrar contexto clínico (como diagnósticos), o pedido nem chega ao Ollama. A versão atual do classificador (`v4`) está registrada com o alias `@champion`.
- **Semantic Cache:** As perguntas são hasheadas via vetor, economizando tokens e hardware em inferências idênticas (distância < 0.08).

## 3. Histórico de Testes e Validação
A infraestrutura passou pelas baterias do `pytest` garantindo:
- Integração da porta de LLM (Mock de streaming no teste).
- Validação do `Retriever` para garantir indexação no ChromaDB.
- Comportamento de Fallback da coleta do Corpus (simulação do Erro HTTP 404 da API do Governo substituído pelo mock estático interno).
- O Frontend foi validado no tratamento de erros HTTP 503 sem quebrar a UI, e finalmente integrando o parseamento contínuo de `type: chunk` e `type: done`.
