# `server.py`

É o servidor HTTP local e o coordenador principal do chat. Entrega `index.html`, `styles.css` e `app.js`; valida requisições e disponibiliza rotas de saúde, prontidão, métricas e trabalhos assíncronos.

Ao processar uma pergunta, resolve o contexto, chama a busca de `govbr_search.py`, monta o prompt, chama o Ollama para gerar e revisar a resposta, aplica as regras de `answer_policy.py` e devolve texto, estado e fontes. O modelo padrão é `qwen2.5:7b`, ajustável por `OLLAMA_MODEL`. Inicia em `127.0.0.1` e, por padrão, na porta 8002.

Apesar de importar `sqlite3` e conter tratamento para um erro SQLite, a busca online usada pelo chat atualmente delega a `search_gov_br`; a base local é voltada a avaliação e manutenção offline.
