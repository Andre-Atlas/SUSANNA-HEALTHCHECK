import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from io import BytesIO

import knowledge
import server


class KnowledgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.database = self.root / 'knowledge.sqlite3'

    def document(self, **overrides):
        data = dict(title='Documento sintético de teste',
                    url='https://example.org/teste', reviewed_at='2026-01-01',
                    text='Informações sobre vacinação. Conteúdo fictício para testar a busca.')
        data.update(overrides)
        path = self.root / 'document.json'
        path.write_text(json.dumps(data), encoding='utf-8')
        return path

    def test_empty_database_does_not_create_file(self):
        self.assertEqual(knowledge.retrieve('vacinação', self.database), [])
        self.assertFalse(self.database.exists())

    def test_search_accents_and_no_match(self):
        knowledge.import_document(self.document(), self.database)
        found = knowledge.retrieve('O que é vacinacao?', self.database)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]['url'], 'https://example.org/teste')
        self.assertEqual(knowledge.retrieve('astronomia', self.database), [])
        self.assertEqual(knowledge.retrieve('como e onde?', self.database), [])

    def test_reimport_replaces_old_text(self):
        knowledge.import_document(self.document(), self.database)
        knowledge.import_document(self.document(text='Texto sobre astronomia.'), self.database)
        self.assertEqual(knowledge.retrieve('vacinação', self.database), [])
        self.assertEqual(len(knowledge.retrieve('astronomia', self.database)), 1)

    def test_invalid_import_preserves_existing_document(self):
        knowledge.import_document(self.document(), self.database)
        with self.assertRaises(ValueError):
            knowledge.import_document(self.document(reviewed_at='invalid'), self.database)
        self.assertEqual(len(knowledge.retrieve('vacinação', self.database)), 1)

    def test_unsafe_url_rejected(self):
        with self.assertRaises(ValueError):
            knowledge.import_document(self.document(url='javascript:alert(1)'), self.database)

    def test_query_operators_are_not_executed(self):
        knowledge.import_document(self.document(), self.database)
        self.assertEqual(knowledge.retrieve('" OR * NOT ()', self.database), [])

    def test_isolated_overlap_is_not_enough_for_multiple_terms(self):
        knowledge.import_document(self.document(text='Tratamento de assunto fictício.'), self.database)
        self.assertEqual(knowledge.retrieve('Tratamento diabetes', self.database), [])
        self.assertEqual(len(knowledge.retrieve('Tratamento assunto', self.database)), 1)

    def test_chunks_bounded_and_complete(self):
        text = 'vacinação exemplo ' * 600
        knowledge.import_document(self.document(text=text), self.database)
        import sqlite3
        from contextlib import closing
        with closing(sqlite3.connect(self.database)) as connection:
            chunks = [row[0] for row in connection.execute('SELECT text FROM chunks ORDER BY rowid')]
        self.assertEqual(' '.join(chunks), text.strip())
        self.assertTrue(all(len(chunk) <= 1200 for chunk in chunks))
        self.assertEqual(len(knowledge.retrieve('vacinação', self.database)), 3)


class PromptTests(unittest.TestCase):
    def test_large_history_keeps_current_question(self):
        messages = [{'role': 'user' if i % 2 == 0 else 'assistant',
                     'content': 'a' * (3000 if i % 2 == 0 else 12000)} for i in range(13)]
        prompt, sources = server.build_prompt(messages, [])
        self.assertEqual(prompt[-1], messages[-1])
        self.assertLess(len(prompt), len(messages))
        self.assertEqual(prompt[0]['role'], 'system')
        self.assertEqual(sources, [])
        self.assertIn('Nenhum trecho', prompt[0]['content'])

    def test_oversized_question_rejected(self):
        with self.assertRaises(ValueError):
            server.build_prompt([{'role': 'user', 'content': '😀' * 3000}], [])

    def test_chat_returns_only_sources_sent_to_model(self):
        handler = object.__new__(server.Handler)
        handler.path = '/api/chat'
        body = json.dumps({'messages': [{'role': 'user', 'content': 'vacinação'}]}).encode()
        handler.headers = {'Content-Type': 'application/json', 'Content-Length': str(len(body))}
        handler.rfile = BytesIO(body)
        handler.server = type('Server', (), {'server_port': 8002})()
        source = dict(title='Teste', text='Trecho sintético.', url='https://example.org', reviewed_at='2026-01-01')
        with patch.object(server, 'retrieve', return_value=[source]), \
             patch.object(server, 'ollama', return_value={'message': {'content': 'Resposta [1]'}}) as model, \
             patch.object(handler, 'json_response') as response:
            handler.do_POST()
            self.assertEqual(response.call_args.args[0], 200)
            self.assertEqual(response.call_args.args[1]['sources'], [source])
            self.assertIn(source['text'], model.call_args.args[1]['messages'][0]['content'])


if __name__ == '__main__':
    unittest.main()
