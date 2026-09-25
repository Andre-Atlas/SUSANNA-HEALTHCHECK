"""Salva o authtoken localmente, sem eco ou argumentos contendo o segredo."""
import getpass
import json
import os
from pathlib import Path
import sys

if __name__ == '__main__':
    if not sys.stdin.isatty():
        raise SystemExit('Execute diretamente no terminal do VS Code.')
    folder = Path(__file__).resolve().parent / '.internet'
    folder.mkdir(mode=0o700, exist_ok=True)
    folder.chmod(0o700)
    if (folder / 'session.lock').exists():
        raise SystemExit('Encerre a demonstração antes de configurar o token.')
    token = getpass.getpass('Cole o authtoken do ngrok e pressione Enter (não será exibido): ').strip()
    if not token or any(c.isspace() for c in token):
        raise SystemExit('Token vazio ou com espaços; copie somente o token do painel.')
    path = folder / 'ngrok.yml'
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as stream:
        stream.write('version: "2"\nauthtoken: ' + json.dumps(token) + '\nweb_addr: false\n')
    path.chmod(0o600)
    print('Token salvo na pasta privada. Inicie com:')
    print('.venv/bin/python internet_demo.py --provider ngrok')
