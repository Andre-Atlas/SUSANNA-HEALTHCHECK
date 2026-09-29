from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.providers.base import EmbeddingProvider
from app.services.ingestion_service import make_chunks, sha256_text

settings = get_settings()


class RAGService:
    def __init__(self, db: AsyncSession, embeddings: EmbeddingProvider):
        self.db = db
        self.embeddings = embeddings

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
