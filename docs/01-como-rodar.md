# 1. Como rodar o projeto

O sistema tem três processos que precisam estar no ar ao mesmo tempo:

| Processo | Porta | Função |
| --- | --- | --- |
| **Ollama** | 11434 | Servidor do LLM local (gera o texto das respostas) |
| **Backend FastAPI** | 8000 | Guardrail, busca vetorial e orquestração |
| **Frontend Next.js** | 3000 | Tela do chat no navegador |

## Pré-requisitos

| Ferramenta | Versão usada | Observação |
| --- | --- | --- |
| Python | 3.14 | 3.11+ deve funcionar |
| Node.js | 24 LTS | Necessário para o Next.js 16 |
| Ollama | qualquer recente | https://ollama.com |
| Espaço em disco | ~6 GB | Principalmente o modelo `llama3.1:8b` (4,9 GB) |

Se o Homebrew não tiver permissão de escrita na máquina (comum em máquinas compartilhadas), dá para instalar o Node sem `sudo`, baixando o binário oficial:

```bash
mkdir -p ~/.local && cd ~/.local
curl -sL https://nodejs.org/dist/v24.21.0/node-v24.21.0-darwin-arm64.tar.gz | tar xz
ln -sfn ~/.local/node-v24.21.0-darwin-arm64 ~/.local/node
export PATH=~/.local/node/bin:$PATH   # coloque no ~/.zshrc para ficar permanente
```

## Passo 1 — Ollama e o modelo

```bash
ollama serve            # se ainda não estiver rodando como serviço
ollama pull llama3.1:8b # modelo padrão do projeto
```

Para usar outro modelo (ex.: `qwen2.5:3b`, mais leve), defina `OLLAMA_MODEL` no `.env` do backend (veja abaixo).

## Passo 2 — Backend

```bash
cd susana_rag_backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# (opcional) configurações
cp .env.example .env

# Treinar e registrar o guardrail de ML no MLflow (só na primeira vez)
.venv/bin/python -m ml.guardrails.train

# Subir a API
.venv/bin/uvicorn app.main:app --port 8000
```

O startup demora de 10 a 30 segundos. Ele baixa o modelo de embeddings do HuggingFace na primeira vez, indexa o corpus e "aquece" o LLM. Ele termina quando aparece:

```text
Pipeline pronto. 27 docs na coleção.
INFO:     Application startup complete.
```

Verificação:

```bash
curl localhost:8000/health
# {"status":"ok","pipeline_ready":true}

curl localhost:8000/health/dependencies   # LLM pronto? quantos blocos indexados? guardrail carregado?
```

> Sem o passo do `ml.guardrails.train`, o backend sobe normalmente e registra no log
> `Falha ao carregar modelo ML (usando só regras)`. As regras continuam bloqueando; o modelo
> só acrescenta proteção. O treino só promove o modelo se ele passar no gate de qualidade
> (veja [05-guardrails.md](05-guardrails.md)), e nesse caso retorna código de saída 0.

## Passo 3 — Frontend

```bash
cd susana-ui
npm ci
npm run dev
```

Abra http://localhost:3000.

## Variáveis de ambiente do backend

Lidas de `susana_rag_backend/.env` por [config.py](../susana_rag_backend/app/config.py). Uma variável de ambiente do shell tem prioridade sobre o `.env`.

| Variável | Padrão | Para que serve |
| --- | --- | --- |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Onde está o Ollama |
| `OLLAMA_MODEL` | `llama3.1:8b` | Qual LLM usar |
| `LLM_TIMEOUT_S` | `12` | Tempo máximo esperando o Ollama (segundos) |
| `LLM_KEEP_ALIVE` | `30m` | Quanto tempo o Ollama mantém o modelo na memória |
| `LLM_NUM_PREDICT` | `350` | Máximo de tokens gerados por resposta |
| `EMBEDDING_MODEL` | `paraphrase-multilingual-MiniLM-L12-v2` | Modelo que transforma texto em vetor |
| `SIMILARITY_THRESHOLD` | `0.74` | Distância máxima (do trecho mais próximo entre os 3) para considerar a busca relevante (calibrada por `ml/retrieval/calibrate_threshold.py`) |
| `EMBEDDING_MAX_SEQ_LENGTH` | `256` | Tokens lidos por bloco pelo modelo de embeddings (padrão do modelo: 128) |
| `TOP_K` | `3` | Quantos trechos a busca entrega ao LLM |
| `GUARDRAIL_MODEL_URI` | `models:/susana-guardrail@champion` | Qual versão do guardrail carregar do MLflow |
| `GUARDRAIL_ENABLED_ML` | `true` | `false` usa só as regras (o ML deixa de acrescentar bloqueios) |
| `GUARDRAIL_THRESHOLD` | `0.4` | p(clínica) a partir da qual o ML bloqueia |
| `MLFLOW_TRACKING_URI` | `sqlite:///.../mlflow.db` | Onde o MLflow guarda os registros |
| `MLFLOW_LOG_REQUESTS` | `true` | Registrar cada pergunta no MLflow (as duas rotas) |
| `MLFLOW_LOG_QUERY_TEXT` | `false` | `true` grava o texto da pergunta; o padrão grava só hash e tamanho (LGPD) |

## Comandos úteis

```bash
# Testes do backend (precisa do Ollama no ar; os testes sobem a API sozinhos)
cd susana_rag_backend && .venv/bin/pytest -q

# Interface do MLflow (experimentos e modelos registrados)
# porta 5001 porque a 5000 é usada pelo AirPlay do macOS
cd susana_rag_backend && .venv/bin/mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5001
# → http://localhost:5001

# Testes com saída detalhada numa janela própria do Terminal (ou duplo clique no Finder)
open susana_rag_backend/rodar_testes.command

# Testar o chat sem o frontend
curl -N -X POST localhost:8000/api/chat/stream \
  -H 'Content-Type: application/json' \
  -d '{"message":"Qual o telefone do SAMU?"}'

# Parar tudo
pkill -f "next dev"; pkill -f uvicorn
```

## Arquivos gerados em tempo de execução (não vão para o git)

| Caminho | O que é |
| --- | --- |
| `susana_rag_backend/.venv/` | Ambiente virtual Python |
| `susana_rag_backend/data/chroma_db/` | Banco vetorial persistido |
| `susana_rag_backend/mlflow.db` | Banco SQLite do MLflow (experimentos, registro de modelos) |
| `susana_rag_backend/mlruns/` | Artefatos do MLflow (o modelo do guardrail serializado fica aqui) |
| `susana-ui/node_modules/`, `susana-ui/.next/` | Dependências e build do frontend |
