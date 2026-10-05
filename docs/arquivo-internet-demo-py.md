# `internet_demo.py`

Inicia uma demonstração temporária acessível pela internet. Verifica pré-requisitos, inicia Cloudflare Tunnel ou ngrok, gera credenciais temporárias e inicia `internet_app.py` localmente; ao encerrar, tenta finalizar os processos iniciados.

É opcional e não é necessário para o uso local por `server.py`. O endereço do túnel pode mudar a cada sessão; credenciais e logs são guardados fora do repositório.
