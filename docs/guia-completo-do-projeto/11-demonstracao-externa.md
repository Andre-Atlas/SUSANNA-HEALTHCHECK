# 11. Demonstração externa opcional

O modo externo permite que pessoas com a credencial acessem temporariamente o computador por um túnel. Não é necessário para o chat local e não representa uma hospedagem permanente.

## Sequência

1. `internet_demo.py` localiza `cloudflared` ou `ngrok` no PATH ou em `.internet/bin/`.
2. Verifica porta local 8010, banco SQLite via `operations.inspect_database()` e disponibilidade do modelo no Ollama.
3. Cria trava e arquivos privados em diretório do usuário via `internet_state.py`.
4. Inicia o túnel para `http://127.0.0.1:8010`, espera a URL, gera senha temporária e grava configuração privada.
5. Inicia `internet_app.py`, servido por Waitress em loopback. Ctrl+C encerra processos iniciados e remove a trava.

Código: [`internet_demo.py`](../../internet_demo.py#L17-L103), [`internet_state.py`](../../internet_state.py#L1-L20), [`internet_app.py`](../../internet_app.py#L99-L113).

## Entrada autenticada

`internet_app.py` verifica host, origin e autenticação HTTP Basic, aplica limites de requisição e expõe apenas arquivos estáticos, `/api/health` e operações `/api/jobs`. A fila remota padrão é um worker e três itens em espera. O trabalho depois reutiliza `process_messages()` de `server.py`.

Waitress, túnel e provedor são componentes separados. O provedor do túnel encaminha o tráfego externo; o modelo permanece no computador. Perguntas passam pela infraestrutura do provedor, logo esse modo tem fluxo de privacidade diferente do loopback local. Não use dados pessoais.

## Divergência que exige atenção

O iniciador atual chama `inspect_database()` e exige o SQLite local, embora o chat online use busca gov.br e a documentação geral diga que o SQLite não é necessário para conversar localmente. Portanto, a demonstração externa possui esse pré-requisito adicional. O motivo funcional exato para essa verificação não está demonstrado pelo caminho de perguntas compartilhado; registre-o como dependência do preflight, não como fonte da resposta.
