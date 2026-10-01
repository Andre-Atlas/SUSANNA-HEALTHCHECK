# Susana — protótipo integrado

Frontend React/Vite independente, baseado no protótipo visual existente e conectado ao backend FastAPI em `susana-backend`.

## Executar localmente

Pré-requisitos: Node.js 20.19+ (ou 22.12+) e os requisitos do backend.

Terminal 1, backend:

```bash
cd susana-backend
make up
make migrate
make dev
```

Terminal 2, frontend:

```bash
cd prototipo-integrado
npm install
npm run dev
```

Abra http://127.0.0.1:5174. O Vite encaminha `/api/*` para `http://127.0.0.1:8000`, sem exigir CORS entre as origens do navegador.

Para apontar o proxy a outro endereço, defina `VITE_BACKEND_URL` no ambiente antes de iniciar o Vite.

## O que está conectado

- A conversa envia `POST /api/v1/chat` com UUID de sessão e contexto de Região Administrativa quando identificado.
- "Nova conversa" limpa a sessão no backend e cria um novo UUID.
- As referências retornadas pela API são exibidas como links externos.
- O cabeçalho do chat verifica `GET /api/v1/health/dependencies` e distingue modelos ausentes de corpus ainda vazio.

O chat requer o backend ativo. Para respostas com Ollama, configure `OLLAMA_MODEL` e `EMBEDDING_MODEL` no `.env` do backend; sem esses provedores, a API pode responder com estado de erro ou sem evidências.

## Projetos separados

- `susana-backend/`: API e banco.
- `prototipo_react/`: protótipo original, ainda independente.
- `prototipo-integrado/`: cópia integrada com dependências frontend próprias.