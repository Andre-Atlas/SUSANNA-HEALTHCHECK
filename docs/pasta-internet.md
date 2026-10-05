A pasta `.internet` é para o **executável opcional do túnel Cloudflare ou ngrok** usado na demonstração externa do projeto. Ela só é consultada pelo script `internet_demo.py` quando esse programa não está disponível no `PATH`; nesse caso, ele procura o executável em `.internet/bin/`.

Ela não guarda as páginas consultadas pelo chatbot, conversas nem a base SQLite. Os registros e credenciais da demonstração ficam em outro diretório privado do usuário, fora do repositório.

A pasta `.internet` está no `.gitignore`, então seu conteúdo não é incluído nos commits. Para usar a demonstração pela internet, o túnel precisa estar instalado no `PATH` ou em `.internet/bin/`. Para executar o projeto apenas localmente com `server.py`, ela não é necessária.