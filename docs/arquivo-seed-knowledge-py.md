# `seed_knowledge.py`

Carrega em `data/knowledge.sqlite3` os arquivos JSON que estão diretamente em `sources/`. Quando um documento declara que substitui outra URL, remove da base os trechos da fonte substituída.

É um comando explícito de preparação/manutenção da base offline; não roda ao iniciar o chat nem busca conteúdo na internet. O subdiretório `sources/retiradas/` não é percorrido pelo glob utilizado.
