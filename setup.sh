#!/usr/bin/env bash
# ==============================================================================
# SUS Digital (Projeto SUSANNA) — Setup e Execução Universal Multiplataforma
# Compatível com: macOS (Apple Silicon / Intel), Linux (Ubuntu/Debian/Fedora/Arch)
#                 e Windows (WSL2 / Git Bash).
#
# Uso rápido:
#   bash setup.sh            # Instala dependências, ajusta ambientes e valida tudo
#   bash setup.sh --start    # Ajusta (se necessário) e sobe Backend (:8000) + Frontend (:3000)
#   bash setup.sh --prod     # Compila o Frontend e sobe Backend + Frontend em modo produção
#   bash setup.sh --docker   # Sobe toda a stack via Docker Compose
#   bash setup.sh --test     # Executa os 237 testes do Backend (pytest) + build do Frontend
#   bash setup.sh --stop     # Encerra serviços locais nas portas 8000/3000 e contêineres Docker
# ==============================================================================

set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/susana_rag_backend"
FRONTEND_DIR="$ROOT_DIR/susana-ui"
LOG_DIR="${TMPDIR:-/tmp}/susanna-runtime"
mkdir -p "$LOG_DIR"

API_PORT="${API_PORT:-8000}"
WEB_PORT="${WEB_PORT:-3000}"
SKIP_OLLAMA="${SKIP_OLLAMA:-0}"
FORCE_REINSTALL="${FORCE_REINSTALL:-0}"
ACTION="setup"

# Cores para terminal
if [ -t 1 ]; then
  RED='\033[0;31m'
  GREEN='\033[0;32m'
  YELLOW='\033[1;33m'
  BLUE='\033[0;34m'
  BOLD='\033[1m'
  NC='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; BLUE=''; BOLD=''; NC=''
fi

info()  { printf "${BLUE}[INFO]${NC} %s\n" "$*"; }
ok()    { printf "${GREEN}[OK]${NC}   %s\n" "$*"; }
warn()  { printf "${YELLOW}[AVISO]${NC} %s\n" "$*"; }
die()   { printf "${RED}[ERRO]${NC} %s\n" "$*" >&2; exit 1; }

usage() {
  cat <<EOF
${BOLD}SUS Digital (SUSANNA) — Script Unificado de Instalação e Execução${NC}

Uso:
  bash setup.sh [opção]

Opções principais:
  (sem argumentos)   Configura todo o sistema (Python .venv, .env, Guardrail, ChromaDB e npm install)
  --start, start     Configura (se necessário) e inicia Backend (:$API_PORT) + Frontend (:$WEB_PORT) em modo dev
  --prod, prod       Configura, compila o Frontend (build) e inicia em modo produção
  --docker, docker   Compila e sobe toda a stack em contêineres via Docker Compose
  --test, test       Executa a suíte de testes do Backend (pytest) e valida o build do Frontend
  --stop, stop       Encerra processos nas portas $API_PORT/$WEB_PORT e contêineres Docker
  --reinstall        Força a recriação do .venv e reinstalação dos pacotes
  --skip-ollama      Pula a verificação/download do modelo no Ollama
  -h, --help         Exibe esta ajuda

Variáveis de ambiente opcionais:
  API_PORT=8000      Porta do Backend FastAPI (padrão: 8000)
  WEB_PORT=3000      Porta do Frontend Next.js (padrão: 3000)
  PYTHON_BIN=...     Caminho explícito para o executável Python 3
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --start|start|--dev|dev) ACTION="start" ;;
    --prod|prod)             ACTION="prod" ;;
    --docker|docker)         ACTION="docker" ;;
    --test|test)             ACTION="test" ;;
    --stop|stop)             ACTION="stop" ;;
    --reinstall)             FORCE_REINSTALL="1" ;;
    --skip-ollama)           SKIP_OLLAMA="1" ;;
    -h|--help|help)          usage; exit 0 ;;
    *)                       die "Opção desconhecida: $1 (use --help para ver as opções)" ;;
  esac
  shift
done

