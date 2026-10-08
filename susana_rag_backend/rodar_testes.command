#!/bin/zsh
# Roda os testes da Susana com saída detalhada (duplo clique no Finder também funciona)
cd "$(dirname "$0")"
clear
echo "=== Testes da Susana (pytest) ==="
echo
.venv/bin/pytest -v --color=yes -p no:cacheprovider -W ignore
echo
echo "Pressione Enter para fechar."
read
