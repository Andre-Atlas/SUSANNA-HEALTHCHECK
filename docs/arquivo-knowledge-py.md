# `knowledge.py`

Gerencia a base documental SQLite offline. Importa documentos JSON, divide o texto em trechos, mantém um índice FTS5 e oferece busca lexical com normalização de acentos, expansão controlada de termos e seleção limitada de resultados.

É usado por scripts de seed, manutenção, avaliações e benchmarks offline. O chat online atual obtém fontes com `govbr_search.py`, não por esta busca local.
