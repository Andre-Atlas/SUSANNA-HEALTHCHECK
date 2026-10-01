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

Para entender o caminho da pergunta, a busca estruturada, o RAG e o que ainda falta para o produto final, consulte o [guia didático de funcionamento da Susana](docs/como-a-susana-funciona.md).

## Requisitos

- Python 3.12+
- Docker + Docker Compose
- Ollama local para chat/RAG real

## Instalação

Execute os comandos a partir da raiz do repositório clonado:

```bash
cd susana-backend
make install
cp .env.example .env
```

Subir PostgreSQL + pgvector:

```bash
make up
```

A migration inicial usa `vector(768)`. O modelo de embeddings configurado precisa produzir essa dimensão, ou a migration e `EMBEDDING_DIMENSIONS` devem ser ajustados de forma consistente antes de executar `alembic upgrade head`.

```bash
make migrate
```

Rodar API:

```bash
make dev
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

Baixe um modelo de chat e um modelo de embeddings compatível com a dimensão do banco:

```env
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

No `.env`, configure os nomes dos modelos instalados:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
EMBEDDING_MODEL=nomic-embed-text:latest
EMBEDDING_DIMENSIONS=768
```

O provider utiliza `/api/generate` para geração e `/api/embed` para embeddings. Reinicie a API depois de alterar `.env`.

Depois de configurar o modelo de embeddings, rode:

```bash
python -m scripts.check_ollama
```

Esse teste confirma a dimensão real produzida pelo Ollama contra `EMBEDDING_DIMENSIONS`.

## Colocar documentos no RAG

O chat não responde com conhecimento geral quando não encontra evidências. Cadastre uma fonte oficial, um documento obtido dessa fonte e depois indexe-o:

1. Crie uma fonte por `POST /api/v1/fontes`, com nome, URL oficial e `source_type` apropriado.
2. Crie um documento por `POST /api/v1/rag/documents`, usando o `source_id` retornado e o conteúdo autorizado da página/documento.
3. Indexe-o com `POST /api/v1/rag/documents/{id}/ingest`.
4. Confirme `status: "indexed"` e teste `POST /api/v1/rag/search` antes de validar o chat.
5. Consulte `GET /api/v1/health/dependencies`: `ollama_chat` e `ollama_embeddings` devem estar como `ok`.

O repositório não contém corpus oficial ingerido. Registros DEMO servem apenas para validar a integração e não devem ser usados para responder cidadãos.

### Importar os Markdown da pasta `DADOS`

Revise `DADOS/manifest.json` e marque `status: "approved"` somente para arquivos conferidos com a fonte indicada. Primeiro veja a prévia, sem gravar nada:

```bash
python -m scripts.ingest_markdown_directory
```

Para criar/atualizar os documentos e gerar embeddings no Ollama:

```bash
python -m scripts.ingest_markdown_directory --apply
```

O importador é idempotente: se o conteúdo não mudou e já estiver indexado, ele não o processa de novo. Alterações no arquivo aprovado atualizam o documento e refazem sua indexação. Arquivos `review_required` são ignorados.

## Endpoints

### Health

```http
GET /api/v1/health
GET /api/v1/health/dependencies
```

`/health/dependencies` informa separadamente `postgres`, `pgvector`, `ollama_chat`, `ollama_embeddings` e `indexed_documents`. Os modelos podem estar prontos enquanto `indexed_documents` ainda é `0`; nesse estado, o chat deve informar que não encontrou evidências.

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
make test
```

Os testes unitários básicos não dependem do Ollama nem do PostgreSQL.
Para executar lint e testes juntos, use `make check`.

## Próximos passos

1. substituir o seed DEMO pelos primeiros dados oficiais do corpus;
2. definir o modelo de embeddings e confirmar sua dimensão;
3. ingerir documentos reais;
4. validar `/api/v1/rag/search` antes de ajustar o prompt;
5. integrar o React;
6. criar o conjunto de avaliação da Susana.
