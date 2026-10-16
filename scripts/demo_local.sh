#!/usr/bin/env bash
# =========================================================================
# Publica o SUSANNA rodando no seu Mac por um túnel HTTPS gratuito
# (Cloudflare Quick Tunnel). Serve para demonstração/apresentação.
#
#   bash scripts/demo_local.sh        # sobe tudo e mostra a URL pública
#   Ctrl+C                            # derruba tudo (backend, site e túnel)
#
# Pré-requisitos: Ollama aberto (modelo llama3.1), ambiente do backend em
# susana_rag_backend/.venv e o cloudflared em ~/tools/cloudflared/cloudflared.
# Limites: o Mac precisa ficar ligado e conectado; a URL muda a cada execução;
# qualquer pessoa com o link acessa. Sem garantia de disponibilidade.
# =========================================================================
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLOUDFLARED="${CLOUDFLARED:-$HOME/tools/cloudflared/cloudflared}"
SITE_PORT="${SITE_PORT:-3001}"
LOG="${TMPDIR:-/tmp}/susana-demo"
mkdir -p "$LOG"

die() { echo "ERRO: $*" >&2; exit 1; }
[ -x "$CLOUDFLARED" ] || die "cloudflared não encontrado em $CLOUDFLARED"
[ -x "$ROOT/susana_rag_backend/.venv/bin/uvicorn" ] || die "ambiente do backend não encontrado (.venv)"
curl -s -m 3 http://localhost:11434/api/tags >/dev/null || echo "AVISO: Ollama não respondeu; abra o app Ollama, senão o chat usa só os trechos oficiais."

PIDS=()
cleanup() { echo; echo "Encerrando..."; kill "${PIDS[@]}" 2>/dev/null; exit 0; }
trap cleanup INT TERM

# Libera as portas de execuções anteriores
pkill -f "uvicorn app.main:app" 2>/dev/null
pkill -f "cloudflared tunnel --no-autoupdate" 2>/dev/null
# O 'next start' deixa um processo filho (next-server) segurando a porta: mata quem estiver nela
for port in 8000 "$SITE_PORT"; do
  pids=$(lsof -ti "tcp:$port" -sTCP:LISTEN 2>/dev/null)
  [ -n "$pids" ] && kill $pids 2>/dev/null
done
sleep 2

# 1. Backend em modo produção (recusa a chave de ingestão padrão, que é pública no repositório)
cd "$ROOT/susana_rag_backend" || exit 1
ENVIRONMENT=production INGESTION_API_KEY="$(openssl rand -hex 24)" \
  ./.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 > "$LOG/backend.log" 2>&1 &
PIDS+=($!)
echo "Aguardando o backend (carrega os modelos, até ~1 min)..."
for _ in $(seq 1 90); do curl -s -m 2 http://localhost:8000/health | grep -q ok && break; sleep 2; done
curl -s -m 2 http://localhost:8000/health | grep -q ok || die "backend não subiu (veja $LOG/backend.log)"

# 2. Site compilado (build só se ainda não existir ou se FORCE_BUILD=1)
cd "$ROOT/susana-ui" || exit 1
if [ ! -f .next/BUILD_ID ] || [ "${FORCE_BUILD:-0}" = "1" ]; then
  echo "Compilando o site..."; npm run build > "$LOG/build.log" 2>&1 || die "build falhou (veja $LOG/build.log)"
fi
npm start -- -p "$SITE_PORT" > "$LOG/site.log" 2>&1 &
PIDS+=($!)
for _ in $(seq 1 30); do curl -s -m 2 -o /dev/null "http://localhost:$SITE_PORT/" && break; sleep 1; done

# 3. Túnel público com HTTPS
"$CLOUDFLARED" tunnel --no-autoupdate --url "http://localhost:$SITE_PORT" > "$LOG/tunnel.log" 2>&1 &
PIDS+=($!)
URL=""
for _ in $(seq 1 40); do
  URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' "$LOG/tunnel.log" | head -1)
  [ -n "$URL" ] && break; sleep 1
done
[ -n "$URL" ] || die "o túnel não abriu (veja $LOG/tunnel.log)"

# Mantém o Mac acordado enquanto o script roda
caffeinate -dims -w $$ &
PIDS+=($!)

echo "============================================================"
echo " SUSANNA no ar:  $URL"
echo " (Ctrl+C para encerrar. Logs em $LOG)"
echo "============================================================"
wait
