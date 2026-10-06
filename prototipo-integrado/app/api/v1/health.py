from fastapi import APIRouter, Depends
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db
from app.models.document import Document

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", summary="Verifica a saúde básica da API")
async def health() -> dict[str, str]:
    settings = get_settings()
    return {"status": "ok", "version": settings.app_version}


@router.get("/dependencies", summary="Verifica PostgreSQL, pgvector e Ollama")
async def dependencies(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    settings = get_settings()
    postgres = "ok"
    pgvector = "error"
    indexed_documents = "error"
    ollama = "error"
    ollama_chat = "error"
    ollama_embeddings = "error"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        postgres = "error"
    try:
        row = (await db.execute(text("SELECT extversion FROM pg_extension WHERE extname = 'vector'"))).first()
        pgvector = "ok" if row else "error"
    except Exception:
        pgvector = "error"
    try:
        count = await db.scalar(
            select(func.count())
            .select_from(Document)
            .where(Document.status == "indexed")
        )
        indexed_documents = str(count or 0)
    except Exception:
        indexed_documents = "error"
    try:
        import httpx

        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{settings.ollama_base_url.rstrip('/')}/api/tags")
            if response.is_success:
                installed_models = {
                    model.get("name") for model in response.json().get("models", [])
                }
                ollama_chat = (
                    "ok"
                    if settings.ollama_model in installed_models
                    else "not_configured"
                    if not settings.ollama_model
                    else "not_installed"
                )
                ollama_embeddings = (
                    "ok"
                    if settings.embedding_model in installed_models
                    else "not_configured"
                    if not settings.embedding_model
                    else "not_installed"
                )
                ollama = (
                    "ok"
                    if ollama_chat == "ok" and ollama_embeddings == "ok"
                    else "error"
                )
    except Exception:
        ollama = "error"
    return {
        "postgres": postgres,
        "pgvector": pgvector,
        "indexed_documents": indexed_documents,
        "ollama": ollama,
        "ollama_chat": ollama_chat,
        "ollama_embeddings": ollama_embeddings,
    }
