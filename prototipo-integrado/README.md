# Susana — protótipo integrado

Frontend React/Vite independente, baseado no protótipo visual existente e conectado ao backend FastAPI em `susana-backend`.

## Executar localmente

Pré-requisitos: Python 3.12+, Docker com Compose, Node.js 20.19+ (ou 22.12+) e Ollama. Execute os comandos abaixo a partir de `Documents`, onde fica a pasta `SUSANNA-HEALTHCHECK`.

### Preparar e iniciar o backend

No primeiro uso, instale as dependências e crie o arquivo de configuração apenas se ele ainda não existir:

```bash
cd SUSANNA-HEALTHCHECK/susana-backend
make install
if [ ! -f .env ]; then cp .env.example .env; fi
```

Confira no `.env` os nomes dos modelos e mantenha `EMBEDDING_DIMENSIONS=768`, compatível com a migration atual. Inicie o Ollama e baixe os modelos configurados; por padrão:

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text:latest
```

Em um terminal de backend:

```bash
cd SUSANNA-HEALTHCHECK/susana-backend
make up
make migrate
make ollama-check
```

### Indexar os documentos aprovados de `DADOS`

Ainda na pasta `susana-backend`, confira primeiro o plano de importação:

```bash
.venv/bin/python -m scripts.ingest_markdown_directory
```

Revise `DADOS/manifest.json` e o conteúdo contra a origem oficial antes de aprovar qualquer documento. No manifesto atual, apenas `02_HUB_Farmacia_Escola.md` está marcado como `approved`; os demais são ignorados por exigirem revisão. Depois de conferir a prévia e validar os modelos, gere os embeddings e indexe:

```bash
.venv/bin/python -m scripts.ingest_markdown_directory --apply
```

O importador atualiza fontes/documentos existentes e evita reindexar conteúdo inalterado. A API recupera os trechos indexados por similaridade vetorial; não marque conteúdo como aprovado sem conferência da fonte.

Inicie a API em um terminal separado:

```bash
cd SUSANNA-HEALTHCHECK/susana-backend
make dev
```

### Iniciar o frontend

Em outro terminal:

```bash
cd SUSANNA-HEALTHCHECK/prototipo-integrado
npm install
npm run dev
```

Abra http://127.0.0.1:5174. O Vite encaminha `/api/*` para `http://127.0.0.1:8000`, sem exigir CORS entre as origens do navegador. O Vite usa a porta 5174 e para com erro se ela já estiver ocupada.

Para apontar o proxy a outro endereço, defina `VITE_BACKEND_URL` no ambiente antes de iniciar o Vite. Verifique http://127.0.0.1:8000/api/v1/health/dependencies: `postgres`, `pgvector` e `ollama` devem estar como `ok`, e `indexed_documents` deve ser maior que `0` para o RAG responder com evidências.

## O que está conectado

- A conversa envia `POST /api/v1/chat` com UUID de sessão e contexto de Região Administrativa quando identificado.
- "Nova conversa" limpa a sessão no backend e cria um novo UUID.
- As referências retornadas pela API são exibidas como links externos.
- O cabeçalho do chat verifica `GET /api/v1/health/dependencies` e distingue modelos ausentes de corpus ainda vazio.

O chat requer o backend, PostgreSQL/pgvector e Ollama ativos, modelos configurados e ao menos um documento indexado. Sem evidências relevantes, a API informa que não encontrou base suficiente para responder.

## Projetos separados

- `susana-backend/`: API e banco.
- `prototipo_react/`: protótipo original, ainda independente.
- `prototipo-integrado/`: cópia integrada com dependências frontend próprias.