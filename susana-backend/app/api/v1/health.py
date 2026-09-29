from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db

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
    ollama = "error"
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
        import httpx
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{settings.ollama_base_url.rstrip('/')}/api/tags")
            ollama = "ok" if response.is_success else "error"
    except Exception:
        ollama = "error"
    return {"postgres": postgres, "pgvector": pgvector, "ollama": ollama}
