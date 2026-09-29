# Arquitetura do Backend da Susana

## Visão geral

```text
React
  |
  v
FastAPI /api/v1
  |
  +--> ScopeService / Intent
  |
  +--> Estruturado --------------------+
  |       PostgreSQL                     |
  |                                      v
  +--> RAG --> pgvector --> evidências --> Ollama
                                      |
                                      v
                              resposta + fontes
```

A arquitetura utiliza duas estratégias de recuperação:

- dados estruturados para unidades e serviços;
- RAG para conteúdo documental e orientações textuais.

## Responsabilidades

`api/v1/`: contrato HTTP, validação e status HTTP.

`services/`: regras e orquestração do caso de uso.

`repositories/`: acesso persistente ao PostgreSQL.

`providers/`: integrações externas, com Ollama isolado atrás de providers.

`models/`: ORM SQLAlchemy.

`schemas/`: contratos Pydantic.

## Chat híbrido

Perguntas sobre unidade podem consultar PostgreSQL diretamente. Perguntas que exigem explicação textual utilizam pgvector. Intenções como vacinação podem combinar os dois caminhos.

## Proveniência

Documentos apontam para uma fonte. Estabelecimentos também podem apontar para uma fonte. A resposta do chat expõe somente evidências que mantêm associação com uma fonte conhecida.

## Estado do MVP

Não há autenticação Gov.br, CPF, prontuário, histórico clínico, agendamento real ou geolocalização automática.

A sessão conversacional permanece em memória de processo por enquanto. Isso é deliberado para o MVP e não deve ser interpretado como armazenamento clínico.
