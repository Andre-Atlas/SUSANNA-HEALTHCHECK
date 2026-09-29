# Susana Backend v0.2.0

Backend inicial da Susana, assistente conversacional para informações sobre serviços do SUS no Distrito Federal.

## Arquitetura

```text
React
  ↓
FastAPI /api/v1
  ↓
Scope / Intent
  ├── dados estruturados → PostgreSQL
  └── RAG → pgvector
                 ↓
             evidências
                 ↓
              Ollama
                 ↓
         resposta + fontes
```

A versão 0.2 usa recuperação híbrida: unidades e serviços podem ser consultados diretamente no PostgreSQL, enquanto explicações documentais passam pelo RAG. A proveniência de estabelecimentos pode ser registrada por `source_id`.

## Requisitos

- Python 3.12+
- Docker + Docker Compose
- Ollama local para chat/RAG real

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Subir PostgreSQL + pgvector:

```bash
docker compose up -d postgres
```

A migration inicial usa `vector(768)`. O modelo de embeddings configurado precisa produzir essa dimensão, ou a migration e `EMBEDDING_DIMENSIONS` devem ser ajustados de forma consistente antes de executar `alembic upgrade head`.

```bash
alembic upgrade head
```

Rodar API:

```bash
uvicorn app.main:app --reload
```

Documentação:

- http://localhost:8000/docs
- http://localhost:8000/redoc
- http://localhost:8000/openapi.json

## Seed

O seed contém apenas dados explicitamente DEMO:

```bash
python -m scripts.seed
```

Não tratar esse seed como corpus oficial.

## Ollama

No `.env`:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=<modelo-de-chat>
EMBEDDING_MODEL=<modelo-de-embedding>
EMBEDDING_DIMENSIONS=768
```

O provider utiliza `/api/generate` para geração e `/api/embed` para embeddings.

Depois de configurar o modelo de embeddings, rode:

```bash
python -m scripts.check_ollama
```

Esse teste confirma a dimensão real produzida pelo Ollama contra `EMBEDDING_DIMENSIONS`.

## Endpoints

### Health

```http
GET /api/v1/health
GET /api/v1/health/dependencies
```

### Chat

```http
POST   /api/v1/chat
DELETE /api/v1/chat/sessions/{session_id}
```

O DELETE limpa a memória volátil da sessão e pode ser usado pelo botão "Nova conversa" no frontend.

Exemplo:

```json
{
  "session_id": "00000000-0000-0000-0000-000000000001",
  "message": "Onde encontro vacinação em Samambaia?",
  "context": {"ra": "Samambaia"}
}
```

### Unidades

```http
GET    /api/v1/unidades
GET    /api/v1/unidades/{id}
GET    /api/v1/unidades/{id}/servicos
POST   /api/v1/unidades
PUT    /api/v1/unidades/{id}
DELETE /api/v1/unidades/{id}
```

Filtros: `type`, `ra`, `cep`, `name`, `limit`, `offset`.

### Serviços

```http
GET    /api/v1/servicos
GET    /api/v1/servicos/{id}
POST   /api/v1/servicos
PUT    /api/v1/servicos/{id}
DELETE /api/v1/servicos/{id}
```

### Fontes

```http
GET    /api/v1/fontes
GET    /api/v1/fontes/{id}
POST   /api/v1/fontes
PUT    /api/v1/fontes/{id}
DELETE /api/v1/fontes/{id}
```

### RAG

```http
GET    /api/v1/rag/documents
GET    /api/v1/rag/documents/{id}
POST   /api/v1/rag/documents
PUT    /api/v1/rag/documents/{id}
DELETE /api/v1/rag/documents/{id}
POST   /api/v1/rag/documents/{id}/ingest
GET    /api/v1/rag/documents/{id}/chunks
POST   /api/v1/rag/search
```

### CKAN

```http
GET /api/v1/ckan/packages
GET /api/v1/ckan/packages/search?q=<termo>
GET /api/v1/ckan/packages/{dataset_id}
GET /api/v1/ckan/groups
GET /api/v1/ckan/tags
GET /api/v1/ckan/resources/search?query=<termo>
```

Integração baseada na Action API documentada pelo CKAN:

https://docs.ckan.org/en/latest/api/
https://docs.ckan.org/en/latest/api/#api-guide

Os URLs `demo.ckan.org` da documentação são apenas exemplos. Configure `CKAN_BASE_URL` com o serviço CKAN que realmente for utilizado.

## Testes

```bash
pytest
```

Os testes unitários básicos não dependem do Ollama nem do PostgreSQL.

## Próximos passos

1. substituir o seed DEMO pelos primeiros dados oficiais do corpus;
2. definir o modelo de embeddings e confirmar sua dimensão;
3. ingerir documentos reais;
4. validar `/api/v1/rag/search` antes de ajustar o prompt;
5. integrar o React;
6. criar o conjunto de avaliação da Susana.
