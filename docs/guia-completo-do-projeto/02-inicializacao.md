# 2. Inicialização

## Modo local

Pré-requisitos indicados pelo projeto: Python compatível, Ollama instalado e modelo configurado. A configuração do modelo padrão está em [`server.py`](../../server.py#L24-L26). Os comandos documentados no [README do repositório](../../README.md) são:

```powershell
py -3 server.py --port 8002 --concurrency 1 --queue-size 3
```

No macOS/Linux, o README usa `python3` no lugar de `py -3`. Se Python estiver em ambiente virtual, use o caminho do executável desse ambiente.

Inicie o Ollama pelo aplicativo ou serviço próprio antes de enviar perguntas. O backend espera encontrar a API em `http://127.0.0.1:11434`; o modelo padrão é `qwen2.5:7b`, substituível pela variável `OLLAMA_MODEL`.

## O que `server.py` faz ao iniciar

1. Lê `--port`, `--concurrency` e `--queue-size`; padrões: 8002, 1 e 3.
2. Abre `ThreadingHTTPServer` somente em `127.0.0.1`.
3. Constrói uma `JobQueue` com esses limites.
4. Imprime o endereço local e o nome do modelo.
5. Atende requisições até Ctrl+C; ao encerrar, fecha fila e servidor.

Veja o ponto de entrada em [`server.py`](../../server.py#L547). Depois, abra `http://127.0.0.1:8002` no navegador.

## Saúde e prontidão

`/api/health` e `/api/ready` consultam `/api/tags` do Ollama e verificam se o nome do modelo configurado está instalado. Isso não testa previamente a busca SERPRO ou cada página gov.br: a busca só é exercitada ao enviar uma pergunta. Implementação em [`server.py`](../../server.py#L400-L433).

## Dependências opcionais

O modo normal usa bibliotecas padrão do Python, além do Ollama instalado separadamente. `requirements-analytics.txt` é para pandas/MLflow das ferramentas analíticas. `requirements-internet.txt` instala Waitress para a demonstração externa. Não é preciso instalar esses extras para abrir o chat local.
