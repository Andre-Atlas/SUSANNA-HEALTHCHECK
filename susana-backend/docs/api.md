# API da Susana

Base: `/api/v1`

Documentação interativa:

- `/docs`
- `/redoc`
- `/openapi.json`

## Health

`GET /health`

`GET /health/dependencies`

## Chat

`POST /chat`

Recebe `session_id`, `message` e contexto territorial opcional (`ra`, `cep`).

## Unidades

`GET /unidades`

`GET /unidades/{id}`

`GET /unidades/{id}/servicos`

`POST /unidades`

`PUT /unidades/{id}`

`DELETE /unidades/{id}`

Filtros de lista: `type`, `ra`, `cep`, `name`, `limit`, `offset`.

## Serviços

`GET /servicos`

`GET /servicos/{id}`

`POST /servicos`

`PUT /servicos/{id}`

`DELETE /servicos/{id}`

## Fontes

`GET /fontes`

`GET /fontes/{id}`

`POST /fontes`

`PUT /fontes/{id}`

`DELETE /fontes/{id}`

Uma fonte com documentos ou estabelecimentos associados não deve ser excluída.

## RAG

`GET /rag/documents`

`GET /rag/documents/{id}`

`POST /rag/documents`

`PUT /rag/documents/{id}`

`DELETE /rag/documents/{id}`

`POST /rag/documents/{id}/ingest`

`GET /rag/documents/{id}/chunks`

`POST /rag/search`

## CKAN

`GET /ckan/packages`

`GET /ckan/packages/search?q=...`

`GET /ckan/packages/{dataset_id}`

`GET /ckan/groups`

`GET /ckan/tags`

`GET /ckan/resources/search?query=...`

A integração utiliza a Action API do CKAN através de `CKAN_BASE_URL`.
