import uuid

from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.providers.base import EmbeddingProvider
from app.services.ingestion_service import make_chunks, sha256_text

settings = get_settings()


class DocumentNotFoundError(LookupError):
    pass


class DocumentAlreadyProcessingError(RuntimeError):
    pass


class RAGService:
    def __init__(self, db: AsyncSession, embeddings: EmbeddingProvider):
        self.db = db
        self.embeddings = embeddings

    async def ingest_document(self, document_id: uuid.UUID) -> int:
        claim = await self.db.execute(
            update(Document)
            .where(Document.id == document_id, Document.status != "processing")
            .values(status="processing")
        )
        if claim.rowcount != 1:
            await self.db.rollback()
            if not await self.db.get(Document, document_id):
                raise DocumentNotFoundError("Documento não encontrado.")
            raise DocumentAlreadyProcessingError("Documento já está sendo processado.")

        await self.db.commit()
        document = await self.db.get(Document, document_id)
        if not document:
            raise DocumentNotFoundError("Documento não encontrado.")

        try:
            return await self.ingest(document)
        except Exception:
            await self.db.rollback()
            document = await self.db.get(Document, document_id)
            if document:
                document.status = "error"
                await self.db.commit()
            raise

    async def ingest(self, document: Document) -> int:
        chunks = make_chunks(
            document.content,
            chunk_size=settings.rag_chunk_size,
            overlap=settings.rag_chunk_overlap,
        )
        if not chunks:
            raise ValueError("Documento sem conteúdo após normalização.")

        # Gera todos os vetores antes de substituir a indexação anterior.
        embeddings = [await self.embeddings.embed(chunk) for chunk in chunks]
        expected = settings.embedding_dimensions
        for vector in embeddings:
            if len(vector) != expected:
                raise ValueError(
                    f"Dimensão de embedding incompatível: esperado {expected}, recebido {len(vector)}."
                )

        await self.db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document.id))
        for index, (content, vector) in enumerate(zip(chunks, embeddings)):
            self.db.add(
                DocumentChunk(
                    document_id=document.id,
                    chunk_index=index,
                    content=content,
                    embedding=vector,
                )
            )

        document.content_hash = sha256_text(document.content)
        document.status = "indexed"
        await self.db.commit()
        return len(chunks)
