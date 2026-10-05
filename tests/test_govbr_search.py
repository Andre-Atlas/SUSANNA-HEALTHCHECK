import unittest
from unittest.mock import patch

from govbr_search import (DIRECT_PAGES, GovBrSearchError, MAX_CANDIDATES, _GovBrRedirects,
                          _extract_page, _read, _search_links,
                          is_gov_br_url, search_gov_br)


class GovBrSearchTests(unittest.TestCase):
    def test_url_policy_accepts_only_https_gov_br_hosts(self):
        allowed = [
            'https://www.gov.br/saude',
            'https://saude.gov.br/pagina',
            'https://gov.br/pagina',
            'https://www.gov.br:443/pagina',
        ]
        rejected = [
            'http://www.gov.br/pagina',
            'https://gov.br.attacker.example/pagina',
            'https://evilgov.br/pagina',
            'https://www.gov.br.evil.example/pagina',
            'https://user:pass@www.gov.br/pagina',
            'https://www.gov.br:444/pagina',
            'javascript:alert(1)',
            'https://%zz.gov.br/pagina',
        ]
        for url in allowed:
            with self.subTest(url=url):
                self.assertTrue(is_gov_br_url(url))
        for url in rejected:
            with self.subTest(url=url):
                self.assertFalse(is_gov_br_url(url))

    def test_redirect_cannot_leave_gov_br(self):
        from urllib.request import Request
        handler = _GovBrRedirects()
        request = Request('https://www.gov.br/origem')
        with self.assertRaises(GovBrSearchError):
            handler.redirect_request(request, None, 302, 'Found', {}, 'https://example.org/')

    def test_search_links_discard_external_and_non_html_documents(self):
        html = '''<div class="search-results">
          <a href="https://www.gov.br/saude/pagina">Página oficial</a>
          <a href="https://example.org/falso">Fora do gov.br</a>
          <a href="/saude/anexo.pdf">PDF</a>
          <a href="/saude/@@search?query=x">Outra busca</a>
        </div>'''
        self.assertEqual(_search_links(html, 'https://www.gov.br/saude/pt-br/@@search'),
                         [('https://www.gov.br/saude/pagina', 'Página oficial')])

    def test_extract_strips_navigation_and_scripts_and_rejects_short_pages(self):
        body = ('<header>cabeçalho</header><nav>menu</nav><script>ignorar()</script>'
                '<h1>Informação oficial</h1><main><p>'
                + 'Conteúdo verificável da página oficial. ' * 12 + '</p></main>')
        source = _extract_page('https://www.gov.br/saude/pagina', body, '2026-10-05T12:00:00-03:00')
        self.assertIsNotNone(source)
        self.assertIn('Conteúdo verificável', source['text'])
        self.assertNotIn('cabeçalho', source['text'])
        self.assertNotIn('ignorar()', source['text'])
        self.assertEqual(source['title'], 'Informação oficial')
        self.assertIsNone(_extract_page('https://www.gov.br/saude/vazia', '<p>curta</p>', '2026-10-05'))

    def test_search_uses_bounded_candidate_pages_and_reports_live_metadata(self):
        page_html = ('<h1>Vacinação</h1><p>'
                     + 'Informação oficial e verificável para fins educativos. ' * 10 + '</p>')
        with patch('govbr_search._serpro_search',
                   return_value=['https://www.gov.br/saude/pagina']) as search, patch(
                'govbr_search._read',
                return_value=('https://www.gov.br/saude/pagina', page_html)) as read:
            sources = search_gov_br('pergunta sintética')
        search.assert_called_once_with('pergunta sintética', 5)
        self.assertEqual(len(read.call_args_list), 1)
        self.assertLessEqual(len(read.call_args_list), MAX_CANDIDATES)
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]['source_type'], 'gov_br_live')
        self.assertEqual(sources[0]['url'], 'https://www.gov.br/saude/pagina')
        self.assertTrue(sources[0]['retrieved_at'])

    def test_hiv_air_question_typo_uses_ministry_transmission_page(self):
        page_html = ('<h1>Transmissão do HIV</h1><p>O HIV não é transmitido pelo ar. '
                     'As formas de transmissão incluem contato com fluidos corporais específicos. '
                     * 8 + '</p>')
        with patch('govbr_search._serpro_search') as serpro, patch(
                'govbr_search._read', return_value=(DIRECT_PAGES['hiv_transmission'], page_html)) as read:
            sources = search_gov_br('aides transmitida pelo ar?')
        serpro.assert_not_called()
        read.assert_called_once_with(DIRECT_PAGES['hiv_transmission'], 2_000_000, 5)
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]['url'], DIRECT_PAGES['hiv_transmission'])
        self.assertIn('não é transmitido pelo ar', sources[0]['text'])

    def test_free_medicines_question_uses_farmacia_popular_and_rename(self):
        farmacia_html = ('<h1>Farmácia Popular</h1><p>Os medicamentos e insumos '
                         'são fornecidos gratuitamente. ' * 8 + '</p>')
        rename_html = ('<h1>Rename</h1><p>A Rename lista medicamentos e insumos '
                       'disponíveis no SUS. ' * 8 + '</p>')
        pages = [
            (DIRECT_PAGES['farmacia_popular'], farmacia_html),
            (DIRECT_PAGES['rename'], rename_html),
        ]
        with patch('govbr_search._serpro_search') as serpro, patch(
                'govbr_search._read', side_effect=pages) as read:
            sources = search_gov_br('tem remédios gratuitos no sus?')
        serpro.assert_not_called()
        self.assertEqual([source['url'] for source in sources], [url for url, _ in pages])
        self.assertEqual(read.call_count, 2)

    def test_failed_search_is_explicit_and_oversized_body_is_rejected(self):
        with patch('govbr_search._serpro_search',
                   side_effect=GovBrSearchError('falha sintética')):
            with self.assertRaises(GovBrSearchError):
                search_gov_br('pergunta sintética')
        with patch('govbr_search._serpro_search', return_value=['https://www.gov.br/saude/pagina']), \
                patch('govbr_search._read', side_effect=GovBrSearchError('falha sintética')):
            self.assertEqual(search_gov_br('pergunta sintética'), [])

        class Headers:
            def get_content_type(self):
                return 'text/html'

            def get_content_charset(self):
                return 'utf-8'

        class Response:
            headers = Headers()

            def geturl(self):
                return 'https://www.gov.br/saude/pagina'

            def read(self, size):
                return b'x' * size

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        class Opener:
            def open(self, *args, **kwargs):
                return Response()

        with patch('govbr_search.build_opener', return_value=Opener()):
            with self.assertRaises(GovBrSearchError):
                _read('https://www.gov.br/saude/pagina', 10, 1)


if __name__ == '__main__':
    unittest.main()
