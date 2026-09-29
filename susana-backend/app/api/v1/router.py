from fastapi import APIRouter

from app.api.v1 import chat, ckan, health, rag, services, sources, units

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(chat.router)
api_router.include_router(units.router)
api_router.include_router(services.router)
api_router.include_router(sources.router)
api_router.include_router(rag.router)
api_router.include_router(ckan.router)
