"""
Susana RAG Backend — FastAPI Application
=========================================
Assistente virtual administrativa do SUS-DF.
Usa LLM Local (Ollama) e Guarda semântica.
"""
from __future__ import annotations

import logging
import os
import time
from contextlib import asynccontextmanager

import mlflow
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.config import get_settings
from app.llm.ollama_adapter import OllamaAdapter
from app.rag.corpus import load_corpus
from app.rag.embeddings import Embedder
from app.rag.guardrails import GuardrailsClassifier
from app.rag.pipeline import RAGPipeline
from app.rag.retriever import ChromaRetriever, SemanticCache

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("susana")

# ---------------------------------------------------------------------------
# Globals for dependency injection
# ---------------------------------------------------------------------------
settings = get_settings()
guardrails = GuardrailsClassifier()
pipeline: RAGPipeline | None = None


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(application: FastAPI):
    global pipeline
    logger.info("Inicializando Pipeline Susana...")
    
    # 1. Configurar MLflow
    os.makedirs(settings.mlflow_artifact_root, exist_ok=True)
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    try:
        mlflow.set_experiment("susana-rag")
    except Exception as e:
        logger.warning("Falha ao configurar MLflow: %s", e)

    # 2. Inicializar Componentes (Ports)
    logger.info("Carregando Embedder: %s", settings.embedding_model)
    embedder = Embedder(settings.embedding_model)
    
    logger.info("Carregando Retriever em %s", settings.chroma_dir)
    retriever = ChromaRetriever(embedder, settings.chroma_dir)
    
    logger.info("Carregando Ollama Adapter (%s em %s)", settings.ollama_model, settings.ollama_base_url)
    llm = OllamaAdapter(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        timeout_s=settings.llm_timeout_s,
        keep_alive=settings.llm_keep_alive,
        num_predict=settings.llm_num_predict,
    )
    
    semantic_cache = SemanticCache(max_distance=0.08)
    
    pipeline = RAGPipeline(
        llm=llm,
        embedder=embedder,
        retriever=retriever,
        semantic_cache=semantic_cache,
        similarity_threshold=settings.similarity_threshold,
        mlflow_enabled=settings.mlflow_log_requests,
    )

    # 3. Indexar Corpus
    if True: # Forçar re-indexação para puxar os novos dados
        logger.info("Lendo corpus de %s", settings.docs_dir)
        if settings.docs_dir.exists():
            txt_files = list(settings.docs_dir.glob("*.txt"))
            blocks = load_corpus(txt_files)
            indexed = pipeline.retriever.index(blocks)
            logger.info("Indexação concluída: %d blocos adicionados/atualizados.", indexed)
        else:
            logger.warning("Diretório de corpus não encontrado: %s", settings.docs_dir)

    # 4. Warm-up LLM
    if llm.is_ready():
        llm.warm_up()
    else:
        logger.warning("LLM Ollama (%s) não está disponível no momento.", settings.ollama_model)

    logger.info("Pipeline pronto. %d docs na coleção.", pipeline.retriever.count())
    yield
    logger.info("Shutting down Susana Backend.")


# ---------------------------------------------------------------------------
# App & Middleware
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Susana RAG Backend",
    version="2.0.0",
    description="Assistente virtual administrativa da SES-DF.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# DTOs
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    response: str
    source: str | None = None
    is_blocked: bool = False
    latency_ms: int = 0


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
async def healthcheck():
    return {"status": "ok", "pipeline_ready": pipeline is not None}


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline inicializando.")

    t0 = time.perf_counter()
    msg = req.message.strip()

    # 1. Guardrails — bloqueia perguntas clínicas
    if guardrails.is_clinical(msg):
        latency = int((time.perf_counter() - t0) * 1000)
        logger.info("BLOCKED clinical query: %s (latency=%dms)", msg[:80], latency)
        return ChatResponse(
            response=(
                "Desculpe, não posso ajudar com essa questão. "
                "A Susana fornece apenas informações administrativas e institucionais da SES-DF. "
                "Para orientações clínicas, procure uma Unidade Básica de Saúde (UBS) ou ligue para o SAMU 192."
            ),
            is_blocked=True,
            latency_ms=latency,
        )

    # 2. RAG — busca vetorial + LLM
    try:
        result = pipeline.query(msg)
    except Exception:
        logger.exception("Erro no pipeline RAG para query: %s", msg[:80])
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao processar sua pergunta. Tente novamente.",
        )

    latency = int((time.perf_counter() - t0) * 1000)
    logger.info(
        "ANSWERED query: %s | source=%s | latency=%dms",
        msg[:80],
        result.get("source", "none"),
        latency,
    )

    return ChatResponse(
        response=result["response"],
        source=result.get("source"),
        is_blocked=False,
        latency_ms=latency,
    )

# Include streaming router
from app.routers_stream import router as stream_router
app.include_router(stream_router)
