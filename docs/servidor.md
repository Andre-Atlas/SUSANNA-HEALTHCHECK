O `server.py` é o backend local do projeto: ele entrega os arquivos da interface, recebe perguntas e coordena a busca, a geração e a revisão das respostas. **Ele só aceita conexões locais** (`127.0.0.1`), então o endereço `http://127.0.0.1:8002` funciona no computador onde o servidor está rodando.

### O que acontece quando você envia uma pergunta

1. **O servidor recebe e valida a requisição.** A interface envia uma requisição HTTP com a conversa em JSON. O servidor verifica se o formato está correto, se a mensagem não excede o limite e se a origem é local.

2. **O pedido entra numa fila.** Com o comando que você usa, `--concurrency 1 --queue-size 3`, o servidor processa uma pergunta por vez e aceita até três pedidos esperando. Se a capacidade estiver cheia, retorna erro `429`. O servidor HTTP pode atender outras conexões enquanto isso, mas o processamento do modelo continua limitado pela concorrência configurada.

3. **O servidor prepara a pergunta e busca fontes.** Ele identifica se a mensagem depende de uma pergunta anterior. Em seguida, consulta páginas do gov.br — por meio de buscas específicas para alguns temas e da busca geral para os demais. A busca ocorre na internet; só páginas HTTPS em domínios `gov.br` são aceitas como fontes.

4. **O Ollama escreve uma resposta localmente.** O servidor envia ao Ollama a pergunta e os trechos encontrados. Por padrão, usa o modelo `qwen2.5:7b`, acessível em `127.0.0.1:11434`. O Ollama não é o servidor da página: é outro serviço local que o backend consulta para gerar texto.

5. **A resposta passa por verificações.** O servidor verifica o formato das citações e pede ao Ollama uma revisão do apoio documental. Se as fontes não responderem à pergunta, houver afirmações sem apoio ou a revisão falhar, ele devolve uma resposta cautelosa em vez de apresentar a resposta como confirmada. Por isso, a interface só mostra o resultado após essa etapa.

6. **O servidor devolve a resposta e as fontes à interface.** O endpoint `/api/chat` espera o processamento terminar. Também existem endpoints de trabalhos assíncronos (`/api/jobs`), estado (`/api/jobs/{id}`), cancelamento e métricas.

### Endpoints de verificação

- `/api/health` verifica se o Ollama responde e se o modelo configurado está instalado.
- `/api/ready` verifica a disponibilidade do modelo para uso.
- `/api/metrics` mostra a fila e tempos recentes, como busca, geração, revisão e duração total.

Assim, a demora total pode incluir **fila + busca na internet + geração pelo Ollama + revisão**. Os tempos em `/api/metrics` ajudam a identificar qual etapa está levando mais tempo.