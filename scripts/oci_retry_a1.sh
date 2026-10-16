#!/usr/bin/env bash
# =========================================================================
# Cria a VM Always Free (Ampere A1, Ubuntu 24.04) no Oracle Cloud Shell,
# repetindo a tentativa até a Oracle liberar capacidade ("Out of host capacity").
#
#   DRY_RUN=1 bash oci_retry_a1.sh   # só confere rede, imagem e chave; não cria nada
#   bash oci_retry_a1.sh             # tenta a cada WAIT segundos até conseguir
#
# Pré-requisitos: rodar no OCI Cloud Shell (já autenticado, na região de São Paulo),
# ter uma sub-rede pública e a chave pública em ~/susana.pub.
# =========================================================================
set -u

NAME="${NAME:-susanna-sus-digital}"
SUBNET_NAME="${SUBNET_NAME:-susanna-subnet-publica}"
PUBKEY="${PUBKEY:-$HOME/susana.pub}"
BOOT_GB="${BOOT_GB:-100}"
SIZES="${SIZES:-2:12 1:6}"   # OCPUs:GB, tentados nesta ordem a cada rodada (teto Always Free: 2 OCPUs / 12 GB)
WAIT="${WAIT:-60}"

die() { echo "ERRO: $*" >&2; exit 1; }
ts() { date +%H:%M:%S; }

command -v oci >/dev/null 2>&1 || die "comando 'oci' não encontrado. Rode isto no Cloud Shell da Oracle."
[ -s "$PUBKEY" ] || die "chave pública não encontrada em $PUBKEY (veja o passo 2 do guia)."
grep -q '^ssh-' "$PUBKEY" || die "$PUBKEY não parece uma chave pública SSH (deve começar com 'ssh-rsa')."

TENANCY="${OCI_TENANCY:-$(awk -F= '/^tenancy/{gsub(/ /,"",$2); print $2; exit}' "$HOME/.oci/config" 2>/dev/null)}"
[ -n "$TENANCY" ] || die "não consegui descobrir o OCID da tenancy."
C="$TENANCY"   # compartimento raiz

AD=$(oci iam availability-domain list -c "$C" --query 'data[0].name' --raw-output) || die "falha ao listar domínios de disponibilidade."

# Pode haver sub-redes repetidas com o mesmo nome (cada tentativa do assistente cria uma rede).
# Escolhe a primeira que seja PÚBLICA e cuja VCN tenha Internet Gateway.
CANDIDATES=$(oci network subnet list -c "$C" --all \
  --query "data[?\"display-name\"=='$SUBNET_NAME'].id" --raw-output 2>/dev/null | grep -o 'ocid1\.subnet[A-Za-z0-9._-]*')
if [ -z "$CANDIDATES" ]; then
  echo "Sub-rede '$SUBNET_NAME' não encontrada. Sub-redes existentes:"
  oci network subnet list -c "$C" --all --query 'data[].{nome:"display-name",privada:"prohibit-public-ip-on-vnic"}' --output table
  die "crie a rede pelo 'VCN Wizard' (veja o guia) ou rode com SUBNET_NAME='nome-da-sua-subnet'."
fi

SUBNET=""
for cand in $CANDIDATES; do
  PRIVATE=$(oci network subnet get --subnet-id "$cand" --query 'data."prohibit-public-ip-on-vnic"' --raw-output)
  VCN=$(oci network subnet get --subnet-id "$cand" --query 'data."vcn-id"' --raw-output)
  IGW=$(oci network internet-gateway list -c "$C" --vcn-id "$VCN" --query 'length(data)' --raw-output)
  echo "candidata ${cand: -8}: privada=$PRIVATE, internet-gateways=$IGW"
  if [ "$PRIVATE" = "false" ] && [ "$IGW" != "0" ]; then SUBNET="$cand"; break; fi
done
[ -n "$SUBNET" ] || die "nenhuma sub-rede '$SUBNET_NAME' é pública e tem Internet Gateway. Verifique a rede no console (veja o guia)."

