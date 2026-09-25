import http.client
from http.server import ThreadingHTTPServer
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from knowledge import import_document
from operations import copy_database, inspect_database
from server import Handler


class OperationsTests(unittest.TestCase):
    def test_backup_restore_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            source, backup, restored = [Path(directory) / name for name in ('source.db', 'backup.db', 'restored.db')]
            import_document(Path(__file__).resolve().parents[1] / 'sources/dengue.json', source)
            expected = inspect_database(source)
            self.assertEqual(copy_database(source, backup), expected)
            source.unlink()
            self.assertEqual(copy_database(backup, restored), expected)
            original = restored.read_bytes()
            with self.assertRaises(FileExistsError):
                copy_database(backup, restored)
            self.assertEqual(restored.read_bytes(), original)

    def test_missing_source_does_not_create_files(self):
        with tempfile.TemporaryDirectory() as directory:
            source, target = Path(directory) / 'absent', Path(directory) / 'backup'
            with self.assertRaises(Exception):
                copy_database(source, target)
            self.assertFalse(source.exists())
            self.assertFalse(target.exists())

    def test_http_access_and_readiness(self):
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        def request(path, headers=None):
            conn = http.client.HTTPConnection('127.0.0.1', server.server_port)
            try:
                conn.request('GET', path, headers=headers or {})
                response = conn.getresponse()
                response.read()
                return response
            finally:
                conn.close()
        try:
            self.assertEqual(request('/').status, 200)
            self.assertEqual(request('/', {'Host': 'untrusted.example'}).status, 403)
            self.assertEqual(request('/api/metrics', {'Origin': 'https://untrusted.example'}).status, 403)
            self.assertEqual(request('/data/knowledge.sqlite3').status, 404)
            with patch('server.inspect_database', return_value={'ready': True, 'chunks': 6}), patch('server.ollama', return_value={'models': []}):
                self.assertEqual(request('/api/ready').status, 503)
            with patch('server.inspect_database', side_effect=ValueError('empty')):
                self.assertEqual(request('/api/ready').status, 503)
            from server import MODEL
            with patch('server.inspect_database', return_value={'ready': True, 'chunks': 6}), patch('server.ollama', return_value={'models': [{'name': MODEL}]}):
                response = request('/api/ready')
                self.assertEqual(response.status, 200)
                self.assertIn("frame-ancestors 'none'", response.getheader('Content-Security-Policy'))
        finally:
            server.shutdown()
            thread.join()
            server.server_close()
