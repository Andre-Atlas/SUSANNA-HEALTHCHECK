Este documento é a fonte de verdade para as tarefas. O plano de implementação original foi arquivado.

## 1. Setup & MLOps Foundation

- [ ] 1.1 Inicializar DVC localmente e criar um arquivo de sample content mockado para simular PDFs do SUS-DF, validando a adição via `dvc add`.
- [ ] 1.2 Configurar o MLflow local, instalar dependências MLOps (`mlflow`, `dvc`, `fastapi`) e confirmar rodando `mlflow ui` local.

## 2. RAG Backend & Guardrails

- [ ] 2.1 Criar o backend FastAPI (`susana_rag_backend/app/main.py`) com as dependências do LangChain e LlamaIndex, verificando via curl na rota raiz.
- [ ] 2.2 Implementar o Semantic Cache integrado ao Vector Store Redis (ou ChromaDB local provisório para evitar infra de docker) e validar com um teste automatizado medindo o tempo da segunda requisição (< 2s).
- [ ] 2.3 Implementar roteamento NeMo Guardrails para rejeição de prompts de cunho clínico e verificar criando um teste `test_guardrails.py` falhando rápido e seguro.
- [ ] 2.4 Integrar o LLM (Gemini) para ler os dados dummy retornando contexto com source citations. Verificar testando perguntas do domínio administrativo e validando a citação extraída no payload JSON.

## 3. UI Prototype (Susana)

- [ ] 3.1 Inicializar o projeto Next.js no diretório `susana-ui` com TailwindCSS configurado para a paleta "Azul Susana" e rodar o servidor verificando a página incial.
- [ ] 3.2 Criar componentes de chat (`MessageBubble` e `SourceCitation`) refletindo os estados Normal e Bloqueado (Alerta de escopo clínico). Validar via Storybook ou renderização no browser.
- [ ] 3.3 Consumir a API do FastAPI pelo Next.js, interligando a UI Susana ao backend RAG. Validar digitando uma pergunta administrativa no chat e recebendo a fonte oficial no balão em menos de 15s.