IMAGE=$(oci compute image list -c "$C" --operating-system "Canonical Ubuntu" --shape VM.Standard.A1.Flex \
  --sort-by TIMECREATED --sort-order DESC --all \
  --query "data[?contains(\"display-name\", '24.04') && contains(\"display-name\", 'aarch64')] | [0].\"display-name\"" --raw-output)
IMAGE_ID=$(oci compute image list -c "$C" --operating-system "Canonical Ubuntu" --shape VM.Standard.A1.Flex \
  --sort-by TIMECREATED --sort-order DESC --all \
  --query "data[?contains(\"display-name\", '24.04') && contains(\"display-name\", 'aarch64')] | [0].id" --raw-output)
{ [ -n "$IMAGE_ID" ] && [ "$IMAGE_ID" != "null" ]; } || die "imagem Ubuntu 24.04 aarch64 não encontrada."

echo "------------------------------------------------------------"
echo "Domínio de disponibilidade : $AD"
echo "Sub-rede pública           : $SUBNET_NAME"
echo "Imagem                     : $IMAGE"
echo "Tamanhos (OCPUs:GB)        : $SIZES"
echo "Disco de boot              : ${BOOT_GB} GB"
echo "Chave pública              : $PUBKEY"
echo "------------------------------------------------------------"
[ "${DRY_RUN:-0}" = "1" ] && { echo "DRY_RUN: tudo certo, nada foi criado."; exit 0; }

already_exists() {
  local n
  n=$(oci compute instance list -c "$C" --display-name "$NAME" \
        --query "data[?\"lifecycle-state\"!='TERMINATED' && \"lifecycle-state\"!='TERMINATING'] | length(@)" --raw-output 2>/dev/null)
  [ -n "$n" ] && [ "$n" != "0" ] && [ "$n" != "null" ]
}

round=0
while true; do
  already_exists && die "já existe uma instância '$NAME' (veja no console). Parando para não duplicar."
  round=$((round + 1))
  for size in $SIZES; do
    OC=${size%%:*}; GB=${size##*:}
    echo "[$(ts)] rodada $round: tentando ${OC} OCPU / ${GB} GB ..."
    OUT=$(oci compute instance launch \
      --availability-domain "$AD" --compartment-id "$C" \
      --display-name "$NAME" --shape VM.Standard.A1.Flex \
      --shape-config "{\"ocpus\":$OC,\"memoryInGBs\":$GB}" \
      --image-id "$IMAGE_ID" --subnet-id "$SUBNET" --assign-public-ip true \
      --boot-volume-size-in-gbs "$BOOT_GB" \
      --ssh-authorized-keys-file "$PUBKEY" 2>&1)
    INSTANCE=$(echo "$OUT" | grep -o 'ocid1\.instance[A-Za-z0-9._-]*' | head -1)
    if [ -n "$INSTANCE" ] && echo "$OUT" | grep -q '"lifecycle-state"'; then
      echo "[$(ts)] SUCESSO! Instância criada com ${OC} OCPU / ${GB} GB: $INSTANCE"
      [ "$OC" = "2" ] || echo "Lembrete: foi criada com tamanho menor; depois use 'More actions > Edit shape' para 2 OCPUs / 12 GB."
      echo "Aguardando o IP público ..."
      for _ in $(seq 1 30); do
        IP=$(oci compute instance list-vnics --instance-id "$INSTANCE" --query 'data[0]."public-ip"' --raw-output 2>/dev/null)
        if [ -n "$IP" ] && [ "$IP" != "null" ]; then
          echo "=============================================="
          echo " IP PÚBLICO: $IP     (usuário SSH: ubuntu)"
          echo "=============================================="
          exit 0
        fi
        sleep 10
      done
      echo "Instância criada, mas o IP ainda não apareceu. Veja a aba Networking da instância no console."
      exit 0
    elif echo "$OUT" | grep -qiE 'capacity|InternalError|TooManyRequests|"status": 429|"status": 500'; then
      echo "[$(ts)] sem capacidade agora; tentando de novo."
    else
      echo "[$(ts)] ERRO diferente de capacidade; parando para você ver:"
      echo "$OUT"
      exit 1
    fi
  done
  sleep "$WAIT"
done
