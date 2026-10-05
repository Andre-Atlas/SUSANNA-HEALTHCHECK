# `ollama_transport.py`

Implementa o transporte HTTP em streaming entre o backend Python e o endpoint `/api/chat` do Ollama local. Reúne os fragmentos recebidos antes de devolver o resultado ao servidor; rascunhos parciais não são publicados como resposta aprovada.

Também registra o tempo até o primeiro token e permite que o sistema de jobs interrompa a conexão quando um pedido é cancelado. É usado por `server.py` tanto para geração quanto para revisão.
