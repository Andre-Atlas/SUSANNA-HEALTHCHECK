"""Validação do catálogo e recuperação dos novos temas em banco temporário."""
import json
from pathlib import Path
import tempfile
import unittest

from answer_policy import source_instruction_errors
from knowledge import import_document, retrieve

ROOT = Path(__file__).resolve().parents[1]


class SourceCatalogTests(unittest.TestCase):
    def test_metadata_and_no_instruction_patterns(self):
        urls = set()
        for path in (ROOT / 'sources').glob('*.json'):
            doc = json.loads(path.read_text(encoding='utf-8'))
            with self.subTest(source=path.name):
                for key in ('title', 'publisher', 'url', 'reviewed_at'):
                    self.assertTrue(doc.get(key))
                self.assertNotIn(doc['url'], urls)
                urls.add(doc['url'])
                self.assertEqual(source_instruction_errors([doc]), [])
                self.assertEqual(doc['reviewed_at'], doc['documentary_check']['checked_at'])

    def test_new_topics_and_disease_mismatch(self):
        cases = [
            ('Preciso vacinar contra gripe todo ano?', 'gripe-prevencao.json'),
            ('Pegar tuberculose usando o mesmo copo é possível?', 'tuberculose.json'),
            ('Pressão alta pode ser controlada?', 'hipertensao.json'),
            ('Abraçar uma pessoa transmite HIV?', 'hiv-transmissao.json'),
            ('Você tem remédio para HIV?', 'hiv-tratamento-sus.json'),
            ('O SUS fornece antirretroviral de graça?', 'hiv-tratamento-sus.json'),
            ('Quais serviços de saúde o SUS oferece?', 'sus-visao-geral.json'),
            ('Quem distribui medicamentos para HIV nos municípios?', 'sus-medicamentos-cesaf.json'),
            ('Como pedir medicamento do componente especializado?', 'sus-medicamentos-ceaf.json'),
            ('Como prevenir raiva depois de mordida?', 'raiva-prevencao.json'),
            ('O atendimento do SAMU é pago?', 'samu-192.json'),
            ('Qual tratamento cura diabetes?', None),
            ('Qual tratamento cura câncer?', None),
        ]
        with tempfile.TemporaryDirectory() as folder:
            database = Path(folder) / 'test.sqlite3'
            urls = {}
            for path in (ROOT / 'sources').glob('*.json'):
                urls[path.name] = json.loads(path.read_text(encoding='utf-8'))['url']
                import_document(path, database)
            for question, expected in cases:
                with self.subTest(question=question):
                    found = [s['url'] for s in retrieve(question, database, rerank=True)]
                    if expected:
                        self.assertIn(urls[expected], found)
                    else:
                        self.assertEqual(found, [])
