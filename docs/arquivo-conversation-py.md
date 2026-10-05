# `conversation.py`

Resolve referências curtas a mensagens anteriores. Reconhece apenas formas explícitas de continuação, como “e nesse caso?” e “pode explicar melhor?”, e usa perguntas anteriores do usuário como contexto.

Respostas anteriores do modelo não são tratadas como evidência. Quando a referência não tem assunto identificável, o módulo pede esclarecimento. `server.py` chama essa lógica antes da busca.
