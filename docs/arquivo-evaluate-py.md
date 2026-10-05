# `evaluate.py`

Avalia o fluxo de recuperação offline com perguntas e documentos versionados. Cria um SQLite temporário, importa os JSON de `sources/` e mede se a busca local recupera as fontes esperadas.

Com `--llm`, também chama geração e validação usando o Ollama. O banco temporário é descartado ao fim; o resultado vai para `evaluation/`. Não é executado automaticamente em cada conversa.
