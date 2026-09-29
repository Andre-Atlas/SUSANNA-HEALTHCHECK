# Runtime local

## Ordem recomendada

```text
PostgreSQL + pgvector
        ↓
Alembic
        ↓
FastAPI
        ↓
Ollama
        ↓
modelos configurados
        ↓
corpus real
        ↓
ingestão
        ↓
/rag/search
        ↓
/chat
```

## Estado de desenvolvimento

- O processo da API deve usar um único worker enquanto a sessão conversacional for mantida em memória.
- O seed é DEMO e não deve ser usado como fonte oficial.
- `EMBEDDING_DIMENSIONS` precisa estar alinhado com o modelo configurado antes da primeira ingestão.
- Não incluir dados pessoais ou clínicos reais no seed ou nos testes.
