# Pasta `.mlflow/`

Armazena dados locais de tracking do MLflow. No projeto, o MLflow pode registrar métricas agregadas de avaliações para comparação entre execuções; o SQLite `mlflow.db`, quando configurado como backend, pertence a esse acompanhamento.

Essa pasta não é a base documental SQLite e não é consultada para gerar respostas do chatbot. É estado local de experimentação e está ignorada pelo Git. Preserve-a se quiser manter o histórico de execuções registrado neste computador.
