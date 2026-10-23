#!/usr/bin/env bash
# =========================================================================
# Remove todos os recursos AWS com a tag Project=susana (us-east-1):
# instâncias EC2 (terminate + wait), Elastic IPs, key pairs e security groups.
# Uso:
#   bash scripts/teardown_aws.sh          # dry-run: só lista o que seria apagado
#   bash scripts/teardown_aws.sh --yes    # apaga de fato
# Variáveis: AWS_REGION (padrão us-east-1), TAG_KEY/TAG_VALUE (padrão Project/susana)
# =========================================================================

set -euo pipefail

REGION="${AWS_REGION:-us-east-1}"
TAG_KEY="${TAG_KEY:-Project}"
TAG_VALUE="${TAG_VALUE:-susana}"
CONFIRM=false
[ "${1:-}" = "--yes" ] && CONFIRM=true

command -v aws > /dev/null || { echo "[ERRO] aws CLI não encontrado."; exit 1; }
aws sts get-caller-identity --region "$REGION" --query Account --output text > /dev/null \
  || { echo "[ERRO] Credenciais AWS inválidas/ausentes."; exit 1; }

FILTER="Name=tag:${TAG_KEY},Values=${TAG_VALUE}"
AWS=(aws --region "$REGION" --output text)

echo "Região: ${REGION} | Tag: ${TAG_KEY}=${TAG_VALUE} | Modo: $([ "$CONFIRM" = true ] && echo 'APAGAR' || echo 'dry-run')"

INSTANCES=$("${AWS[@]}" ec2 describe-instances --filters "$FILTER" \
  "Name=instance-state-name,Values=pending,running,stopping,stopped,shutting-down" \
  --query 'Reservations[].Instances[].InstanceId')
EIPS=$("${AWS[@]}" ec2 describe-addresses --filters "$FILTER" --query 'Addresses[].AllocationId')
KEYS=$("${AWS[@]}" ec2 describe-key-pairs --filters "$FILTER" --query 'KeyPairs[].KeyName')
SGS=$("${AWS[@]}" ec2 describe-security-groups --filters "$FILTER" --query 'SecurityGroups[].GroupId')

echo "Instâncias:      ${INSTANCES:-<nenhuma>}"
echo "Elastic IPs:     ${EIPS:-<nenhum>}"
echo "Key pairs:       ${KEYS:-<nenhum>}"
echo "Security groups: ${SGS:-<nenhum>}"

if [ "$CONFIRM" != true ]; then
  echo
  echo "Dry-run: nada foi apagado. Rode novamente com --yes para apagar."
  exit 0
fi

if [ -n "$INSTANCES" ]; then
  echo "Terminando instâncias: $INSTANCES"
  # shellcheck disable=SC2086
  "${AWS[@]}" ec2 terminate-instances --instance-ids $INSTANCES > /dev/null
  # shellcheck disable=SC2086
  aws --region "$REGION" ec2 wait instance-terminated --instance-ids $INSTANCES
  echo "Instâncias terminadas."
fi

for alloc in $EIPS; do
  echo "Liberando Elastic IP: $alloc"
  ASSOC=$("${AWS[@]}" ec2 describe-addresses --allocation-ids "$alloc" --query 'Addresses[0].AssociationId')
  if [ -n "$ASSOC" ] && [ "$ASSOC" != "None" ]; then
    "${AWS[@]}" ec2 disassociate-address --association-id "$ASSOC" || true
  fi
  "${AWS[@]}" ec2 release-address --allocation-id "$alloc"
done

for key in $KEYS; do
  echo "Apagando key pair: $key"
  "${AWS[@]}" ec2 delete-key-pair --key-name "$key"
done

for sg in $SGS; do
  echo "Apagando security group: $sg"
  # As ENIs das instâncias podem demorar alguns segundos para sumir
  for attempt in 1 2 3 4 5 6; do
    if "${AWS[@]}" ec2 delete-security-group --group-id "$sg" 2> /dev/null; then break; fi
    [ "$attempt" = 6 ] && echo "[AVISO] Não foi possível apagar $sg (ainda em uso?)."
    sleep 10
  done
done

echo
echo "Recursos ainda marcados com ${TAG_KEY}=${TAG_VALUE} em ${REGION}:"
aws --region "$REGION" resourcegroupstaggingapi get-resources \
  --tag-filters "Key=${TAG_KEY},Values=${TAG_VALUE}" \
  --query 'ResourceTagMappingList[].ResourceARN' --output text || true
echo "(instâncias terminadas podem aparecer por até ~1h até a AWS removê-las da listagem)"
"${AWS[@]}" ec2 describe-instances --filters "$FILTER" \
  "Name=instance-state-name,Values=pending,running,stopping,stopped,shutting-down" \
  --query 'Reservations[].Instances[].[InstanceId,State.Name]' || true
