# 9. Fontes, SQLite e modo offline

## Documentos de `sources/`

Os JSON versionados registram sínteses/trechos, título, URL e data de revisão. `seed_knowledge.py` percorre apenas `sources/*.json` diretamente e importa esses documentos na base SQLite; não percorre automaticamente `sources/retiradas/`.

## Banco local

`knowledge.py` cria tabela virtual FTS5 `chunks` com título, texto, URL e data. Divide textos em blocos de até aproximadamente 1.200 caracteres, indexa com tokenizer Unicode e remoção de diacríticos e oferece busca lexical, expansão controlada/alias e seleção de até três trechos. `operations.py` inspeciona e copia o arquivo.

Banco padrão: `data/knowledge.sqlite3`. Esse SQLite é para busca offline, avaliações e manutenção, **não é o índice consultado na conversa online atual**. O `retrieve()` de `server.py` chama `search_gov_br()`.

## Avaliações offline

`evaluate.py`, `evaluate_search.py` e `evaluate_acceptance.py` podem construir bases temporárias usando documentos JSON para isolar os casos e não alterar a base do usuário. `benchmark_performance.py` usa busca local por padrão e pode optar explicitamente por busca online com `--live-search`.

## SQLite do MLflow

O tracking configurado pelos scripts analíticos fica em `.mlflow/mlflow.db`. O arquivo `mlflow.db` da raiz está versionado, mas os caminhos atuais do código não apontam para ele; origem e necessidade não foram confirmadas. Isso não deve ser confundido com `data/knowledge.sqlite3`.
