# =========================================================================
# FastAPI Backend — Production Dockerfile
# Suporte nativo a arquiteturas ARM64 (Ampere A1 OCI) e AMD64 (x86_64)
# =========================================================================

FROM python:3.11-slim

WORKDIR /app

# Instala ferramentas essenciais do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python em camada com cache
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Pré-download do modelo SentenceTransformers durante o build da imagem
# Isso elimina o cold start em produção, permitindo boot instantâneo do container
ENV HF_HOME=/app/.cache/huggingface
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"

# Copia código da aplicação e artefatos
COPY app/ ./app/
COPY data/ ./data/
COPY ml/ ./ml/

# Cria diretórios de runtime com permissões adequadas
RUN mkdir -p /app/data/chroma_db /app/data/corpus /app/data/db /app/mlruns && \
    useradd -m -u 1001 appuser && \
    chown -R appuser:appuser /app

USER appuser

ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV HOST=0.0.0.0

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
