# `evaluate_acceptance.py`

Executa casos de aceitação pelo caminho HTTP real de jobs e pelo Ollama. Sobe um servidor de teste, usa dados/corpus isolados e verifica propriedades do resultado, como estado, formato e fonte esperada.

Gera relatório em `evaluation/`. É uma verificação explícita de aceitação; não roda junto com o servidor de uso cotidiano.
