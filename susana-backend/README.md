# Susana Backend

Backend inicial da Susana, assistente conversacional para informações sobre serviços do SUS no Distrito Federal.

Este guia explica como instalar e iniciar o backend no macOS. Os exemplos partem da pasta `Documents`, que é onde o terminal estava quando ocorreu o erro. **Os comandos de instalação precisam rodar dentro da pasta `susana-backend`**, onde estão `pyproject.toml` e `.env.example`, e não diretamente em `Documents`.

## Arquitetura

```text
React
  ↓
FastAPI /api/v1
  ↓
ScopeService → RetrievalService → PostgreSQL + pgvector → Ollama
                                      ↓
                                fontes/evidências
```

Dados estruturados (unidades/serviços) são separados do conteúdo textual usado pelo RAG.

## Requisitos

- macOS com Python 3.12 ou superior;
- Docker Desktop instalado e aberto para usar o PostgreSQL deste projeto;
- Ollama instalado e em execução para usar chat/RAG com modelos locais.

Docker e Ollama não são necessários para abrir a documentação da API. O PostgreSQL é necessário para aplicar migrations e usar os endpoints que leem ou gravam dados; Ollama e modelos são necessários para geração de respostas e embeddings.

Confira sua versão do Python:

```bash
python3 --version
```

O resultado precisa indicar `Python 3.12` ou superior. Se o Python não estiver instalado ou a versão for menor, instale/ative uma versão compatível antes de continuar.

## Instalação e início rápido

Com Python 3.12 ou superior instalado, copie **o bloco inteiro** abaixo para o terminal. Ele foi preparado para ser executado a partir de `Documents`:

```bash
cd "$HOME/Documents/SUSANNA-HEALTHCHECK/susana-backend" || exit 1

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install -e ".[dev]"

if [ ! -f .env ]; then
  cp .env.example .env
fi

uvicorn app.main:app --reload
```

O bloco entra na pasta que contém `pyproject.toml`, cria o ambiente `.venv` apenas se ele ainda não existir, ativa esse ambiente, instala o backend e as ferramentas de desenvolvimento e cria `.env` sem substituir um arquivo de configuração que você já tenha. Por fim, inicia a API. Aguarde a mensagem `Uvicorn running on http://127.0.0.1:8000` e abra os links abaixo. **Deixe esse terminal aberto** enquanto usar a API; para pará-la, pressione `Control+C` nesse terminal.

Se o comando parar com erro durante `pip install`, corrija primeiro essa etapa: `uvicorn`, `alembic` e `sqlalchemy` só ficam disponíveis quando a instalação termina com sucesso. Se aparecer `does not appear to be a Python project`, confira se o caminho do `cd` corresponde à localização do repositório.

Quando o servidor estiver rodando, abra no navegador:

- http://localhost:8000/docs — documentação interativa;
- http://localhost:8000/redoc — documentação em formato alternativo;
- http://localhost:8000/openapi.json — contrato da API em JSON.

## Seed demonstrativo (opcional)

O seed contém somente dados fictícios identificados como DEMO. Ele não é um corpus oficial do SUS. Execute-o apenas depois de subir o PostgreSQL e aplicar as migrations.

```bash
cd "$HOME/Documents/SUSANNA-HEALTHCHECK/susana-backend"
source .venv/bin/activate
python -m scripts.seed
```

O comando entra na pasta correta, ativa o ambiente virtual e cria registros de demonstração no banco. **Execute-o uma única vez em cada banco limpo**: o script atual insere novos registros toda vez que roda e não é idempotente.

## Ollama (opcional)

O Ollama é necessário para respostas geradas localmente, mas não para iniciar a API ou abrir sua documentação. Instale e inicie o Ollama separadamente. Depois, edite `.env` e informe nomes de modelos que já estejam disponíveis na sua instalação:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=nome-do-modelo-de-chat
EMBEDDING_MODEL=nome-do-modelo-de-embedding
EMBEDDING_DIMENSIONS=768
```

Substitua `nome-do-modelo-de-chat` e `nome-do-modelo-de-embedding` pelos nomes reais dos modelos instalados; não copie esses exemplos literalmente. A dimensão configurada deve coincidir com a saída do modelo de embeddings e com `vector(768)` da migration. O provider usa `/api/generate` para geração e `/api/embed` para embeddings.

## Testes

```bash
cd "$HOME/Documents/SUSANNA-HEALTHCHECK/susana-backend"
source .venv/bin/activate
pytest
```

O `cd` e a ativação garantem que os testes rodem na pasta e no ambiente corretos; `pytest` executa a suíte automatizada. Os testes unitários básicos não dependem do PostgreSQL nem do Ollama. Se aparecer `pytest: command not found`, ative `.venv` e repita `pip install -e ".[dev]"`.

## Testar uma requisição POST manualmente

Para testar uma chamada HTTP real, mantenha a API rodando em um terminal e execute este comando em outro:

```bash
curl -i -X POST "http://127.0.0.1:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "00000000-0000-0000-0000-000000000001",
    "message": "Onde encontro vacinação em Samambaia?",
    "context": {"ra": "Samambaia"}
  }' \
  -w '\n\nTempo total: %{time_total}s\nTempo até o primeiro byte: %{time_starttransfer}s\n'
