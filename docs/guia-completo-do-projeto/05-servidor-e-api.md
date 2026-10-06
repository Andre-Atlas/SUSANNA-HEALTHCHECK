# 5. Servidor e API

## Servidor local

`server.py` usa `ThreadingHTTPServer`, mas o processamento caro é limitado pela `JobQueue`. O bind em `127.0.0.1` restringe a entrada ao computador local. O handler também valida Host e Origin e restringe os arquivos estáticos servidos.

## Rotas locais

| Método e caminho | Função |
|---|---|
| `GET /` e `GET /index.html` | Entrega o HTML. |
| `GET /styles.css`, `GET /app.js` | Entrega recursos da interface. |
| `GET /api/health` | Verifica conexão Ollama/modelo instalado. |
| `GET /api/ready` | Retorna prontidão do modelo; não testa a internet de busca antecipadamente. |
| `GET /api/metrics` | Retorna configuração da fila e métricas recentes agregadas. |
| `POST /api/jobs` | Valida e enfileira mensagem; responde `202` com estado/ID. |
| `GET /api/jobs/{id}` | Consulta estado e, ao concluir, resultado. |
| `DELETE /api/jobs/{id}` | Solicita cancelamento. |
| `POST /api/chat` | Forma síncrona mantida por compatibilidade; usa a mesma fila. |

Handler e rotas: [`server.py`](../../server.py#L358-L506).

## Contrato e limites de entrada

O POST exige JSON, corpo de até 150.000 bytes e entre 1 e 13 mensagens, alternando `user` e `assistant`, sempre terminando com `user`. Limites individuais: 3.000 caracteres para usuário e 12.000 para assistant. Ver [`validate_messages()`](../../server.py#L339-L355).

Erros usuais incluem 400 para JSON/histórico inválido, 403 para Host/Origin não permitido, 404 para rota ou job inexistente, 415 para tipo de conteúdo incorreto, 429 para fila cheia, 502/503 para falhas do modelo/serviços e 504 para timeout. Os caminhos específicos de erro estão em [`Handler`](../../server.py#L462-L506) e [`process_messages()`](../../server.py#L509-L534).

## Nota sobre SQLite

Há um `except sqlite3.Error` em `process_messages`, mas a função `retrieve()` do modo de chat chama busca online em SERPRO/gov.br. A presença desse tratamento de erro não quer dizer que o chat atual leia `data/knowledge.sqlite3`; veja [fontes SQLite e modo offline](09-fontes-sqlite-e-modos-offline.md).