# ------------------------------------------------------------------------------
# 1. Enriquecimento multiplataforma do PATH (Homebrew, ~/.local/bin, nvm, fnm, volta, asdf, mise, pyenv)
# ------------------------------------------------------------------------------
enrich_path() {
  local extra_paths=(
    "$HOME/.local/bin"
    "/opt/homebrew/bin"
    "/opt/homebrew/sbin"
    "/usr/local/bin"
    "$HOME/.volta/bin"
    "$HOME/.asdf/shims"
    "$HOME/.local/share/mise/shims"
    "$HOME/.pyenv/shims"
    "$HOME/.fnm/current/bin"
    "$HOME/.local/share/fnm/aliases/default/bin"
    "$HOME/Library/Application Support/fnm/aliases/default/bin"
    "/Applications/Ollama.app/Contents/Resources"
  )

  # Detecta versão mais recente do Node no ~/.nvm se existir
  if [ -d "$HOME/.nvm/versions/node" ]; then
    local latest_nvm
    latest_nvm="$(ls -1d "$HOME/.nvm/versions/node"/* 2>/dev/null | sort -V | tail -n 1 || true)"
    if [ -n "$latest_nvm" ] && [ -d "$latest_nvm/bin" ]; then
      extra_paths=("$latest_nvm/bin" "${extra_paths[@]}")
    fi
  fi

  local p
  for p in "${extra_paths[@]}"; do
    if [ -d "$p" ]; then
      case ":$PATH:" in
        *":$p:"*) ;;
        *) PATH="$p:$PATH" ;;
      esac
    fi
  done
  export PATH
}

enrich_path

# ------------------------------------------------------------------------------
# 2. Utilitários de gerenciamento de portas e processos (macOS / Linux / WSL)
# ------------------------------------------------------------------------------
free_port() {
  local port="$1"
  local pids=""
  if command -v lsof >/dev/null 2>&1; then
    pids="$(lsof -ti "tcp:$port" -sTCP:LISTEN 2>/dev/null || true)"
  elif command -v fuser >/dev/null 2>&1; then
    pids="$(fuser "${port}/tcp" 2>/dev/null || true)"
  elif command -v ss >/dev/null 2>&1; then
    pids="$(ss -lptn "sport = :$port" 2>/dev/null | grep -o 'pid=[0-9]*' | cut -d= -f2 | sort -u || true)"
  fi
  if [ -n "$pids" ]; then
    info "Liberando porta $port (PIDs: $(echo $pids | tr '\n' ' '))..."
    # shellcheck disable=SC2086
    kill $pids 2>/dev/null || true
    sleep 1
    # shellcheck disable=SC2086
    kill -9 $pids 2>/dev/null || true
  fi
}

stop_all() {
  info "Encerrando processos locais da SUSANNA..."
  pkill -f "uvicorn app.main:app" 2>/dev/null || true
  free_port "$API_PORT"
  free_port "$WEB_PORT"
  free_port 3001
  if command -v docker >/dev/null 2>&1 && [ -f "$ROOT_DIR/docker-compose.yml" ]; then
    if docker compose ps --services --filter "status=running" 2>/dev/null | grep -q .; then
      info "Parando contêineres Docker..."
      (cd "$ROOT_DIR" && docker compose down) || true
    fi
  fi
  ok "Serviços encerrados."
}

if [ "$ACTION" = "stop" ]; then
  stop_all
  exit 0
fi

