# `analyze_evaluations.py`

Usa pandas para ler relatórios JSON compatíveis em `evaluation/`, extrair apenas campos de resumo permitidos e consolidá-los em CSV. Com `--mlflow`, envia ao tracking local parâmetros e métricas agregadas, sem registrar perguntas, respostas ou fontes recuperadas.

O tracking configurado pelo script fica em `.mlflow/mlflow.db`. O script é opcional e precisa das dependências de `requirements-analytics.txt`.
