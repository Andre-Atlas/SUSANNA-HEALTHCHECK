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


def main():
    executable = shutil.which('cloudflared') or str(ROOT / '.internet/bin/cloudflared')
    if not Path(executable).is_file():
        raise SystemExit('Instale cloudflared antes de iniciar.')
    import socket
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 8010))
    from operations import inspect_database
    from server import ollama, MODEL
    inspect_database()
    if not any(m.get('name') == MODEL for m in ollama('/api/tags', timeout=5).get('models', [])):
        raise SystemExit('Abra o Ollama e instale o modelo antes de iniciar.')
    private = ROOT / '.internet'
    private.mkdir(mode=0o700, exist_ok=True)
    private.chmod(0o700)
    # Impede duas sessões concorrentes e substituição acidental das credenciais.
    lock = private / 'session.lock'
    fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(fd)
    processes = []
    try:
        with (private / 'tunnel.log').open('w') as log:
            tunnel = subprocess.Popen([executable, 'tunnel', '--url', 'http://127.0.0.1:8010',
                '--no-autoupdate', '--protocol', 'http2'], stdout=log, stderr=subprocess.STDOUT)
            processes.append(tunnel)
            origin = None
            for _ in range(90):
                if tunnel.poll() is not None:
                    raise RuntimeError('Túnel encerrou; confira .internet/tunnel.log.')
                logs = (private / 'tunnel.log').read_text()
                match = re.search(r'https://[a-z0-9-]+\.trycloudflare\.com', logs)
                if match and 'Registered tunnel connection' in logs:
                    origin = match.group()
                    break
                time.sleep(1)
            if not origin:
                raise RuntimeError('Túnel não conectou em 90 segundos. Confira a saída TCP 7844 e .internet/tunnel.log.')
            config = private / 'access.json'
            config.write_text(json.dumps({'origin': origin, 'username': 'equipe', 'password': secrets.token_urlsafe(24)}, indent=2)+'\n')
            config.chmod(0o600)
            with (private / 'server.log').open('w') as server_log:
                server = subprocess.Popen([sys.executable, str(ROOT / 'internet_app.py'), '--config', str(config)],
                    cwd=ROOT, stdout=server_log, stderr=subprocess.STDOUT)
                processes.append(server)
                print(f'URL: {origin}\nUsuário: equipe\nSenha: consulte .internet/access.json\nCtrl+C encerra o acesso.', flush=True)
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
