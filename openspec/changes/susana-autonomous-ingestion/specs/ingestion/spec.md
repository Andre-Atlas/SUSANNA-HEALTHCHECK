# Especificação Delta: Ingestão Autônoma e Resiliência Concorrente

## Cenários de Comportamento (WHEN / THEN)

### Cenário 1: Webhook sem Chave ou com Chave Inválida
- **GIVEN** o endpoint `/api/ingestion/webhook` ativo
- **WHEN** uma requisição POST é enviada sem o cabeçalho `X-Ingestion-Key` ou com valor diferente de `settings.ingestion_api_key`
- **THEN** o sistema SHALL responder com status HTTP 403 Forbidden
- **AND** nenhum processamento ou indexação SHALL ocorrer.

### Cenário 2: Ingestão de Documento de Domínio Não Autorizado
- **GIVEN** o payload `RawDocumentPayload`
- **WHEN** o campo `source_url` contiver um domínio fora de `ALLOWED_SUS_DOMAINS` (ex: `globo.com`, `wikipedia.org`)
- **THEN** o sistema SHALL disparar erro de validação (HTTP 422 Unprocessable Entity)
- **AND** o documento SHALL ser rejeitado antes de atingir o processador.

### Cenário 3: Ingestão Idempotente sob Rajada Concorrente
- **GIVEN** 10 requisições simultâneas contendo exatamente o mesmo documento e URL
- **WHEN** submetidas paralelamente ao `IngestionProcessor`
- **THEN** exatamente 1 requisição SHALL ser processada com `status="success"`
- **AND** 9 requisições SHALL retornar `status="skipped"` com `is_duplicate=True`
- **AND** o manifesto SHALL registrar exatamente 1 ocorrência do hash.

### Cenário 4: Invalidação Atômica do SemanticCache
- **GIVEN** uma consulta previamente cacheada no `SemanticCache`
- **WHEN** um novo documento for indexado com sucesso no ChromaDB
- **THEN** o `IngestionProcessor` SHALL invocar `cache_invalidator()`
- **AND** a entrada do cache SHALL ser imediatamente expurgada, garantindo frescor de dados na próxima requisição.

### Cenário 5: Concorrência Não-Bloqueante no Endpoint de Chat
- **GIVEN** múltiplas requisições simultâneas em `/api/chat`
- **WHEN** a inferência vetorial e o LLM estiverem processando queries pesadas
- **THEN** as operações SHALL executar dentro do worker threadpool via `run_in_threadpool`
- **AND** o event loop assíncrono SHALL permanecer livre para atender requisições de `/health` e streaming SSE sem timeout.
