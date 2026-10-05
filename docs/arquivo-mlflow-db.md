# `mlflow.db` na raiz

O arquivo mostrado no print está versionado na raiz do repositório. **O código atual não aponta para esse caminho**: `analyze_evaluations.py` configura o tracking local em `.mlflow/mlflow.db`, e `benchmark_performance.py` também usa essa configuração.

Assim, o `mlflow.db` da raiz parece ser um banco antigo ou um artefato separado, e não é consultado pelo chat. Não o confunda com `data/knowledge.sqlite3`, que é a base documental local. Antes de removê-lo, confira se há histórico que precise ser preservado; este documento não inspecionou o conteúdo das tabelas.
