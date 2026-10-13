"""Router FastAPI para Webhook de ingestão e monitoramento de novos dados."""
from __future__ import annotations

import os
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel

from app.config import get_settings
from app.ingestion.contracts import IngestionResult, RawDocumentPayload
from app.ingestion.processor import IngestionProcessor

router = APIRouter(prefix="/api/ingestion", tags=["Ingestão Autônoma"])

_processor_instance: Optional[IngestionProcessor] = None


def get_processor() -> IngestionProcessor:
    """Dependency injection para o processador global de ingestão."""
    global _processor_instance
    if _processor_instance is None:
        # Importação tardia para acessar o retriever global do main se disponível
        from app.main import pipeline
        retriever = pipeline.retriever if pipeline is not None else None
        cache_invalidator = (
            pipeline.semantic_cache.clear
            if (pipeline is not None and pipeline.semantic_cache is not None)
            else None
        )
        _processor_instance = IngestionProcessor(
            retriever=retriever, cache_invalidator=cache_invalidator
        )
    return _processor_instance


def set_processor(processor: IngestionProcessor) -> None:
    """Permite sobrescrever o processador durante testes."""
    global _processor_instance
    _processor_instance = processor


def verify_ingestion_key(
    x_ingestion_key: Optional[str] = Header(None, alias="X-Ingestion-Key")
) -> str:
    """Valida a chave secreta de autenticação do webhook de forma fail-closed."""
    settings = get_settings()
    expected_key = settings.ingestion_api_key or os.getenv("INGESTION_API_KEY")
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Configuração de segurança pendente: chave INGESTION_API_KEY não definida.",
        )
    if not x_ingestion_key or x_ingestion_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: Chave X-Ingestion-Key inválida ou ausente.",
        )
    return x_ingestion_key


class IngestionStatusResponse(BaseModel):
    total_documents: int
    storage_path: str
    last_indexed_at: Optional[str] = None


@router.get("/status", response_model=IngestionStatusResponse)
async def get_ingestion_status(
    processor: IngestionProcessor = Depends(get_processor),
):
    """Retorna o status do manifesto de documentos ingeridos autonomamente."""
    docs = processor._manifest.get("documents", {})
    last_date = None
    if docs:
        last_date = max((d.get("indexed_at") for d in docs.values() if "indexed_at" in d), default=None)
    return IngestionStatusResponse(
        total_documents=len(docs),
        storage_path=str(processor.storage_dir),
        last_indexed_at=last_date,
    )


@router.post("/webhook", response_model=IngestionResult)
async def receive_sus_document_webhook(
    payload: RawDocumentPayload,
    _: str = Depends(verify_ingestion_key),
    processor: IngestionProcessor = Depends(get_processor),
):
    """
    Recebe um novo documento ou comunicado oficial do SUS via Webhook.
    Deduplica por hash SHA-256 e indexa dinamicamente no ChromaDB.
    """
    result = processor.process_document(payload)
    if result.status == "error":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=result.message)
    return result
