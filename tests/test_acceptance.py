import json
from pathlib import Path
import unittest

from audit_interface import audit, contrast
from evaluate_acceptance import assess, human_packet

ROOT = Path(__file__).resolve().parents[1]


class AcceptanceTests(unittest.TestCase):
    def test_new_scenarios_are_not_copies_of_development_questions(self):
        old = set()
        for filename in ('questions.json', 'search-cases.json'):
            old.update(case['question'].strip().casefold() for case in
                       json.loads((ROOT / 'evaluation' / filename).read_text()))
        cases = json.loads((ROOT / 'evaluation/acceptance-cases.json').read_text())['cases']
        self.assertEqual(len({case['id'] for case in cases}), len(cases))
        for case in cases:
            # Abertura inédita; expressões comuns de continuidade podem se repetir.
            self.assertNotIn(case['turns'][0].strip().casefold(), old)

    def test_technical_rejection_does_not_count_as_semantic_abstention(self):
        checks = assess({'expected': 'abstain'}, {'message': 'Recusa técnica.', 'answer_status': 'reference_rejected'})
        self.assertFalse(checks['expected_status'])
        self.assertFalse(checks['no_technical_rejection'])

    def test_unexercised_fixture_and_attack_marker_fail(self):
        case = {'expected': 'answer_or_abstain', 'expected_sources_count': 1, 'forbidden': ['ATAQUE']}
        checks = assess(case, {'message': 'ATAQUE', 'answer_status': 'grounding_checked', 'sources': []})
        self.assertFalse(checks['no_attack_marker'])
        self.assertFalse(checks['fixture_exercised'])

    def test_human_packet_never_marks_automatic_success_as_human_approval(self):
        packet = human_packet({'created_at': '2026-09-24',
            'hashes': {'evaluation/acceptance-cases.json': 'hash'},
            'results': [{'id': 'test', 'category': 'test', 'rubric': 'Conferir.', 'automatic_pass': True,
                         'turns': [{'question': 'Pergunta', 'result': {'message': 'Resposta', 'sources': []}}]}]},
            Path('acceptance.json'))
        self.assertIn('Revisor A: **PENDENTE**', packet)
        self.assertIn('Revisor B: **PENDENTE**', packet)

    def test_static_markup_checks_and_known_contrast_values(self):
        self.assertAlmostEqual(contrast('#000000', '#ffffff'), 21)
        self.assertAlmostEqual(contrast('#ffffff', '#ffffff'), 1)
        result = audit()
        self.assertTrue(result['static_pass'], result['checks'])
        self.assertIn('celular físico e teclado virtual', result['pending'])
