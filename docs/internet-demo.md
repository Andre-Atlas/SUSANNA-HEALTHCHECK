# Demonstração temporária pela internet

Modo solicitado em 25/09/2026. Usa o computador como servidor e um Quick Tunnel
Cloudflare, sem contratação de hospedagem ou domínio. Link aleatório e temporário;
sem garantia de disponibilidade. É uma demonstração restrita, não entrega final
aprovada: a falha F01 do revisor permanece aberta.

## Acessar a demonstração ativa

**Link temporário desta sessão:**
[https://what-attended-saturday-equity.trycloudflare.com](https://what-attended-saturday-equity.trycloudflare.com)

Estado conferido em 30/09/2026: o túnel autenticado e o endpoint de saúde
responderam; uma pergunta de teste passou pela revisão documental. O endereço e a
senha foram renovados nesta inicialização. Consulte a senha no arquivo privado
`access.json` descrito abaixo; não use a senha da sessão anterior.

Ao abrir o link, informe o usuário `equipe` e peça a senha atual ao responsável
pela demonstração. A senha não fica neste arquivo. O endereço funciona somente
enquanto o túnel estiver ativo e este computador estiver ligado e conectado. Se a
sessão for encerrada ou reiniciada, o link e a senha podem mudar; o responsável
deve atualizar esta seção antes de compartilhar o novo endereço.

Use perguntas fictícias, sem nomes, contatos ou relatos pessoais de saúde. As
perguntas passam pela infraestrutura do provedor do túnel e o chatbot é experimental;
não use as respostas para decisões de saúde. Veja [privacidade e limitações](privacidade.md).

## Instalar e iniciar

Requer Windows 10/11 ou macOS, Python 3.10+, Ollama aberto com `qwen2.5:7b`,
e o programa `cloudflared` instalado e disponível no PATH. Instalação oficial:
[Windows](https://developers.cloudflare.com/tunnel/downloads/) (baixe o executável
e adicione sua pasta ao PATH) ou macOS (`brew install cloudflared`). No Windows,
confira no PowerShell com `cloudflared --version`; no macOS, no Terminal com o
mesmo comando.

Crie o ambiente e instale Waitress. **Windows (PowerShell):**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-internet.txt
.\.venv\Scripts\python.exe internet_demo.py
```

**macOS (Terminal):**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-internet.txt
.venv/bin/python internet_demo.py
```

O iniciador verifica a base/modelo, cria túnel, gera senha aleatória nova e inicia
a aplicação WSGI no loopback `127.0.0.1:8010`. Não precisa executar `server.py`.
O endereço aparece no terminal. As credenciais ficam no diretório privado do
usuário: `%LOCALAPPDATA%\SUSANNA-HEALTHCHECK\internet\access.json` no Windows,
`~/Library/Application Support/SUSANNA-HEALTHCHECK/internet/access.json` no macOS,
ou `~/.local/state/SUSANNA-HEALTHCHECK/internet/access.json` no Linux. Abra esse
arquivo para consultar
`origin`, usuário `equipe` e senha. Compartilhe a senha apenas com os integrantes
convidados, separadamente do link. Todos usam a mesma credencial nesta demonstração;
não existem contas individuais ou isolamento por usuário. IDs aleatórios dão acesso
a pedidos para quem também possuir a credencial; não os compartilhe.

O navegador solicita usuário e senha via HTTP Basic sobre HTTPS. Ele pode manter
a autenticação em cache; use janela privativa e feche-a ao terminar. Para revogar
acesso, encerre a sessão e reinicie, gerando outra senha e outro link.
Não use a senha em URL nem em argumentos de terminal.

## Encerrar

Pressione Ctrl+C no terminal do iniciador: ele encerra aplicativo e túnel.
Deixe o computador ligado, conectado e sem repouso durante o uso. Não há serviço
automático nem mudança das configurações de energia. Se uma interrupção abrupta
deixar `session.lock` no diretório privado indicado acima, confirme que a sessão
anterior encerrou antes de remover esse arquivo e iniciar novamente. Não inicie
duas sessões simultâneas.

## Proteções e limites

- Todas as páginas e APIs exigem autenticação; Host e Origin aceitam a URL exata.
- Waitress atende a entrada externa; `http.server` não atende o túnel.
- Uma geração e três pedidos em espera; limite global de 10 envios/minuto e
  1.200 requisições/minuto, incluindo polling. Não há cotas individuais.
- Conexões Waitress limitadas a 32, corpo a 150.000 bytes e cabeçalhos a 8 KiB.
- Só interface, saúde do modelo e criar/consultar/cancelar pedidos são publicados.
  Métricas, prontidão detalhada, arquivos internos e Ollama não são expostos.
- Senha, token ngrok e registros do túnel ficam fora do repositório, no diretório
  privado do usuário indicado acima. Não inclua esses arquivos em pacotes, capturas
  ou compartilhamentos.

## Privacidade e limitações

As perguntas agora transitam pela infraestrutura Cloudflare, que termina HTTPS e
encaminha o tráfego pelo túnel até o computador. O modelo continua local. Não
prometer que o conteúdo nunca passa por terceiros. Não inserir dados pessoais.
O aviso da interface neste modo foi atualizado para refletir esse fluxo.

O servidor não implementa logs de conversas, mas `tunnel.log` e `server.log` no
diretório privado mantêm diagnósticos da sessão; são substituídos no próximo início.
Não foram auditadas políticas de registros da Cloudflare ou logs do Ollama.
As demais regras de retenção estão em [privacidade](privacidade.md).

Waitress: [ZPL 2.1 e documentação](https://docs.pylonsproject.org/projects/waitress/en/stable/).
Cloudflared: [Apache 2.0](https://github.com/cloudflare/cloudflared/blob/master/LICENSE).
[Quick Tunnels](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/trycloudflare/)
são para testes: limite de 200 requisições simultâneas e sem SSE. Nosso frontend usa
polling, não SSE. Disponibilidade e condições do serviço podem mudar.

## Tentativa de conexão em 25/09/2026

Ativação autorizada pelo responsável. A Cloudflare gerou endereço, mas não
registrou conexão: saída TCP 7844 expirou e o endereço retornou HTTP 530 /
erro 1033. A tentativa foi encerrada; não há demonstração pública funcionando.
O iniciador agora aguarda registro de conexão antes de anunciar o endereço.
Teste uma conexão que permita saída TCP 7844 (por exemplo, outra rede autorizada)
ou peça ao administrador da rede que verifique esse acesso. Não é necessário
abrir portas de entrada no roteador. Depois execute o iniciador novamente.

## Alternativa na mesma internet: ngrok

Cliente ngrok precisa estar no PATH. Requer conta e authtoken;
usará o ngrok como intermediário do tráfego, em lugar da Cloudflare. O modelo
continua no computador. Não há promessa de acesso se a rede também bloquear ngrok.

No terminal do VS Code, execute uma vez:

```bash
.venv/bin/python configurar_ngrok.py  # macOS
# Windows PowerShell: .\.venv\Scripts\python.exe configurar_ngrok.py
```

Cole somente o authtoken do painel e pressione Enter. A entrada fica oculta e o
segredo é salvo em `ngrok.yml` no diretório privado do usuário; não envie esse arquivo
ou o token pela conversa nem o inclua no Git. Este token é diferente da senha
`equipe` usada para entrar no chatbot.

Com Ollama aberto, inicie:

```bash
.venv/bin/python internet_demo.py --provider ngrok  # macOS
# Windows PowerShell: .\.venv\Scripts\python.exe internet_demo.py --provider ngrok
```

O iniciador espera o evento de criação do túnel HTTPS antes de iniciar o servidor.
Use a URL exibida e a senha nova no `access.json` do diretório privado. Ctrl+C encerra ambos.
A inspeção local de tráfego está desativada (`--inspect=false`, `web_addr: false`);
isso não declara ausência de registros na infraestrutura do provedor. O aviso da
interface identifica ngrok. Limites e autenticação da aplicação são preservados.
A conectividade real ainda depende de configurar o token e testar nesta rede.

Referências: [instalação oficial](https://ngrok.com/download/mac-os) e
[CLI do agente](https://ngrok.com/docs/gateway/agent/cli).

## Diagnóstico de acesso em 29/09/2026

O túnel ngrok conectou e o servidor autenticado respondeu localmente: HTTP 401
sem credenciais e HTTP 200 em `/api/health` com credenciais, com modelo pronto.
Entretanto, a conexão HTTPS ao domínio do túnel nesta rede apresentou certificado
para `*.ngrok-free.app` emitido por Fortinet (CA `FG3K2D3Z16800349`). A cadeia
não foi reconhecida: OpenSSL retornou código 21 e Chrome exibiu
`NET::ERR_CERT_AUTHORITY_INVALID`. Isso confirma interferência da inspeção TLS
no acesso; não confirma que o domínio esteja bloqueado por uma regra de conteúdo.

A correção nesta rede depende de a TI verificar a inspeção HTTPS, fornecer e
validar a cadeia oficial de certificados da organização e confirmar se ngrok é
permitido. Não instalar certificados obtidos do próprio erro nem desativar a
validação HTTPS. Testar o endereço pelos dados móveis ajuda a separar o problema
da rede do funcionamento externo do túnel.

Para acessar no próprio computador, executar `python3 server.py` e abrir
`http://127.0.0.1:8002`. Esse endereço é exclusivamente local e não serve como
link para os colegas. O acesso externo continua dependendo do túnel e da rede.
