# `internet_app.py`

Implementa a aplicação WSGI para a demonstração externa. Exige autenticação, confere host/origem permitidos e publica um conjunto restrito de rotas para saúde e trabalhos do chat, encaminhando o processamento a componentes do servidor.

É iniciada por `internet_demo.py` com Waitress; não substitui nem é usada pelo servidor local padrão.
