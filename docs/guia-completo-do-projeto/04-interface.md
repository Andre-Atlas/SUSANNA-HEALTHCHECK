# 4. Interface

## Arquivos

- [`index.html`](../../index.html): estrutura semântica da página, menu, área do chat, sugestões e campos.
- [`styles.css`](../../styles.css): identidade visual, estados, leiaute e adaptação de tela.
- [`app.js`](../../app.js): comportamento no navegador, histórico de conversa, chamadas HTTP, polling, cancelamento, estados de espera, fontes e erros.

## Chamadas do navegador

Ao carregar, o JavaScript consulta `GET /api/health`. Ao enviar uma pergunta, usa `POST /api/jobs`; recebe um ID e acompanha `GET /api/jobs/{id}` até o término. Cancelar ou sair da página pode enviar `DELETE /api/jobs/{id}`. O envio é assíncrono: os fragmentos recebidos do Ollama não são exibidos como resposta parcial; o navegador apresenta o resultado quando o trabalho termina.

Os endpoints e formatos estão em [`app.js`](../../app.js#L68-L92) e [`app.js`](../../app.js#L108-L190).

## Histórico

O histórico é uma variável JavaScript em memória e pode ser apagado ou reiniciado ao recarregar a página. Ele não é persistido por `localStorage` ou `sessionStorage` no código atual. O servidor ainda limita e interpreta o histórico recebido.

## Texto de boas-vindas divergente

O texto inicial definido em `app.js` diz que são consultados documentos locais “sem pesquisa na internet ao vivo”. Isso está em desacordo com o caminho atual de `server.py`, cujo `retrieve()` chama `search_gov_br()`. É um texto visível para o usuário que merece atualização; este guia não alterou o código.
