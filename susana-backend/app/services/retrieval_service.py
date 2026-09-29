from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.models.source import Source
from app.providers.base import EmbeddingProvider

settings = get_settings()


class RetrievalService:
    def __init__(self, db: AsyncSession, embeddings: EmbeddingProvider):
        self.db = db
        self.embeddings = embeddings

    async def search(self, query: str, top_k: int | None = None) -> list[dict]:
        vector = await self.embeddings.embed(query)
        limit = top_k or settings.rag_top_k
        distance = DocumentChunk.embedding.cosine_distance(vector)

        stmt = (
            select(DocumentChunk, Document, Source, distance.label("distance"))
            .join(Document, Document.id == DocumentChunk.document_id)
            .join(Source, Source.id == Document.source_id)
            .where(
                DocumentChunk.embedding.is_not(None),
                Document.status == "indexed",
            )
            .order_by(distance)
            .limit(limit)
        )

        rows = (await self.db.execute(stmt)).all()
        results: list[dict] = []
        for chunk, document, source, distance_value in rows:
            score = 1.0 - float(distance_value)
            if score < settings.rag_similarity_threshold:
                continue
            results.append(
                {
                    "document_id": document.id,
                    "chunk_id": chunk.id,
                    "score": score,
                    "content": chunk.content,
                    "document_title": document.title,
                    "source_name": source.name,
                    "source_url": source.url,
                    "source_id": source.id,
                    "source_updated_at": document.source_updated_at,
                    "structured": False,
                }
            )
        return results
