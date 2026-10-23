#!/usr/bin/env bash
# =========================================================================
# Provisionamento e deploy do SUSANNA numa EC2 (Ubuntu 24.04, x86_64)
# Stack: docker-compose.yml (backend FastAPI + Next.js + Caddy + Ollama CPU)
# Firewall: liberar 80/443 no Security Group (não mexemos em iptables).
# Uso: sudo bash scripts/deploy_aws.sh
# =========================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}===================================================================${NC}"
echo -e "${GREEN}   SUSANNA — Deploy na AWS EC2 (Ubuntu x86_64)                     ${NC}"
echo -e "${BLUE}===================================================================${NC}"

if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}[ERRO] Execute com sudo: sudo bash scripts/deploy_aws.sh${NC}"
  exit 1
fi

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

# 1. Pacotes base
echo -e "\n${YELLOW}[1/6] Atualizando pacotes do sistema...${NC}"
apt-get update -qq
apt-get install -y -qq curl git ca-certificates gnupg openssl

# 2. Docker Engine + Compose plugin
if ! command -v docker &> /dev/null || ! docker compose version &> /dev/null; then
  echo -e "\n${YELLOW}[2/6] Instalando Docker Engine e Compose Plugin...${NC}"
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor --yes -o /etc/apt/keyrings/docker.gpg
  chmod a+r /etc/apt/keyrings/docker.gpg
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    tee /etc/apt/sources.list.d/docker.list > /dev/null
  apt-get update -qq
  apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  systemctl enable --now docker
  if [ -n "${SUDO_USER:-}" ]; then usermod -aG docker "$SUDO_USER" || true; fi
else
  echo -e "\n${GREEN}[2/6] Docker e Compose já instalados.${NC}"
fi

# 3. Swap de 4 GB (8 GB de RAM é justo para LLM + embeddings + build)
echo -e "\n${YELLOW}[3/6] Verificando swap...${NC}"
if ! swapon --show=NAME --noheadings | grep -q .; then
  if [ ! -f /swapfile ]; then
    fallocate -l 4G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=4096
    chmod 600 /swapfile
    mkswap /swapfile > /dev/null
  fi
  swapon /swapfile
  grep -q '^/swapfile ' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
  echo -e "${GREEN}Swap de 4 GB ativo.${NC}"
else
  echo -e "${GREEN}Swap já ativo.${NC}"
fi

# 4. .env (gerado só se não existir; nunca imprimimos a chave)
echo -e "\n${YELLOW}[4/6] Configurando .env...${NC}"
imds_get() {
  local token
  token=$(curl -sf --max-time 3 -X PUT "http://169.254.169.254/latest/api/token" \
    -H "X-aws-ec2-metadata-token-ttl-seconds: 300") || return 1
  curl -sf --max-time 3 -H "X-aws-ec2-metadata-token: $token" "http://169.254.169.254/latest/meta-data/$1"
}

if [ ! -f .env ]; then
  if [ -z "${DOMAIN:-}" ]; then
    PUBLIC_IP=$(imds_get public-ipv4 || true)
    if [ -n "$PUBLIC_IP" ]; then
      DOMAIN="app.${PUBLIC_IP}.nip.io"
    else
      echo -e "${YELLOW}[AVISO] IP público não obtido via IMDSv2; DOMAIN vazio (Caddy em :80).${NC}"
      DOMAIN=""
    fi
  fi
  if [ -n "$DOMAIN" ]; then CORS="https://${DOMAIN}"; else CORS="*"; fi
  umask 077
  cat > .env <<ENVEOF
DOMAIN=${DOMAIN}
OLLAMA_MODEL=${OLLAMA_MODEL:-llama3.2:3b}
INGESTION_API_KEY=$(openssl rand -hex 32)
CORS_ORIGINS=${CORS}
LLM_TIMEOUT_S=${LLM_TIMEOUT_S:-120}
ENVEOF
  if [ -n "${SUDO_USER:-}" ]; then chown "$SUDO_USER" .env || true; fi
  echo -e "${GREEN}.env criado (DOMAIN=${DOMAIN:-<vazio>}; INGESTION_API_KEY aleatória).${NC}"
else
  echo -e "${GREEN}.env já existe — mantido.${NC}"
fi

# Lê do .env apenas o que o script precisa (sem 'source' para não exportar segredos)
env_val() { grep -E "^$1=" .env | tail -n1 | cut -d= -f2- || true; }
DOMAIN_ENV=$(env_val DOMAIN)
MODEL=$(env_val OLLAMA_MODEL)
MODEL=${MODEL:-llama3.2:3b}

# 5. Build e subida
echo -e "\n${YELLOW}[5/6] Build e subida dos contêineres...${NC}"
docker compose up -d --build

echo -e "\n${YELLOW}Baixando modelo ${MODEL} no Ollama (pode levar alguns minutos)...${NC}"
for _ in $(seq 1 30); do
  docker compose exec -T ollama ollama list > /dev/null 2>&1 && break
  sleep 2
done
docker compose exec -T ollama ollama pull "$MODEL"

# 6. Saúde
echo -e "\n${YELLOW}[6/6] Aguardando backend ficar healthy (até ~10 min)...${NC}"
STATUS=""
for _ in $(seq 1 60); do
  STATUS=$(docker inspect -f '{{.State.Health.Status}}' susana-backend 2>/dev/null || echo "unknown")
  [ "$STATUS" = "healthy" ] && break
  sleep 10
done
echo "backend: ${STATUS}"

# Verificação através do Caddy (porta 80; com DOMAIN o Caddy redireciona p/ HTTPS,
# então enviamos o Host correto e seguimos o redirect)
HEALTH_OK=false
for _ in $(seq 1 30); do
  if [ -n "$DOMAIN_ENV" ]; then
    OUT=$(curl -sk -L --max-time 10 -H "Host: ${DOMAIN_ENV}" http://localhost/health \
      --resolve "${DOMAIN_ENV}:443:127.0.0.1" || true)
  else
    OUT=$(curl -s --max-time 10 http://localhost/health || true)
  fi
  if echo "$OUT" | grep -q "ok"; then HEALTH_OK=true; break; fi
  sleep 5
done

docker compose ps

if [ "$HEALTH_OK" = true ]; then
  echo -e "\n${GREEN}===================================================================${NC}"
  echo -e "${GREEN}   DEPLOY CONCLUÍDO NA AWS EC2                                     ${NC}"
  echo -e "${GREEN}===================================================================${NC}"
  if [ -n "$DOMAIN_ENV" ]; then
    echo -e "App:     👉 ${BLUE}https://${DOMAIN_ENV}${NC}"
    echo -e "Swagger: 👉 ${BLUE}https://${DOMAIN_ENV}/docs${NC}"
  else
    echo -e "App: 👉 ${BLUE}http://<IP_PUBLICO>${NC}"
  fi
else
  echo -e "\n${YELLOW}[AVISO] /health via Caddy ainda não respondeu. Veja: docker compose logs -f${NC}"
  exit 1
fi