# ------------------------------------------------------------------------------
# 3. Modo Docker Compose
# ------------------------------------------------------------------------------
run_docker() {
  command -v docker >/dev/null 2>&1 || die "Docker não encontrado. Instale o Docker Desktop / Docker Engine ou use 'bash setup.sh --start'."
  info "Subindo stack completa via Docker Compose..."
  cd "$ROOT_DIR" || exit 1
  if [ ! -f "$ROOT_DIR/.env" ]; then
    printf "DOMAIN=\nAPI_PORT=%s\nWEB_PORT=%s\n" "$API_PORT" "$WEB_PORT" > "$ROOT_DIR/.env"
  fi
  docker compose up --build -d || die "Falha ao subir contêineres com Docker Compose."

  info "Aguardando healthcheck do Backend (http://localhost:$API_PORT/health)..."
  local ready=0
  for _ in $(seq 1 60); do
    if curl -fsS -m 2 "http://localhost:$API_PORT/health" 2>/dev/null | grep -q '"ok"'; then
      ready=1
      break
    fi
    sleep 2
  done
  [ "$ready" -eq 1 ] || warn "O Backend ainda está inicializando. Acompanhe com: docker compose logs -f"

  printf "\n${GREEN}======================================================================${NC}\n"
  printf "${BOLD} SUSANNA (Docker) em execução!${NC}\n"
  printf "  - Frontend Web (Proxy): ${BLUE}http://localhost${NC} (ou ${BLUE}http://localhost:%s${NC})\n" "$WEB_PORT"
  printf "  - Backend API:          ${BLUE}http://localhost:%s${NC}\n" "$API_PORT"
  printf "  - Swagger Docs:         ${BLUE}http://localhost:%s/docs${NC}\n" "$API_PORT"
  printf "  - Parar serviços:       ${YELLOW}bash setup.sh --stop${NC}\n"
  printf "${GREEN}======================================================================${NC}\n"
}

if [ "$ACTION" = "docker" ]; then
  run_docker
  exit 0
fi

# ------------------------------------------------------------------------------
# 4. Detecção inteligente de Python (evita stubs quebrados do Xcode e prioriza wheels pré-compiladas)
# ------------------------------------------------------------------------------
venv_python_path() {
  if [ -x "$BACKEND_DIR/.venv/bin/python" ]; then
    echo "$BACKEND_DIR/.venv/bin/python"
  elif [ -x "$BACKEND_DIR/.venv/Scripts/python.exe" ]; then
    echo "$BACKEND_DIR/.venv/Scripts/python.exe"
  else
    echo ""
  fi
}

check_venv_healthy() {
  local vpy
  vpy="$(venv_python_path)"
  [ -n "$vpy" ] || return 1
  "$vpy" -W ignore -c "import fastapi, uvicorn, pydantic_settings, chromadb, sentence_transformers, mlflow, pytest, httpx" >/dev/null 2>&1
}

find_system_python() {
  local candidates=()
  [ -n "${PYTHON_BIN:-}" ] && candidates+=("$PYTHON_BIN")
  candidates+=(
    "/opt/homebrew/bin/python3.12"
    "/opt/homebrew/bin/python3.11"
    "/opt/homebrew/bin/python3.10"
    "/opt/homebrew/bin/python3.13"
    "/opt/homebrew/bin/python3"
    "/usr/local/bin/python3.12"
    "/usr/local/bin/python3.11"
    "/usr/local/bin/python3.10"
    "/usr/local/bin/python3.13"
    "python3.12"
    "python3.11"
    "python3.10"
    "python3.13"
    "/Library/Developer/CommandLineTools/usr/bin/python3"
    "/usr/local/bin/python3"
    "python3"
    "python"
  )

  local cand resolved
  for cand in "${candidates[@]}"; do
    if command -v "$cand" >/dev/null 2>&1; then
      resolved="$(command -v "$cand")"
    elif [ -x "$cand" ]; then
      resolved="$cand"
    else
      continue
    fi
    if "$resolved" -c 'import sys, venv; assert sys.version_info >= (3, 9)' >/dev/null 2>&1; then
      echo "$resolved"
      return 0
    fi
  done
  return 1
}

