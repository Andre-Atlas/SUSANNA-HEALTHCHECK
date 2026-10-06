# 6. Busca e fontes

## Busca por pergunta

`server.retrieve()` delega a `search_gov_br(question)`. O buscador remove palavras comuns, reduz a consulta e possui rotas diretas para alguns temas previstos no código, por exemplo vacinação, hepatite B, HIV/AIDS e transmissão, medicamentos gratuitos e conteúdo sobre desinformação. As URLs estão na constante `DIRECT_PAGES` em [`govbr_search.py`](../../govbr_search.py#L32-L41); a seleção está em [`search_gov_br()`](../../govbr_search.py#L356-L380).

Quando não há rota direta aplicável, `_serpro_search()` consulta `https://portalunico.estaleiro.serpro.gov.br/api/search/` com termos da pergunta e filtros do portal. A resposta SERPRO serve para localizar URLs: o código não usa o resumo da API como evidência. Ele percorre os resultados, aceita somente links HTTPS cujo host seja `gov.br` ou subdomínio e rebaixa a página diretamente de gov.br para extrair texto. Veja [`_serpro_search()`](../../govbr_search.py#L88-L171).

## Validação e extração

O leitor aceita apenas HTML/XHTML, valida também redirecionamentos, limita a página a 2 MB e o JSON SERPRO a 1 MB. A extração ignora elementos como script, estilo, cabeçalho, rodapé, navegação e aside. Por pergunta, tenta até cinco candidatas e retorna até três páginas; texto de cada página é limitado a 2.500 caracteres. PDFs e documentos não HTML são descartados. Limites e leitura: [`govbr_search.py`](../../govbr_search.py#L14-L21), [`_read()`](../../govbr_search.py#L260-L305), [`_extract_page()`](../../govbr_search.py#L329-L354).

## Limites práticos

- A busca geral usa consulta lexical do portal, não uma compreensão semântica garantida.
- SERPRO pode não retornar itens para termos/filtros; uma página pode ser oficial e irrelevante para a pergunta.
- Páginas renderizadas só por JavaScript, conteúdo bloqueado, HTML curto ou arquivos PDF podem não gerar trecho utilizável.
- A extração truncada pode omitir ressalvas que estavam em outra parte da página.
- `gov.br` indica o domínio, mas não significa que o trecho prove a resposta nem que tenha sido validado clinicamente.

Quando não se recupera fonte útil, o servidor pode abster-se sem chamar o modelo. Consulte [geração e revisão](07-ollama-geracao-e-revisao.md).
