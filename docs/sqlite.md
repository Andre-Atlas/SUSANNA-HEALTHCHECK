No chat atual, o SQLite **não participa da busca que fundamenta as respostas**. Apesar de o `server.py` importar `sqlite3` e ter uma mensagem de erro para falhas na base, a função `retrieve()` usada pelo chat chama `search_gov_br()`: a busca é feita ao vivo no portal do Ministério da Saúde e nas páginas gov.br encontradas.

O SQLite é usado em outros fluxos do projeto:

- **Avaliação offline:** os documentos JSON versionados em `sources/` são importados para uma base temporária. Os avaliadores consultam essa base sem acessar a internet.
- **Manutenção e inspeção:** `knowledge.py` permite importar ou remover documentos; `operations.py` verifica a integridade da base e pode fazer uma cópia de segurança.
- **Busca local:** os textos são divididos em trechos e guardados numa tabela FTS5 chamada `chunks`, com título, texto, URL e data de revisão. O índice busca palavras e variações; não entende o significado como um modelo de linguagem.

Portanto, no funcionamento atual, a resposta do chat vem dos trechos obtidos na busca online, **não dos registros locais do SQLite**. Essa separação também está descrita no [README.md](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/README.md:21>); a implementação da base está em [knowledge.py](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/knowledge.py:29>) e o servidor direciona a busca do chat para o gov.br em [server.py](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/server.py:29>).