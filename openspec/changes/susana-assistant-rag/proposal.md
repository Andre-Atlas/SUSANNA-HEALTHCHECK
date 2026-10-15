## Why

A Secretaria de Saúde necessita de uma interface eficiente e confiável para responder dúvidas dos cidadãos sobre unidades, horários e fluxos administrativos do SUS-DF. A implementação de um chatbot baseado em RAG garante que as respostas sejam exclusivamente originadas de fontes oficiais, com um rígido SLA de 15 segundos para alta disponibilidade, bloqueando qualquer interação de cunho clínico.

## What Changes

- Criação do frontend (UI) no React/Next.js baseado no Design System "Susana" (balões, citações de fonte, avisos de escopo).
- Criação de um backend FastAPI com LangChain para orquestrar RAG e buscas de documentos oficiais.
- Implementação de NeMo Guardrails para classificar e bloquear instantaneamente perguntas clínicas (Caso C).
- Implementação de um Cache Semântico (Redis Vector Search) para garantir latência sub-segundo em perguntas frequentes, respeitando a meta de < 15s.
- Setup do fluxo de MLOps: versionamento de dados com DVC e rastreamento de experimentos com MLflow.

## Capabilities

### New Capabilities
- `susana/chat-interface`: A interface de chat em React interagindo com as APIs RAG.
- `susana/rag-backend`: O serviço que indexa os PDFs e responde a perguntas administrativas com citação.
- `susana/guardrails`: O roteador pré-LLM para bloquear orientações clínicas.

### Modified Capabilities

## Impact

Afeta o fluxo de atendimento virtual do usuário. Demanda provisionamento do Redis, infraestrutura de DVC (S3/storage) e banco MLflow.