```

`curl` envia uma requisição para o backend; `-X POST` seleciona o método POST; o cabeçalho informa que o corpo está em JSON; e `-d` envia a pergunta, um identificador de sessão e a Região Administrativa como contexto. A opção `-i` mostra o código HTTP e os cabeçalhos. `-w` imprime a duração total da requisição e o tempo até o primeiro byte da resposta, ambos em segundos. A resposta inclui campos como `reply`, `status`, `sources` e `evidence`. Um `status` como `no_evidence` pode indicar que a chamada funcionou, mas ainda não há conteúdo relevante ingerido para responder.

Esse endpoint usa PostgreSQL com migrations aplicadas, Ollama disponível e modelos de chat e embeddings configurados em `.env`. No estado atual, se o Docker Compose ainda não estiver instalado ou o Ollama não estiver configurado, o POST pode retornar erro de dependência; isso é separado dos testes do `pytest`, que verificam o código sem esses serviços.

## Banco de dados (opcional para abrir a documentação)

A API e sua documentação podem iniciar sem PostgreSQL. Para usar endpoints que leem ou gravam dados, instalar/abrir o Docker Desktop e executar o bloco abaixo em outro terminal. O Docker Compose v2 precisa estar disponível; confirme com `docker compose version` antes de continuar.

```bash
cd "$HOME/Documents/SUSANNA-HEALTHCHECK/susana-backend" || exit 1
source .venv/bin/activate
docker compose up -d postgres && alembic upgrade head
```

O bloco inicia PostgreSQL com pgvector em segundo plano e, se essa etapa terminar bem, aplica as migrations. A migration inicial usa embeddings `vector(768)`: a dimensão do modelo de embeddings e a variável `EMBEDDING_DIMENSIONS` em `.env` precisam ser compatíveis com esse valor antes de migrar. Se aparecer `docker: unknown command: docker compose`, instale ou atualize o Docker Desktop, abra-o e confirme que `docker compose version` funciona. Esse erro não é corrigido reinstalando os pacotes Python.

## Problemas comuns

- **`file:///Users/.../Documents does not appear to be a Python project`:** `pip install` foi executado em `Documents`. Entre em `susana-backend` e confirme com `pwd` e `ls` que `pyproject.toml` está na pasta atual.
- **`cp: .env.example: No such file or directory`:** o terminal não está na pasta do backend. Entre nela antes de executar `cp .env.example .env`.
- **`alembic`, `uvicorn`, `pytest` ou `sqlalchemy` não encontrado:** a instalação não terminou corretamente ou `.venv` não está ativo. Na pasta `susana-backend`, ative com `source .venv/bin/activate` e repita `pip install -e ".[dev]"`. Só continue quando o comando terminar sem erro.
- **Erro de conexão com PostgreSQL:** confirme que o Docker Desktop está em execução e rode `docker compose up -d postgres` dentro do backend.
- **`docker: unknown command: docker compose` ou `unknown shorthand flag: 'd' in -d`:** o Docker Compose v2 não está disponível no Docker CLI usado pelo terminal. Instale ou atualize o Docker Desktop para macOS, abra-o e espere iniciar. Depois confira `docker compose version`; só tente subir o banco quando esse comando mostrar a versão do Compose.
- **Porta `5432` ou `8000` ocupada:** outro processo está usando a porta. Encerre esse processo ou ajuste a configuração antes de iniciar o serviço novamente.

## Endpoints

### Health

```http
GET /api/v1/health
GET /api/v1/health/dependencies
```

### Chat

```http
POST /api/v1/chat
```

Exemplo de corpo para `POST /api/v1/chat`:

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

A integração usa a Action API documentada pelo CKAN:

- https://docs.ckan.org/en/latest/api/
- https://docs.ckan.org/en/latest/api/#api-guide

Os endereços `demo.ckan.org` encontrados em exemplos da documentação são apenas demonstrativos. Configure `CKAN_BASE_URL` em `.env` com o serviço CKAN que será realmente utilizado.

## Próximos passos

1. substituir o seed DEMO pelos primeiros dados oficiais do corpus;
2. definir o modelo de embeddings e confirmar sua dimensão;
3. ingerir documentos reais;
4. validar `/api/v1/rag/search` antes de ajustar o prompt;
5. integrar o React;
6. criar o conjunto de avaliação da Susana.
