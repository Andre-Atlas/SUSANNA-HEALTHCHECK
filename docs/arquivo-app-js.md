# `app.js`

Controla a interface no navegador: valida o envio, apresenta mensagens e fontes, consulta o estado do servidor, atualiza o progresso e permite cancelar uma solicitação.

O fluxo assíncrono cria um pedido em `/api/jobs`, consulta `/api/jobs/{id}` periodicamente e envia DELETE para cancelar. Também verifica `/api/health`. A busca e a geração são feitas no backend Python, não neste arquivo.

**Ponto para revisar:** o texto de boas-vindas atualmente diz que o chatbot consulta documentos locais e não pesquisa na internet ao vivo. Isso contradiz o fluxo atual de `server.py`, que busca conteúdo gov.br. O texto é exibido ao usuário e deve ser alinhado ao comportamento real.
