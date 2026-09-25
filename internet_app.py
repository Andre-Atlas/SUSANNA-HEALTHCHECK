"""Entrada WSGI autenticada para demonstração temporária via HTTPS."""
import base64
import hmac
import json
import re
import threading
import time
from collections import deque
from urllib.parse import urlsplit
from pathlib import Path
from jobs import JobQueue, QueueFull
from server import ROOT, MODEL, ollama, process_messages, validate_messages


class DemoApp:
    def __init__(self, origin, password, runtime=None):
        parsed = urlsplit(origin)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.path or parsed.query or parsed.fragment or parsed.username:
            raise ValueError('Configure uma origem HTTPS exata, sem caminho.')
        if len(password) < 24:
            raise ValueError('A senha da demonstração deve ter pelo menos 24 caracteres.')
        self.origin, self.host = origin, parsed.netloc
        self.authorization = 'Basic ' + base64.b64encode(('equipe:' + password).encode()).decode()
        self.runtime = runtime or JobQueue(process_messages, concurrency=1, capacity=3)
        self.lock = threading.Lock()
        self.requests, self.submissions = deque(), deque()

    def __call__(self, env, start):
        def respond(status, data, mime='application/json; charset=utf-8', extra=()):
            body = data if isinstance(data, bytes) else json.dumps(data, ensure_ascii=False).encode()
            headers = [('Content-Type', mime), ('Content-Length', str(len(body))),
                ('Cache-Control', 'no-store'), ('X-Content-Type-Options', 'nosniff'),
                ('Referrer-Policy', 'no-referrer'), ('Content-Security-Policy',
                 "default-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'")]
            start(status, headers + list(extra))
            return [body]
        now = time.monotonic()
        with self.lock:
            while self.requests and self.requests[0] < now - 60:
                self.requests.popleft()
            if len(self.requests) >= 1200:
                return respond('429 Too Many Requests', {'error': 'Limite temporário de acessos.'}, extra=[('Retry-After', '60')])
            self.requests.append(now)
        if env.get('HTTP_HOST') != self.host:
            return respond('403 Forbidden', {'error': 'Host não permitido.'})
        if env.get('HTTP_ORIGIN') not in (None, self.origin):
            return respond('403 Forbidden', {'error': 'Origem não permitida.'})
        if not hmac.compare_digest(env.get('HTTP_AUTHORIZATION', '').encode(), self.authorization.encode()):
            return respond('401 Unauthorized', {'error': 'Entre com o acesso da equipe.'},
                           extra=[('WWW-Authenticate', 'Basic realm="Demonstracao da equipe", charset="UTF-8"')])
        path, method = env.get('PATH_INFO', '/'), env['REQUEST_METHOD']
        files = {'/': ('index.html', 'text/html'), '/index.html': ('index.html', 'text/html'),
                 '/app.js': ('app.js', 'text/javascript'), '/styles.css': ('styles.css', 'text/css')}
        if method == 'GET' and path in files:
            name, mime = files[path]
            body = (ROOT / name).read_bytes()
            if name == 'index.html':
                body = body.replace(b'Este projeto n\xc3\xa3o grava conversas em arquivos ou banco de dados.',
                    'Demonstração experimental com falha conhecida na revisão de respostas. Não use para decisões de saúde. O acesso passa pela Cloudflare; o processamento da IA ocorre neste computador. O servidor do chat não grava conversas em arquivos ou banco de dados.'.encode())
            return respond('200 OK', body, mime + '; charset=utf-8')
        if method == 'GET' and path == '/api/health':
            try:
                ready = any(m.get('name') == MODEL for m in ollama('/api/tags', timeout=5).get('models', []))
                return respond('200 OK', {'ready': ready, 'model': MODEL})
            except Exception:
                return respond('503 Service Unavailable', {'ready': False, 'model': MODEL})
        if method == 'POST' and path == '/api/jobs':
            if env.get('CONTENT_TYPE', '').split(';')[0] != 'application/json':
                return respond('415 Unsupported Media Type', {'error': 'Use application/json.'})
            try:
                length = int(env.get('CONTENT_LENGTH') or 0)
                if not 0 < length <= 150000:
                    raise ValueError('Tamanho inválido.')
                messages = validate_messages(json.loads(env['wsgi.input'].read(length)))
            except (ValueError, UnicodeError):
                return respond('400 Bad Request', {'error': 'Pedido inválido.'})
            with self.lock:
                while self.submissions and self.submissions[0] < now - 60:
                    self.submissions.popleft()
                if len(self.submissions) >= 10:
                    return respond('429 Too Many Requests', {'error': 'Limite da equipe: 10 envios por minuto.'})
                self.submissions.append(now)
            try:
                job = self.runtime.submit(messages)
                return respond('202 Accepted', self.runtime.snapshot(job))
            except QueueFull:
                return respond('429 Too Many Requests', {'error': 'Fila cheia. Aguarde e tente novamente.'})
        if method in {'GET', 'DELETE'} and re.fullmatch(r'/api/jobs/[A-Za-z0-9_-]{32}', path):
            job_id = path.rsplit('/', 1)[1]
            job = self.runtime.get(job_id) if method == 'GET' else self.runtime.cancel(job_id)
            return respond('200 OK', self.runtime.snapshot(job)) if job else respond('404 Not Found', {'error': 'Pedido não encontrado ou expirado.'})
        return respond('404 Not Found', {'error': 'Rota não encontrada.'})


if __name__ == '__main__':
    import argparse
    from waitress import serve
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    app = DemoApp(config['origin'], config['password'])
    try:
        serve(app, host='127.0.0.1', port=8010, threads=4, connection_limit=32,
              backlog=32, channel_timeout=15, max_request_header_size=8192,
              max_request_body_size=150000, expose_tracebacks=False,
              inbuf_overflow=200000, log_socket_errors=False)
    finally:
        app.runtime.close()
