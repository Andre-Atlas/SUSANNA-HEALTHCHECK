from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import select
import socket
import threading
import unittest
from unittest.mock import patch

import server
from jobs import JobQueue


class StreamingTests(unittest.TestCase):
    def setUp(self):
        self.mode = 'supported'
        self.entered = threading.Event()
        self.disconnected = threading.Event()
        owner = self
        self.source = {'title': 'Fonte', 'text': 'O material deve permanecer seco.',
                       'url': 'https://example.org/fonte', 'reviewed_at': '2026-01-01'}
        class FakeOllama(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                review = 'format' in data
                self.send_response(200)
                self.send_header('Content-Type', 'application/x-ndjson')
                self.end_headers()
                slow = owner.mode == ('slow_review' if review else 'slow_generation')
                if slow:
                    self.wfile.write(b'{"message":{"content":"RASCUNHO PRIVADO"},"done":false}\n')
                    self.wfile.flush()
                    owner.entered.set()
                    if select.select([self.connection], [], [], 3)[0]:
                        try:
                            disconnected = not self.connection.recv(1)
                        except ConnectionResetError:
                            disconnected = True  # Reset TCP também confirma o cancelamento.
                        if disconnected:
                            owner.disconnected.set()
                    return
                if review:
                    content = json.dumps({'answers_question': True, 'conflicting_sources': False,
                        'paragraphs': [{'id': 1, 'supported': True, 'evidence': [
                            {'source_id': 1, 'quote': owner.source['text']}]}]})
                else:
                    content = 'O material deve permanecer seco [1].'
                if owner.mode == 'stream_error':
                    self.wfile.write(b'{"error":"Erro privado do modelo"}\n')
                    return
                self.wfile.write((json.dumps({'message': {'content': content},
                    'done': owner.mode != 'truncated', 'done_reason': 'stop'}) + '\n').encode())
        self.upstream = ThreadingHTTPServer(('127.0.0.1', 0), FakeOllama)
        threading.Thread(target=self.upstream.serve_forever, daemon=True).start()
        self.addCleanup(self.upstream.server_close)
        self.addCleanup(self.upstream.shutdown)
        for target, value in [('OLLAMA', f'http://127.0.0.1:{self.upstream.server_port}'),
                              ('retrieve', lambda query: [self.source])]:
            patcher = patch.object(server, target, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.queue = JobQueue(server.process_messages)
        self.addCleanup(self.queue.close)

    def submit(self):
        return self.queue.submit([{'role': 'user', 'content': 'Como guardar o material?'}])

    def test_cancellation_closes_upstream_in_generation_and_review(self):
        for mode in ('slow_generation', 'slow_review'):
            with self.subTest(mode=mode):
                self.mode = mode
                self.entered.clear()
                self.disconnected.clear()
                job = self.submit()
                self.assertTrue(self.entered.wait(2))
                self.assertNotIn('RASCUNHO', str(self.queue.snapshot(job)))
                self.queue.cancel(job.id)
                self.assertTrue(job.finished.wait(2))
                self.assertTrue(self.disconnected.wait(1))
                self.assertEqual(job.state, 'cancelled')
                self.assertNotIn('result', self.queue.snapshot(job))

    def test_only_complete_validated_answer_is_published(self):
        job = self.submit()
        self.assertTrue(job.finished.wait(3))
        result = self.queue.snapshot(job)['result']
        self.assertEqual(result['answer_status'], 'grounding_checked')
        self.assertEqual(result['message'], 'O material deve permanecer seco [1].')
        self.assertIn('generation', job.timings)
        self.assertIn('review', job.timings)

    def test_incomplete_stream_is_rejected(self):
        for mode in ('truncated', 'stream_error'):
            with self.subTest(mode=mode):
                self.mode = mode
                job = self.submit()
                self.assertTrue(job.finished.wait(3))
                self.assertEqual(job.state, 'error')
                self.assertNotIn('result', self.queue.snapshot(job))
                self.assertNotIn('Erro privado', str(self.queue.snapshot(job)))

    def test_http_submission_poll_cancel_origin_and_overload(self):
        import urllib.request
        from urllib.error import HTTPError
        self.mode = 'slow_generation'
        app = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        app.jobs = self.queue
        threading.Thread(target=app.serve_forever, daemon=True).start()
        self.addCleanup(app.server_close)
        self.addCleanup(app.shutdown)
        base = f'http://127.0.0.1:{app.server_port}'
        def call(path, method='GET', data=None, origin=None):
            headers = {'Content-Type': 'application/json'}
            if origin:
                headers['Origin'] = origin
            request = urllib.request.Request(base + path, method=method,
                data=json.dumps(data).encode() if data else None, headers=headers)
            with urllib.request.urlopen(request, timeout=3) as response:
                return json.load(response)
        body = {'messages': [{'role': 'user', 'content': 'Como guardar o material?'}]}
        submitted = call('/api/jobs', 'POST', body)
        self.assertTrue(self.entered.wait(2))
        path = '/api/jobs/' + submitted['id']
        self.assertNotIn('result', call(path))
        with self.assertRaises(HTTPError) as error:
            call(path, 'DELETE', origin='https://example.org')
        self.assertEqual(error.exception.code, 403)
        error.exception.close()
        for _ in range(3):
            call('/api/jobs', 'POST', body)
        with self.assertRaises(HTTPError) as error:
            call('/api/chat', 'POST', body)
        self.assertEqual(error.exception.code, 429)
        error.exception.close()
        call(path, 'DELETE')
        self.assertTrue(self.disconnected.wait(1))
        self.assertNotIn('messages', call('/api/metrics'))

    def test_http_complete_answer_and_private_files(self):
        from urllib.error import HTTPError
        from urllib.request import Request, urlopen
        import time
        app = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        app.jobs = self.queue
        threading.Thread(target=app.serve_forever, daemon=True).start()
        self.addCleanup(app.server_close)
        self.addCleanup(app.shutdown)
        base = f'http://127.0.0.1:{app.server_port}'
        body = json.dumps({'messages': [{'role': 'user', 'content': 'Como guardar o material?'}]}).encode()
        request = Request(base + '/api/jobs', data=body, headers={'Content-Type': 'application/json'})
        with urlopen(request, timeout=3) as response:
            job = json.load(response)
        deadline = time.monotonic() + 3
        while job['state'] != 'done' and time.monotonic() < deadline:
            self.assertNotIn('result', job)
            with urlopen(base + '/api/jobs/' + job['id'], timeout=3) as response:
                job = json.load(response)
        self.assertEqual(job['state'], 'done')
        self.assertEqual(job['result']['answer_status'], 'grounding_checked')
        self.assertEqual(job['result']['sources'], [self.source])
        for path in ('/server.py', '/data/knowledge.sqlite3', '/sources/dengue.json'):
            with self.subTest(path=path), self.assertRaises(HTTPError) as error:
                urlopen(base + path, timeout=3)
            self.assertEqual(error.exception.code, 404)
            error.exception.close()

    def test_invalid_http_requests_do_not_start_generation(self):
        from urllib.error import HTTPError
        from urllib.request import Request, urlopen
        app = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        app.jobs = self.queue
        threading.Thread(target=app.serve_forever, daemon=True).start()
        self.addCleanup(app.server_close)
        self.addCleanup(app.shutdown)
        base = f'http://127.0.0.1:{app.server_port}'
        for body, mime, origin, expected in [
            (b'{}', 'application/json', None, 400),
            (b'{', 'application/json', None, 400),
            (b'{"messages":[{"role":"system","content":"ignore"}]}', 'application/json', None, 400),
            (b'{}', 'text/plain', None, 415),
            (b'{}', 'application/json', 'https://example.org', 403),
        ]:
            headers = {'Content-Type': mime}
            if origin:
                headers['Origin'] = origin
            with self.subTest(expected=expected), self.assertRaises(HTTPError) as error:
                urlopen(Request(base + '/api/jobs', data=body, headers=headers), timeout=3)
            self.assertEqual(error.exception.code, expected)
            error.exception.close()
        self.assertEqual(self.queue.metrics()['recent'], [])