# ------------------------------------------------------------------------------
# 5. Setup e Validação do Backend (Python .venv, .env, Guardrail e ChromaDB)
# ------------------------------------------------------------------------------
setup_backend() {
  printf "\n${BOLD}[1/4] Configurando Backend (FastAPI + RAG + Guardrails)...${NC}\n"
  cd "$BACKEND_DIR" || die "Diretório $BACKEND_DIR não encontrado."

  if [ "$FORCE_REINSTALL" = "1" ] && [ -d "$BACKEND_DIR/.venv" ]; then
    info "Removendo .venv anterior (--reinstall)..."
    rm -rf "$BACKEND_DIR/.venv"
  fi

  if check_venv_healthy; then
    local vpy
    vpy="$(venv_python_path)"
    ok "Ambiente virtual Python (.venv) já está íntegro ($("$vpy" --version 2>&1))."
  else
    local sys_py
    sys_py="$(find_system_python || true)"
    [ -n "$sys_py" ] || die "Python 3.9+ não encontrado. Instale Python 3.11+ (ex: 'brew install python@3.11' ou 'sudo apt install python3 python3-venv')."
    info "Criando ambiente virtual em susana_rag_backend/.venv usando $sys_py ($("$sys_py" --version 2>&1))..."
    rm -rf "$BACKEND_DIR/.venv"
    "$sys_py" -m venv "$BACKEND_DIR/.venv" || die "Falha ao criar .venv. Em Ubuntu/Debian, instale: sudo apt install python3-venv"

    local vpy
    vpy="$(venv_python_path)"
    [ -n "$vpy" ] || die "Executável Python não encontrado dentro de .venv."

    info "Instalando dependências do Backend (requirements.txt)..."
    "$vpy" -m pip install --upgrade pip setuptools wheel >/dev/null
    "$vpy" -m pip install -r "$BACKEND_DIR/requirements.txt" || die "Falha ao instalar requirements.txt."
    ok "Dependências Python instaladas com sucesso."
  fi

  # Arquivo .env
  if [ ! -f "$BACKEND_DIR/.env" ]; then
    cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
    ok "Arquivo susana_rag_backend/.env criado a partir de .env.example."
  else
    ok "Arquivo susana_rag_backend/.env presente."
  fi

  # Validação do modelo de Guardrail (re-treina automaticamente se incompatível com a versão do scikit-learn local)
  local vpy
  vpy="$(venv_python_path)"
  if ! "$vpy" -W ignore -c "
import pathlib, joblib
p = pathlib.Path('data/guardrail_model.pkl')
assert p.exists(), 'missing'
m = joblib.load(p)
m.predict_proba(['Qual o horário da UBS 1 da Asa Sul?'])
" >/dev/null 2>&1; then
    info "Ajustando artefato data/guardrail_model.pkl para a versão local do scikit-learn..."
    "$vpy" -W ignore -m ml.guardrails.train || warn "Não foi possível retreinar o guardrail ML; o sistema usará fallback Regex."
  else
    ok "Modelo clínico Guardrail (data/guardrail_model.pkl) validado."
  fi

  # Validação de diretórios de dados e índice ChromaDB
  mkdir -p "$BACKEND_DIR/data/chroma_db" "$BACKEND_DIR/data/corpus" "$BACKEND_DIR/mlruns"
  ok "Diretórios de dados e persistência prontos."
}

# ------------------------------------------------------------------------------
# 6. Setup e Validação do Frontend (Node.js + Next.js 16)
# ------------------------------------------------------------------------------
setup_frontend() {
  printf "\n${BOLD}[2/4] Configurando Frontend (Next.js 16 + React 19)...${NC}\n"
  cd "$FRONTEND_DIR" || die "Diretório $FRONTEND_DIR não encontrado."

  command -v node >/dev/null 2>&1 || die "Node.js não encontrado no PATH. Instale Node.js 20+ (https://nodejs.org ou via brew/apt/nvm)."
  command -v npm  >/dev/null 2>&1 || die "npm não encontrado no PATH."

  local node_ver
  node_ver="$(node -v 2>/dev/null || echo "desconhecida")"
  info "Node.js detectado: $node_ver ($(command -v node))"

  if [ "$FORCE_REINSTALL" = "1" ] || [ ! -d "$FRONTEND_DIR/node_modules" ] || [ ! -x "$FRONTEND_DIR/node_modules/.bin/next" ]; then
    info "Instalando dependências do Frontend (npm install)..."
    npm install --no-audit --no-fund || die "Falha ao executar 'npm install' em susana-ui."
    ok "Dependências do Frontend instaladas."
  else
    ok "Dependências do Frontend (node_modules) já instaladas."
  fi
}

