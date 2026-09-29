import uuid

from app.models.source import Source
from app.repositories.source_repository import SourceRepository
from app.schemas.source import SourceCreate, SourceUpdate


class SourceService:
    def __init__(self, repository: SourceRepository):
        self.repository = repository

    async def list(self) -> list[Source]:
        return await self.repository.list()

    async def get(self, source_id: uuid.UUID) -> Source | None:
        return await self.repository.get(source_id)

    async def create(self, payload: SourceCreate) -> Source:
        data = payload.model_dump()
        data["url"] = str(payload.url)
        return await self.repository.create(Source(**data))

    async def update(self, source: Source, payload: SourceUpdate) -> Source:
        data = payload.model_dump()
        data["url"] = str(payload.url)
        return await self.repository.update(source, data)

    async def delete(self, source: Source) -> None:
        if await self.repository.has_dependencies(source.id):
            raise ValueError("Fonte possui documentos ou unidades associados.")
        await self.repository.delete(source)
