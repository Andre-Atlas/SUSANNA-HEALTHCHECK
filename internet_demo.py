"""Inicia um túnel temporário e servidor autenticado; Ctrl+C encerra ambos."""
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
from internet_state import state_dir


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--provider', choices=['cloudflare', 'ngrok'], default='cloudflare')
    args = parser.parse_args()
    provider = args.provider
    client = 'cloudflared'
    if provider == 'ngrok':
        client = 'ngrok'
        if not (state_dir() / 'ngrok.yml').exists():
            python = '.venv\\Scripts\\python.exe' if os.name == 'nt' else '.venv/bin/python'
            raise SystemExit(f'Primeiro execute: {python} configurar_ngrok.py')
    executable = shutil.which(client)
    if executable is None:
        filename = client + ('.exe' if os.name == 'nt' else '')
        candidate = ROOT / '.internet' / 'bin' / filename
        executable = str(candidate) if candidate.is_file() else None
    if executable is None:
        raise SystemExit('Instale o cliente do túnel antes de iniciar.')
    import socket
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 8010))
    from operations import inspect_database
    from server import ollama, MODEL
    inspect_database()
    if not any(m.get('name') == MODEL for m in ollama('/api/tags', timeout=5).get('models', [])):
        raise SystemExit('Abra o Ollama e instale o modelo antes de iniciar.')
    private = state_dir()
    # Impede duas sessões concorrentes e substituição acidental das credenciais.
    lock = private / 'session.lock'
    fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(fd)
    processes = []
    try:
        with (private / 'tunnel.log').open('w') as log:
            command = [executable, 'tunnel', '--url', 'http://127.0.0.1:8010',
                       '--no-autoupdate', '--protocol', 'http2']
            if provider == 'ngrok':
                command = [executable, 'http', 'http://127.0.0.1:8010',
                           '--config', str(private / 'ngrok.yml'), '--inspect=false',
                           '--log=stdout', '--log-format=json']
            tunnel = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
            processes.append(tunnel)
            origin = None
            for _ in range(90):
                if tunnel.poll() is not None:
                    raise RuntimeError('Túnel encerrou; confira .internet/tunnel.log.')
                logs = (private / 'tunnel.log').read_text()
                if provider == 'ngrok':
                    for line in logs.splitlines():
                        try:
                            entry = json.loads(line)
                        except ValueError:
                            continue
                        if entry.get('msg') == 'started tunnel' and entry.get('url', '').startswith('https://'):
                            origin = entry['url']
                    if origin:
                        break
                else:
                    match = re.search(r'https://[a-z0-9-]+\.trycloudflare\.com', logs)
                    if match and 'Registered tunnel connection' in logs:
                        origin = match.group()
                        break
                time.sleep(1)
            if not origin:
                raise RuntimeError('Túnel não conectou em 90 segundos. Confira a conexão de saída e .internet/tunnel.log.')
            config = private / 'access.json'
            config.write_text(json.dumps({'origin': origin, 'provider': provider, 'username': 'equipe', 'password': secrets.token_urlsafe(24)}, indent=2)+'\n')
            config.chmod(0o600)
            with (private / 'server.log').open('w') as server_log:
                server = subprocess.Popen([sys.executable, str(ROOT / 'internet_app.py'), '--config', str(config)],
                    cwd=ROOT, stdout=server_log, stderr=subprocess.STDOUT)
                processes.append(server)
                print(f'URL: {origin}\nUsuário: equipe\nSenha: consulte {config}\nCtrl+C encerra o acesso.', flush=True)
                while tunnel.poll() is None and server.poll() is None:
                    time.sleep(1)
                raise RuntimeError('Um serviço encerrou; confira os logs em .internet/.')
    finally:
        for process in reversed(processes):
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
        lock.unlink(missing_ok=True)


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    try:
        main()
    except KeyboardInterrupt:
        pass