# ------------------------------------------------------------------------------
# 7. Verificação Opcional do Ollama (LLM Local)
# ------------------------------------------------------------------------------
setup_ollama() {
  printf "\n${BOLD}[3/4] Verificando LLM Local (Ollama — opcional)...${NC}\n"
  if [ "$SKIP_OLLAMA" = "1" ]; then
    info "Verificação do Ollama ignorada (--skip-ollama)."
    return 0
  fi

  local model_name="llama3.1:8b"
  if [ -f "$BACKEND_DIR/.env" ]; then
    local env_model
    env_model="$(grep -E '^OLLAMA_MODEL=' "$BACKEND_DIR/.env" 2>/dev/null | head -n 1 | cut -d= -f2- | tr -d ' "\r' || true)"
    [ -n "$env_model" ] && model_name="$env_model"
  fi

  if ! command -v ollama >/dev/null 2>&1; then
    warn "Ollama não está instalado nesta máquina."
    info "O sistema funciona normalmente sem Ollama (usando recuperação determinística oficial da SES-DF)."
    info "Para habilitar geração com LLM local futuramente, instale em https://ollama.com e rode: ollama pull $model_name"
    return 0
  fi

  if ! curl -fsS -m 2 http://localhost:11434/api/tags >/dev/null 2>&1; then
    info "Iniciando servidor Ollama em segundo plano..."
    nohup ollama serve >"$LOG_DIR/ollama.log" 2>&1 &
    for _ in $(seq 1 15); do
      curl -fsS -m 2 http://localhost:11434/api/tags >/dev/null 2>&1 && break
      sleep 1
    done
  fi

  if curl -fsS -m 2 http://localhost:11434/api/tags >/dev/null 2>&1; then
    if ollama list 2>/dev/null | awk '{print $1}' | grep -q "^${model_name}$"; then
      ok "Ollama ativo e modelo '$model_name' disponível."
    else
      info "Ollama ativo, mas modelo '$model_name' não encontrado localmente. Baixando (pode levar alguns minutos)..."
      ollama pull "$model_name" || warn "Não foi possível baixar '$model_name' agora; o chat usará o modo determinístico oficial."
    fi
  else
    warn "Servidor Ollama não respondeu em localhost:11434. O chat funcionará com os trechos oficiais da SES-DF."
  fi
}

# ------------------------------------------------------------------------------
# 8. Execução de Testes (--test)
# ------------------------------------------------------------------------------
run_tests() {
  printf "\n${BOLD}[4/4] Executando Suíte de Testes e Validação de Build...${NC}\n"
  local vpy
  vpy="$(venv_python_path)"

  info "Executando suíte pytest no Backend..."
  (cd "$BACKEND_DIR" && "$vpy" -W ignore -m pytest tests/ -q) || die "Falha nos testes do Backend."
  ok "Suíte de testes do Backend aprovada."

  info "Validando compilação de produção do Frontend (npm run build)..."
  (cd "$FRONTEND_DIR" && npm run build) || die "Falha no build do Frontend."
  ok "Build de produção do Frontend aprovado."
}

