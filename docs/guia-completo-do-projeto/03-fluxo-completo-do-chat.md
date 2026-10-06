# 3. Fluxo completo do chat

Este é o percurso de uma pergunta no modo local.

1. **Interface:** `app.js` coloca a mensagem no histórico em memória e envia `POST /api/jobs` com JSON `{ "messages": [...] }`.
2. **Validação HTTP:** `server.py` verifica rota, origem/host, tipo de conteúdo, tamanho do corpo, papéis alternados e limites por mensagem.
3. **Fila:** `jobs.py` cria ID aleatório, registra o trabalho como `queued` e o worker o processa de acordo com a concorrência.
4. **Contexto:** `resolve_question()` decide se é uma pergunta independente ou uma das formas curtas de acompanhamento reconhecidas. Respostas antigas da IA não viram evidência.
5. **Recuperação:** `retrieve()` chama `search_gov_br()`. O fluxo de busca está em [Busca e fontes](06-busca-e-fontes.md).
6. **Prompt:** `build_prompt()` combina instruções do assistente, pergunta, contexto de acompanhamento e trechos identificados com IDs como `[1]`. Reduz histórico/fontes se ultrapassar o orçamento configurado.
7. **Geração:** o backend pede ao Ollama uma resposta curta e citada.
8. **Validação do formato:** o servidor rejeita resposta vazia, referências inexistentes, parágrafos sem citação ou recortes por limite. Uma segunda tentativa só é feita para certas falhas de formato de citação.
9. **Revisão documental:** quando o formato é aceitável, `verify_grounding()` faz outra chamada ao Ollama com a pergunta, os parágrafos e as fontes citadas.
10. **Decisão:** o backend verifica o JSON do revisor, cobertura dos parágrafos e IDs de fontes. Em caso de falta de apoio, conflito ou alegação não apoiada, falha de modo conservador e retorna mensagem de insuficiência/recusa.
11. **Exibição:** `app.js` recebe o resultado final pelo polling do job e mostra mensagem, status e links das fontes.

Orquestração: [`process_messages()`](../../server.py#L509-L534); validação e geração: [`server.py`](../../server.py#L280-L336); cliente do navegador: [`app.js`](../../app.js#L108-L190).

## Dados que transitam

- Pergunta e histórico recente: navegador → backend.
- Consulta lexical reduzida: backend → busca SERPRO.
- HTML: backend ← páginas gov.br aceitas.
- Pergunta, instruções e trechos: backend → Ollama local, na geração.
- Pergunta, resposta, parágrafos e fontes citadas: backend → Ollama local, na revisão.
- Resultado, status e fontes: backend → navegador.

No modo externo, navegador e backend também passam pela infraestrutura do provedor do túnel; detalhes em [Demonstração externa](11-demonstracao-externa.md). Recomendações de dados e retenção estão em [Segurança e privacidade](13-seguranca-privacidade-e-limitacoes.md).
