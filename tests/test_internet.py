import io
import json
import unittest
from jobs import JobQueue
from internet_app import DemoApp


class InternetTests(unittest.TestCase):
    def setUp(self):
        self.runtime = JobQueue(lambda messages: (200, {'message': 'Teste'}))
        self.addCleanup(self.runtime.close)
        self.app = DemoApp('https://demo.trycloudflare.com', 'x'*32, self.runtime)

    def request(self, path='/', method='GET', auth=True, origin=None, body=None, host='demo.trycloudflare.com'):
        data = json.dumps(body).encode() if body else b''
        env = {'HTTP_HOST': host, 'PATH_INFO': path, 'REQUEST_METHOD': method,
               'wsgi.input': io.BytesIO(data), 'CONTENT_LENGTH': str(len(data)), 'CONTENT_TYPE':'application/json'}
        if auth: env['HTTP_AUTHORIZATION'] = self.app.authorization
        if origin: env['HTTP_ORIGIN'] = origin
        result = {}
        response = b''.join(self.app(env, lambda status, headers: result.update(status=status, headers=dict(headers))))
        return result, response

    def test_all_routes_require_auth(self):
        for path in ('/', '/app.js', '/api/health', '/api/jobs/'+'a'*32):
            result, _ = self.request(path, auth=False)
            self.assertTrue(result['status'].startswith('401'))
            self.assertIn('WWW-Authenticate', result['headers'])

    def test_origin_host_and_private_routes(self):
        self.assertTrue(self.request(origin='https://evil.example')[0]['status'].startswith('403'))
        self.assertTrue(self.request(host='evil.example')[0]['status'].startswith('403'))
        for path in ('/api/metrics', '/api/ready', '/api/chat', '/.internet/access.json', '/server.py'):
            self.assertTrue(self.request(path)[0]['status'].startswith('404'))
        self.assertIn(b'Cloudflare', self.request()[1])

    def test_submit_poll_cancel_and_limit(self):
        body = {'messages':[{'role':'user','content':'Teste'}]}
        result, data = self.request('/api/jobs','POST', origin=self.app.origin, body=body)
        self.assertTrue(result['status'].startswith('202'))
        job = json.loads(data)
        self.assertTrue(self.request('/api/jobs/'+job['id'])[0]['status'].startswith('200'))
        self.assertTrue(self.request('/api/jobs/'+job['id'],'DELETE',origin=self.app.origin)[0]['status'].startswith('200'))
        import time
        self.app.submissions.extend([time.monotonic()]*10)
        self.assertTrue(self.request('/api/jobs','POST',body=body)[0]['status'].startswith('429'))
