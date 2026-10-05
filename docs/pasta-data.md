# Pasta `data/`

Contém o banco SQLite local `knowledge.sqlite3`, criado e mantido pelos módulos `knowledge.py`, `seed_knowledge.py` e `operations.py`. Ele indexa documentos para busca lexical offline, avaliações e tarefas de manutenção.

O servidor do chat online atualmente consulta o gov.br por meio de `govbr_search.py`; não usa esse arquivo SQLite como fonte das respostas. A pasta é ignorada pelo Git porque o banco é um artefato local que pode ser reconstruído a partir dos documentos apropriados.

Use os comandos de manutenção documentados no projeto para inspecionar ou copiar o banco. Evite editar o arquivo manualmente e não o apague se precisar executar avaliações offline sem reconstruí-lo.
