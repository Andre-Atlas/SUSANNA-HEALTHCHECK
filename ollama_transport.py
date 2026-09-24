"""Stream privado do Ollama: rascunhos nunca são publicados no estado do pedido."""
import http.client
import json
import time
from urllib.error import HTTPError
from urllib.parse import urlsplit

from jobs import current_job


def chat_stream(base_url, data, timeout=180):
    started = time.monotonic()
    phase = 'review' if 'format' in data else 'generation'
    url = urlsplit(base_url)
    connection = http.client.HTTPConnection(url.hostname, url.port, timeout=5)
    job = current_job()
    try:
        if job:
            job.check()
        connection.connect()
        connection.sock.settimeout(timeout)
        if job:
            job.attach(connection.sock)
        connection.request('POST', '/api/chat', body=json.dumps({**data, 'stream': True}).encode(),
                           headers={'Content-Type': 'application/json'})
        response = connection.getresponse()
        if response.status != 200:
            raise HTTPError(base_url + '/api/chat', response.status, response.reason, response.headers, None)
        content = []
        size = 0
        while True:
            if job:
                job.check()
            line = response.readline(262145)
            if not line or len(line) > 262144:
                raise ValueError('Stream incompleto ou muito grande.')
            item = json.loads(line)
            if not isinstance(item, dict) or item.get('error'):
                raise ValueError('Falha no stream do modelo.')
            fragment = item.get('message', {}).get('content', '')
            if not isinstance(fragment, str):
                raise ValueError('Conteúdo inválido.')
            content.append(fragment)
            if job and fragment:
                with job.lock:
                    job.timings.setdefault(phase + '_first_token', round(time.monotonic() - started, 4))
            size += len(line)
            if size > 2_000_000:
                raise ValueError('Resposta do modelo muito grande.')
            if item.get('done') is True:
                if job:
                    job.check()
                return {**item, 'message': {'content': ''.join(content)}}
    except Exception:
        if job:
            job.check()
        raise
    finally:
        if job:
            with job.lock:
                job.upstream = None
        connection.close()
