# `benchmark_performance.py`

Mede tempos do pipeline e, quando disponível, dados do Ollama, como versão, modelo carregado e uso reportado. Por padrão, usa busca SQLite offline; a opção `--live-search` mede também a busca online gov.br.

Pode repetir perguntas sintéticas, descartar aquecimentos, gravar um JSON em `evaluation/` e, com `--mlflow`, registrar métricas técnicas agregadas. Não faz parte do caminho normal do chat.
