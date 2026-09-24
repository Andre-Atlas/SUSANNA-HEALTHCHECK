import json
import unittest
from unittest.mock import patch

from answer_policy import grounding_errors, normalize_references, NO_EVIDENCE, INVALID_ANSWER
from server import generate_answer


class GroundingTests(unittest.TestCase):
    sources = [{'text': 'A vacinação não elimina a necessidade de controlar o mosquito.'}]
    answer = 'A vacinação não elimina o controle do mosquito [1].'
    prompt = [{'role': 'user', 'content': 'A vacinação dispensa controlar o mosquito?'}]

    def verdict(self, **overrides):
        value = {'answers_question': True, 'conflicting_sources': False, 'paragraphs': [
            {'id': 1, 'supported': True, 'evidence': [
                {'source_id': 1, 'quote': self.sources[0]['text']}]}]}
        value.update(overrides)
        return json.dumps(value)

    def run_generation(self, verdict, answer=None, reason='stop'):
        with patch('server.ollama', side_effect=[
            {'message': {'content': answer or self.answer}},
            {'message': {'content': verdict}, 'done_reason': reason}]) as model:
            result = generate_answer(self.prompt, self.sources)
        self.assertEqual(model.call_count, 2)
        return result

    def test_supported_answer_with_literal_evidence_is_released(self):
        result = self.run_generation(self.verdict())
        self.assertEqual(result['message'], self.answer)
        self.assertEqual(result['answer_status'], 'grounding_checked')

    def test_unsupported_clause_is_not_exposed(self):
        verdict = self.verdict(paragraphs=[{'id': 1, 'supported': False, 'evidence': []}])
        result = self.run_generation(verdict, 'A vacina cura dengue e dispensa prevenção [1].')
        self.assertEqual(result['message'], NO_EVIDENCE)
        self.assertNotIn('cura dengue', str(result))

    def test_irrelevant_or_conflicting_sources_abstain(self):
        for change in ({'answers_question': False}, {'conflicting_sources': True}):
            with self.subTest(change=change):
                self.assertEqual(self.run_generation(self.verdict(**change))['message'], NO_EVIDENCE)

    def test_invented_quote_wrong_id_missing_paragraph_and_boolean_rejected(self):
        baseline = json.loads(self.verdict())
        cases = []
        for field, value in [('quote', 'Esta frase não existe na fonte.'), ('source_id', 2), ('source_id', True)]:
            variant = json.loads(self.verdict())
            variant['paragraphs'][0]['evidence'][0][field] = value
            cases.append(json.dumps(variant))
        cases.extend([self.verdict(paragraphs=[]), self.verdict(answers_question='true'), 'null', '[]', '{}', 'inválido'])
        for raw in cases:
            with self.subTest(raw=raw):
                self.assertTrue(grounding_errors(raw, self.answer, self.sources))
        self.assertEqual(grounding_errors(json.dumps(baseline), self.answer, self.sources), [])

    def test_every_citation_must_have_evidence(self):
        errors = grounding_errors(self.verdict(), self.answer + ' [2]', self.sources * 2)
        self.assertIn('unchecked_citation', errors)

    def test_uncited_source_is_not_given_to_reviewer(self):
        with patch('server.ollama', side_effect=[{'message': {'content': self.answer}},
                    {'message': {'content': self.verdict()}}]) as model:
            generate_answer(self.prompt, self.sources + [{'text': 'Informação que não deve justificar a resposta.'}])
        payload = json.loads(model.call_args.args[1]['messages'][1]['content'])
        self.assertEqual(payload['sources'], [{'id': 1, 'text': self.sources[0]['text']}])

    def test_every_paragraph_must_be_checked(self):
        self.assertTrue(grounding_errors(self.verdict(), self.answer + '\n\n' + self.answer, self.sources))

    def test_verifier_truncation_and_failure_never_release_draft(self):
        self.assertEqual(self.run_generation(self.verdict(), reason='length')['message'], INVALID_ANSWER)
        with patch('server.ollama', side_effect=[{'message': {'content': self.answer}}, TimeoutError()]):
            result = generate_answer(self.prompt, self.sources)
        self.assertEqual(result['message'], INVALID_ANSWER)
        self.assertEqual(result['validation_errors'], ['verification_unavailable'])

    def test_numeric_format_is_normalized_without_inventing_citations(self):
        self.assertEqual(normalize_references('Texto [ 1, 2; 3 ].'), 'Texto [1][2][3].')
        self.assertEqual(normalize_references('Texto sem citação.'), 'Texto sem citação.')
        self.assertEqual(normalize_references('Texto [01].'), 'Texto [01].')
        self.assertEqual(self.run_generation(self.verdict(), 'Texto [ 1 ].')['answer_status'], 'grounding_checked')


if __name__ == '__main__':
    unittest.main()
