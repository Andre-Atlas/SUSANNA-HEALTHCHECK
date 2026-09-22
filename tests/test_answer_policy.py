import unittest
from unittest.mock import patch

from answer_policy import NO_EVIDENCE, INVALID_ANSWER, reference_errors
from server import generate_answer


class AnswerPolicyTests(unittest.TestCase):
    sources = [{'title': 'Teste', 'text': 'Texto sintético.', 'url': 'https://example.org'}]

    def test_no_sources_never_calls_model(self):
        with patch('server.ollama') as model:
            result = generate_answer([], [])
        model.assert_not_called()
        self.assertEqual(result['message'], NO_EVIDENCE)
        self.assertFalse(result['llm_called'])

    def test_existing_citation_is_accepted(self):
        self.assertEqual(reference_errors('Informação [1].', self.sources), [])

    def test_invalid_formats_and_out_of_range(self):
        for ref in ('0', '2', '1,2', '01', '999999999999999999999999', 'fonte'):
            with self.subTest(ref=ref):
                self.assertIn('invalid_citation', reference_errors(f'Informação [{ref}]', self.sources))

    def test_each_paragraph_needs_citation(self):
        errors = reference_errors('Informação [1]\n\nAfirmação sem referência.', self.sources)
        self.assertIn('uncited_paragraph', errors)

    def test_links_only_come_from_backend(self):
        for link in ('https://example.org', 'www.example.org', 'example.org', '[link](/pagina)'):
            with self.subTest(link=link):
                self.assertIn('generated_link', reference_errors(f'Confira {link} [1]', self.sources))

    def test_missing_citation_falls_back_without_exposing_text(self):
        with patch('server.ollama', return_value={'message': {'content': 'Texto não validado.'}}):
            result = generate_answer([], self.sources)
        self.assertEqual(result['message'], INVALID_ANSWER)
        self.assertEqual(result['answer_status'], 'reference_rejected')
        self.assertNotIn('Texto não validado.', str(result))

    def test_model_can_abstain_even_with_retrieved_sources(self):
        with patch('server.ollama', return_value={'message': {'content': 'SEM_EVIDENCIA'}}):
            result = generate_answer([], self.sources)
        self.assertEqual(result['answer_status'], 'insufficient_evidence')
        self.assertEqual(result['message'], NO_EVIDENCE)

    def test_abstention_marker_with_citation_is_never_displayed(self):
        with patch('server.ollama', return_value={'message': {'content': 'SEM_EVIDENCIA [1]'}}):
            result = generate_answer([], self.sources)
        self.assertEqual(result['message'], NO_EVIDENCE)
        self.assertEqual(result['answer_status'], 'insufficient_evidence')

    def test_truncated_output_is_not_shown(self):
        with patch('server.ollama', return_value={'message': {'content': 'Informação [1]'}, 'done_reason': 'length'}):
            result = generate_answer([], self.sources)
        self.assertEqual(result['answer_status'], 'reference_rejected')
        self.assertIn('truncated_answer', result['validation_errors'])

    def test_empty_or_wrong_type_output(self):
        for content in ('', None, []):
            with self.subTest(content=content), patch('server.ollama', return_value={'message': {'content': content}}):
                result = generate_answer([], self.sources)
                self.assertEqual(result['message'], INVALID_ANSWER)


if __name__ == '__main__':
    unittest.main()
