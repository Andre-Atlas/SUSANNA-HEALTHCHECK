from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.providers.base import EmbeddingProvider
from app.services.ingestion_service import make_chunks, sha256_text


class RAGService:
    def __init__(self, db: AsyncSession, embeddings: EmbeddingProvider):
        self.db = db
        self.embeddings = embeddings

    async def ingest(self, document: Document) -> int:
        settings = get_settings()
        await self.db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document.id))
        chunks = make_chunks(document.content, settings.rag_chunk_size, settings.rag_chunk_overlap)
        for index, content in enumerate(chunks):
            vector = await self.embeddings.embed(content)
            self.db.add(DocumentChunk(document_id=document.id, chunk_index=index, content=content, embedding=vector))
        document.content_hash = sha256_text(document.content)
        document.status = "indexed"
        await self.db.commit()
        return len(chunks)
