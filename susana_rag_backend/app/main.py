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
from starlette.concurrency import run_in_threadpool

from app.config import get_settings
from app.llm.ollama_adapter import OllamaAdapter
from app.rag.corpus import discover_corpus_files, load_corpus
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
    embedder = Embedder(settings.embedding_model, settings.embedding_max_seq_length)
    
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
    
    from app.ingestion.processor import IngestionProcessor
    from app.rag.online_search import ScopedOnlineSearchComplementer

    ingestion_processor = IngestionProcessor(
        retriever=retriever,
        storage_dir=settings.docs_dir,
        cache_invalidator=semantic_cache.clear,
    )
    online_search = ScopedOnlineSearchComplementer(
        retriever=retriever,
        ingestion_processor=ingestion_processor,
        guardrails=guardrails,
        timeout_seconds=settings.online_search_timeout_s,
        max_results=settings.online_search_max_results,
    )

    pipeline = RAGPipeline(
        llm=llm,
        embedder=embedder,
        retriever=retriever,
        semantic_cache=semantic_cache,
        similarity_threshold=settings.similarity_threshold,
        confident_threshold=settings.relevance_confident_threshold,
        top_k=settings.top_k,
        mlflow_enabled=settings.mlflow_log_requests,
        online_search=online_search,
    )

    # 3. Verificação do Corpus e Auto-Indexação Inteligente
    if pipeline.retriever.count() == 0:
        logger.info("Índice vazio detectado! Iniciando indexação inicial de bootstrap...")
        corpus_files = discover_corpus_files([settings.docs_dir, settings.project_corpus_dir, settings.legacy_docs_file])
        blocks = load_corpus(corpus_files)
        if blocks:
            pipeline.retriever.index(blocks)
            logger.info("Indexação concluída: %d blocos inseridos no ChromaDB.", pipeline.retriever.count())
        else:
            logger.warning("Nenhum arquivo encontrado nas pastas do Corpus!")
    else:
        logger.info("Índice já preenchido. Contém %d blocos. Inicialização rápida ativada.", pipeline.retriever.count())

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

cors_list = (
    [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    if settings.cors_origins != "*"
    else ["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_list,
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

    # 1. Guardrails — bloqueia perguntas clínicas (non-blocking threadpool)
    if await run_in_threadpool(guardrails.is_clinical, msg):
        latency = int((time.perf_counter() - t0) * 1000)
        logger.info("BLOCKED clinical query: %s (latency=%dms)", msg[:80], latency)
        return ChatResponse(
            response=(
                "Desculpe, não posso ajudar com essa questão. "
                "A SUSANNA fornece apenas informações administrativas e institucionais da SES-DF. "
                "Para orientações clínicas, procure uma Unidade Básica de Saúde (UBS) ou ligue para o SAMU 192."
            ),
            is_blocked=True,
            latency_ms=latency,
        )

    # 2. RAG — busca vetorial + LLM (non-blocking threadpool)
    try:
        result = await run_in_threadpool(pipeline.query, msg)
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

# Include autonomous ingestion webhook router
from app.ingestion.webhook import router as ingestion_router
app.include_router(ingestion_router)

# Include citizen identity and profile router
from app.citizen.router import router as citizen_router
app.include_router(citizen_router)

# Include multi-session chat history router
from app.chat_sessions.router import router as chat_sessions_router
app.include_router(chat_sessions_router)

# Include healthcare units and RA directory router
from app.units.router import router as units_router
app.include_router(units_router)

# Include official PNI vaccine guide router
from app.vaccines.router import router as vaccines_router
app.include_router(vaccines_router)

# Include official epidemiological surveillance router
from app.surveillance.router import router as surveillance_router
app.include_router(surveillance_router)


class OnlineSearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    auto_ingest: bool = True


@app.post("/api/search/online")
async def online_search_endpoint(req: OnlineSearchRequest):
    if pipeline is None or getattr(pipeline, "online_search", None) is None:
        raise HTTPException(status_code=503, detail="Mecanismo de pesquisa online não disponível.")

    query = req.query.strip()
    if await run_in_threadpool(guardrails.is_clinical, query):
        return {
            "query": query,
            "results_found": 0,
            "is_blocked": True,
            "message": "Consulta clínica bloqueada por diretrizes éticas e de segurança do SUS.",
            "chunks": [],
        }

    chunks = await pipeline.online_search.search_async(query)
    return {
        "query": query,
        "results_found": len(chunks),
        "is_blocked": False,
        "chunks": [{"id": c.id, "source": c.source, "url": c.url, "text": c.text} for c in chunks],
    }
