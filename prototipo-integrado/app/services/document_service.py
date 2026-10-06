import uuid

from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.repositories.source_repository import SourceRepository
from app.schemas.rag import DocumentCreate, DocumentUpdate


class DocumentService:
    def __init__(self, repository: DocumentRepository, sources: SourceRepository):
        self.repository = repository
        self.sources = sources

    async def list(self) -> list[Document]:
        return await self.repository.list()

    async def get(self, document_id: uuid.UUID) -> Document | None:
        return await self.repository.get(document_id)

    async def create(self, payload: DocumentCreate) -> Document:
        if not await self.sources.get(payload.source_id):
            raise ValueError("Fonte associada não encontrada.")
        data = payload.model_dump()
        data["url"] = str(payload.url)
        return await self.repository.create(Document(**data))

    async def update(self, document: Document, payload: DocumentUpdate) -> Document:
        data = payload.model_dump()
        data["url"] = str(payload.url)
        document.content_hash = None
        document.status = "pending"
        return await self.repository.update(document, data)

    async def delete(self, document: Document) -> None:
        await self.repository.delete(document)
