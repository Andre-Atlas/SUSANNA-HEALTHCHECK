import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.chunk import DocumentChunk
from app.providers.ollama import OllamaProvider
from app.repositories.document_repository import DocumentRepository
from app.repositories.source_repository import SourceRepository
from app.schemas.rag import (
    ChunkRead,
    DocumentCreate,
    DocumentRead,
    DocumentUpdate,
    IngestResponse,
    RagSearchRequest,
    RagSearchResponse,
    RagSearchResult,
    RagSearchSource,
)
from app.services.document_service import DocumentService
from app.services.rag_service import (
    DocumentAlreadyProcessingError,
    DocumentNotFoundError,
    RAGService,
)
from app.services.retrieval_service import RetrievalService

router = APIRouter(prefix="/rag", tags=["RAG"])


def document_service(db: AsyncSession) -> DocumentService:
    return DocumentService(DocumentRepository(db), SourceRepository(db))


@router.get("/documents", response_model=list[DocumentRead], summary="Lista documentos")
async def list_documents(db: AsyncSession = Depends(get_db)):
    return await document_service(db).list()


@router.get("/documents/{document_id}", response_model=DocumentRead, summary="Obtém documento")
async def get_document(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    document = await document_service(db).get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    return document


@router.post("/documents", response_model=DocumentRead, status_code=status.HTTP_201_CREATED, summary="Cadastra documento")
async def create_document(payload: DocumentCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await document_service(db).create(payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/documents/{document_id}", response_model=DocumentRead, summary="Atualiza documento")
async def update_document(
    document_id: uuid.UUID, payload: DocumentUpdate, db: AsyncSession = Depends(get_db)
):
    service = document_service(db)
    document = await service.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    return await service.update(document, payload)


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove documento")
async def delete_document(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = document_service(db)
    document = await service.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    await service.delete(document)


@router.post("/documents/{document_id}/ingest", response_model=IngestResponse, summary="Indexa documento")
async def ingest_document(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    rag_service = RAGService(db, OllamaProvider())
    try:
        chunks = await rag_service.ingest_document(document_id)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DocumentAlreadyProcessingError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Falha ao processar o documento com o provedor de embeddings.",
        ) from exc
    document = await document_service(db).get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    return IngestResponse(document_id=document_id, status=document.status, chunks_created=chunks)


@router.get("/documents/{document_id}/chunks", response_model=list[ChunkRead], summary="Lista chunks do documento")
async def list_chunks(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    if not await document_service(db).get(document_id):
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    stmt = (
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
    )
    return list((await db.execute(stmt)).scalars().all())


@router.post("/search", response_model=RagSearchResponse, summary="Busca semântica")
async def semantic_search(payload: RagSearchRequest, db: AsyncSession = Depends(get_db)):
    try:
        results = await RetrievalService(db, OllamaProvider()).search(payload.query, payload.top_k)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Não foi possível executar a busca semântica.") from exc
    return RagSearchResponse(
        query=payload.query,
        results=[
            RagSearchResult(
                document_id=item["document_id"],
                chunk_id=item["chunk_id"],
                score=round(item["score"], 4),
                content=item["content"],
                source=RagSearchSource(name=item["source_name"], url=item["source_url"]),
            )
            for item in results
        ],
    )
