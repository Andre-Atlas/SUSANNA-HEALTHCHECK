#!/usr/bin/env bash
# =========================================================================
# Script de Provisionamento e Deploy Automatizado na Oracle Cloud (OCI)
# Sistema: Ubuntu 24.04 / 22.04 LTS (ARM64 Ampere A1 ou AMD64)
# Projeto: SUS Digital (Projeto Suzanna)
# =========================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}===================================================================${NC}"
echo -e "${GREEN}   SUS Digital (Projeto Suzanna) — Deploy na Oracle Cloud (OCI)   ${NC}"
echo -e "${BLUE}===================================================================${NC}"

# 1. Verificação de privilégios
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}[ERRO] Este script deve ser executado com permissões de root (sudo).${NC}"
  echo "Exemplo: sudo bash scripts/deploy_oci.sh"
  exit 1
fi

# 2. Atualização do Sistema
echo -e "\n${YELLOW}[1/5] Atualizando pacotes do sistema Ubuntu...${NC}"
apt-get update -qq
apt-get install -y -qq curl git iptables-persistent netfilter-persistent ca-certificates gnupg

# 3. Instalação do Docker e Docker Compose (se não instalados)
if ! command -v docker &> /dev/null; then
  echo -e "\n${YELLOW}[2/5] Instalando Docker Engine e Compose Plugin...${NC}"
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  chmod a+r /etc/apt/keyrings/docker.gpg

  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    tee /etc/apt/sources.list.d/docker.list > /dev/null

  apt-get update -qq
  apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  systemctl enable --now docker
  echo -e "${GREEN}Docker instalado com sucesso!${NC}"
else
  echo -e "\n${GREEN}[2/5] Docker já instalado no sistema.${NC}"
fi

# 4. Configuração Crítica do Firewall da Oracle Cloud
# Gotcha OCI: O Ubuntu na OCI possui regras iptables restritivas por padrão que bloqueiam 80 e 443
echo -e "\n${YELLOW}[3/5] Abrindo portas 80 (HTTP) e 443 (HTTPS) no firewall local...${NC}"
iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT 2>/dev/null || iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT 2>/dev/null || iptables -A INPUT -p tcp --dport 443 -j ACCEPT
netfilter-persistent save > /dev/null 2>&1 || true

if command -v ufw &> /dev/null; then
  ufw allow 80/tcp > /dev/null 2>&1 || true
  ufw allow 443/tcp > /dev/null 2>&1 || true
fi
echo -e "${GREEN}Portas 80 e 443 liberadas no firewall do host.${NC}"

# 5. Configuração de Variáveis de Ambiente e Domínio
echo -e "\n${YELLOW}[4/5] Configurando variáveis de ambiente...${NC}"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

if [ ! -f .env ]; then
  if [ -n "${DOMAIN:-}" ]; then
    echo "DOMAIN=${DOMAIN}" > .env
  else
    echo "# Configuração do Caddy (deixe vazio para rodar na porta 80 por IP)" > .env
    echo "DOMAIN=" >> .env
  fi
fi

# 6. Build e Inicialização dos Contêineres
echo -e "\n${YELLOW}[5/5] Compilando e iniciando contêineres com Docker Compose...${NC}"
docker compose down --remove-orphans || true
docker compose build
docker compose up -d

# 7. Verificação de Saúde
echo -e "\n${YELLOW}Aguardando inicialização dos serviços (15 segundos)...${NC}"
sleep 15

if curl -s http://localhost:8000/health | grep -q "ok"; then
  echo -e "\n${GREEN}===================================================================${NC}"
  echo -e "${GREEN}   DEPLOY CONCLUÍDO COM SUCESSO NA ORACLE CLOUD!                 ${NC}"
  echo -e "${GREEN}===================================================================${NC}"
  PUBLIC_IP=$(curl -s https://ifconfig.me || echo "SEU_IP_PUBLICO")
  echo -e "Acesse a aplicação no navegador em:"
  echo -e "👉 ${BLUE}http://${PUBLIC_IP}${NC} (ou no seu domínio configurado via HTTPS)"
  echo -e "API Swagger: 👉 ${BLUE}http://${PUBLIC_IP}/docs${NC}"
else
  echo -e "\n${YELLOW}[AVISO] Os contêineres estão subindo. Verifique os logs com:${NC}"
  echo -e "docker compose logs -f"
fi
