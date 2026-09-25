# Demonstração temporária pela internet

Modo solicitado em 25/09/2026. Usa o computador como servidor e um Quick Tunnel
Cloudflare, sem contratação de hospedagem ou domínio. Link aleatório e temporário;
sem garantia de disponibilidade. É uma demonstração restrita, não entrega final
aprovada: a falha F01 do revisor permanece aberta.

## Iniciar

Mantenha Ollama aberto com `qwen2.5:7b`. Na pasta do projeto:

```bash
.venv/bin/python internet_demo.py
```

A instalação deste ambiente inclui Waitress 3.0.2 na `.venv` e cloudflared em
`.internet/bin/`. Para reinstalar o Python da demonstração:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-internet.txt
```

O iniciador verifica a base/modelo, cria túnel, gera senha aleatória nova e inicia
a aplicação WSGI no loopback `127.0.0.1:8010`. Não precisa executar `server.py`.
O endereço aparece no terminal. Abra `.internet/access.json` para consultar
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
deixar `.internet/session.lock`, confirme que a sessão anterior encerrou antes de
remover esse arquivo e iniciar novamente. Não inicie duas sessões simultâneas.

## Proteções e limites

- Todas as páginas e APIs exigem autenticação; Host e Origin aceitam a URL exata.
- Waitress atende a entrada externa; `http.server` não atende o túnel.
- Uma geração e três pedidos em espera; limite global de 10 envios/minuto e
  1.200 requisições/minuto, incluindo polling. Não há cotas individuais.
- Conexões Waitress limitadas a 32, corpo a 150.000 bytes e cabeçalhos a 8 KiB.
- Só interface, saúde do modelo e criar/consultar/cancelar pedidos são publicados.
  Métricas, prontidão detalhada, arquivos internos e Ollama não são expostos.
- Senha e registros do túnel ficam em `.internet/`, ignorada pelo Git, com pasta
  de acesso restrito. Não incluir essa pasta em pacotes, capturas ou compartilhamentos.

## Privacidade e limitações

As perguntas agora transitam pela infraestrutura Cloudflare, que termina HTTPS e
encaminha o tráfego pelo túnel até o computador. O modelo continua local. Não
prometer que o conteúdo nunca passa por terceiros. Não inserir dados pessoais.
O aviso da interface neste modo foi atualizado para refletir esse fluxo.

O servidor não implementa logs de conversas, mas `.internet/tunnel.log` e
`server.log` mantêm diagnósticos da sessão; são substituídos no próximo início.
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
