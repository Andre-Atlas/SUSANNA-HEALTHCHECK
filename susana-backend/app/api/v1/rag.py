import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.models.source import Source
from app.providers.ollama import OllamaProvider
from app.schemas.rag import ChunkRead, DocumentCreate, DocumentRead, DocumentUpdate, IngestResponse, RagSearchRequest, RagSearchResponse, RagSearchResult, RagSearchSource
from app.services.rag_service import RAGService
from app.services.retrieval_service import RetrievalService

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.get("/documents", response_model=list[DocumentRead])
async def list_documents(db: AsyncSession = Depends(get_db)):
    return list((await db.execute(select(Document).order_by(Document.created_at.desc()))).scalars().all())


@router.get("/documents/{document_id}", response_model=DocumentRead)
async def get_document(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    document = await db.get(Document, document_id)
    if not document: raise HTTPException(404, "Documento não encontrado.")
    return document


@router.post("/documents", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def create_document(payload: DocumentCreate, db: AsyncSession = Depends(get_db)):
    if not await db.get(Source, payload.source_id):
        raise HTTPException(404, "Fonte associada não encontrada.")
    data = payload.model_dump(); data["url"] = str(payload.url)
    document = Document(**data); db.add(document); await db.commit(); await db.refresh(document)
    return document


@router.put("/documents/{document_id}", response_model=DocumentRead)
async def update_document(document_id: uuid.UUID, payload: DocumentUpdate, db: AsyncSession = Depends(get_db)):
    document = await db.get(Document, document_id)
    if not document: raise HTTPException(404, "Documento não encontrado.")
    for field, value in payload.model_dump().items():
        if field == "url": value = str(payload.url)
        setattr(document, field, value)
    document.status = "pending"
    await db.commit(); await db.refresh(document)
    return document


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    document = await db.get(Document, document_id)
    if not document: raise HTTPException(404, "Documento não encontrado.")
    await db.delete(document); await db.commit()


@router.post("/documents/{document_id}/ingest", response_model=IngestResponse)
async def ingest_document(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    document = await db.get(Document, document_id)
    if not document: raise HTTPException(404, "Documento não encontrado.")
    try:
        chunks = await RAGService(db, OllamaProvider()).ingest(document)
    except Exception as exc:
        document.status = "error"; await db.commit()
        raise HTTPException(503, "Falha ao processar o documento com o provedor de embeddings.") from exc
    return IngestResponse(document_id=document_id, status=document.status, chunks_created=chunks)


@router.get("/documents/{document_id}/chunks", response_model=list[ChunkRead])
async def list_chunks(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    if not await db.get(Document, document_id): raise HTTPException(404, "Documento não encontrado.")
    stmt = select(DocumentChunk).where(DocumentChunk.document_id == document_id).order_by(DocumentChunk.chunk_index)
    return list((await db.execute(stmt)).scalars().all())


@router.post("/search", response_model=RagSearchResponse)
async def semantic_search(payload: RagSearchRequest, db: AsyncSession = Depends(get_db)):
    try:
        results = await RetrievalService(db, OllamaProvider()).search(payload.query, payload.top_k)
    except Exception as exc:
        raise HTTPException(503, "Não foi possível executar a busca semântica.") from exc
    return RagSearchResponse(
        query=payload.query,
        results=[RagSearchResult(
            document_id=item["document_id"], chunk_id=item["chunk_id"], score=round(item["score"], 4),
            content=item["content"], source=RagSearchSource(name=item["source_name"], url=item["source_url"])
        ) for item in results],
    )