# ------------------------------------------------------------------------------
# 9. Inicialização Integrada de Backend + Frontend (--start / --prod)
# ------------------------------------------------------------------------------
start_services() {
  local mode="$1" # start (dev) | prod
  printf "\n${BOLD}[4/4] Iniciando Serviços SUSANNA (modo: %s)...${NC}\n" "$mode"

  free_port "$API_PORT"
  free_port "$WEB_PORT"

  local vpy
  vpy="$(venv_python_path)"
  local pids=()

  cleanup_services() {
    printf "\n"
    info "Encerrando serviços SUSANNA..."
    if [ "${#pids[@]}" -gt 0 ]; then
      kill "${pids[@]}" 2>/dev/null || true
    fi
    free_port "$API_PORT"
    free_port "$WEB_PORT"
    exit 0
  }
  trap cleanup_services INT TERM

  # 1. Inicia Backend FastAPI
  info "Iniciando Backend FastAPI na porta $API_PORT (log: $LOG_DIR/backend.log)..."
  (
    cd "$BACKEND_DIR" || exit 1
    exec "$vpy" -m uvicorn app.main:app --host 0.0.0.0 --port "$API_PORT"
  ) >"$LOG_DIR/backend.log" 2>&1 &
  pids+=($!)

  info "Aguardando inicialização do pipeline RAG e modelos..."
  local backend_ok=0
  for _ in $(seq 1 90); do
    if curl -fsS -m 2 "http://127.0.0.1:$API_PORT/health" 2>/dev/null | grep -q '"ok"'; then
      backend_ok=1
      break
    fi
    sleep 1
  done
  [ "$backend_ok" -eq 1 ] || die "O Backend não respondeu a tempo. Verifique o log em: $LOG_DIR/backend.log"
  ok "Backend online em http://localhost:$API_PORT"

  # 2. Inicia Frontend Next.js
  if [ "$mode" = "prod" ]; then
    if [ ! -f "$FRONTEND_DIR/.next/BUILD_ID" ] || [ "$FORCE_REINSTALL" = "1" ]; then
      info "Compilando Frontend para produção (npm run build)..."
      (cd "$FRONTEND_DIR" && BACKEND_URL="http://127.0.0.1:$API_PORT" npm run build >"$LOG_DIR/frontend_build.log" 2>&1) \
        || die "Falha ao compilar Frontend (veja $LOG_DIR/frontend_build.log)"
    fi
    info "Iniciando Frontend em modo produção na porta $WEB_PORT..."
    (
      cd "$FRONTEND_DIR" || exit 1
      exec env BACKEND_URL="http://127.0.0.1:$API_PORT" npm run start -- -p "$WEB_PORT"
    ) >"$LOG_DIR/frontend.log" 2>&1 &
    pids+=($!)
  else
    info "Iniciando Frontend em modo desenvolvimento na porta $WEB_PORT..."
    (
      cd "$FRONTEND_DIR" || exit 1
      exec env BACKEND_URL="http://127.0.0.1:$API_PORT" npm run dev -- -p "$WEB_PORT"
    ) >"$LOG_DIR/frontend.log" 2>&1 &
    pids+=($!)
  fi

  local frontend_ok=0
  for _ in $(seq 1 45); do
    if curl -fsS -m 2 -o /dev/null "http://127.0.0.1:$WEB_PORT/" 2>/dev/null; then
      frontend_ok=1
      break
    fi
    sleep 1
  done
  [ "$frontend_ok" -eq 1 ] || die "O Frontend não respondeu a tempo. Verifique o log em: $LOG_DIR/frontend.log"
  ok "Frontend online em http://localhost:$WEB_PORT"

  printf "\n${GREEN}======================================================================${NC}\n"
  printf "${BOLD} 💙 SUS Digital (SUSANNA) está no ar!${NC}\n"
  printf "  - Interface Web:        ${BLUE}http://localhost:%s${NC}\n" "$WEB_PORT"
  printf "  - API FastAPI:          ${BLUE}http://localhost:%s${NC}\n" "$API_PORT"
  printf "  - Documentação Swagger: ${BLUE}http://localhost:%s/docs${NC}\n" "$API_PORT"
  printf "  - Healthcheck:          ${BLUE}http://localhost:%s/health${NC}\n" "$API_PORT"
  printf "  - Logs em tempo real:   ${YELLOW}%s/${NC}\n" "$LOG_DIR"
  printf "${GREEN}======================================================================${NC}\n"
  printf "Pressione ${BOLD}Ctrl+C${NC} para encerrar todos os serviços.\n\n"
  wait
}

# ------------------------------------------------------------------------------
# Fluxo Principal
# ------------------------------------------------------------------------------
setup_backend
setup_frontend
setup_ollama

case "$ACTION" in
  setup)
    printf "\n${BOLD}[4/4] Ambiente configurado e pronto para uso!${NC}\n"
    printf "\n${GREEN}======================================================================${NC}\n"
    printf "${BOLD} Próximos comandos:${NC}\n"
    printf "  - Subir o sistema inteiro: ${BLUE}bash setup.sh --start${NC}\n"
    printf "  - Rodar os testes e build: ${BLUE}bash setup.sh --test${NC}\n"
    printf "  - Subir via Docker:        ${BLUE}bash setup.sh --docker${NC}\n"
    printf "${GREEN}======================================================================${NC}\n"
    ;;
  test)
    run_tests
    ;;
  start)
    start_services "start"
    ;;
  prod)
    start_services "prod"
    ;;
esac
