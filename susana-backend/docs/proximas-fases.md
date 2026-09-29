# Próximas fases do backend

## Fase A — Ambiente

1. Definir o modelo de chat do Ollama.
2. Definir o modelo de embeddings.
3. Confirmar a dimensão do embedding.
4. Rodar `python -m scripts.check_ollama`.

## Fase B — Banco

1. Subir PostgreSQL/pgvector.
2. Executar `alembic upgrade head`.
3. Validar `/health/dependencies`.

## Fase C — Corpus

1. Cadastrar fontes oficiais.
2. Inserir documentos reais.
3. Ingerir documentos.
4. Conferir chunks.
5. Testar `/rag/search`.

## Fase D — RAG

Ajustar somente com evidência de teste:

- chunk size;
- overlap;
- top_k;
- threshold;
- modelo de embeddings;
- prompt.

## Fase E — Dados estruturados

Importar unidades e serviços reais, mantendo `source_id` preenchido para preservar proveniência.

## Fase F — Avaliação

Criar e executar perguntas normais, ambíguas, fora do escopo e sem resposta no corpus.

## Fase G — Frontend

Substituir o comportamento simulado do protótipo React pelo `POST /api/v1/chat` e pelas consultas de unidades/serviços.
