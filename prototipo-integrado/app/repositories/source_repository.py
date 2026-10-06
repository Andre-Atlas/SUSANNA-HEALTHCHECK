import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.establishment import Establishment
from app.models.source import Source


class SourceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(self) -> list[Source]:
        result = await self.db.execute(select(Source).order_by(Source.name))
        return list(result.scalars().all())

    async def get(self, source_id: uuid.UUID) -> Source | None:
        return await self.db.get(Source, source_id)

    async def has_dependencies(self, source_id: uuid.UUID) -> bool:
        document_count = await self.db.scalar(
            select(func.count()).select_from(Document).where(Document.source_id == source_id)
        )
        establishment_count = await self.db.scalar(
            select(func.count()).select_from(Establishment).where(Establishment.source_id == source_id)
        )
        return bool(document_count or establishment_count)

    async def create(self, source: Source) -> Source:
        self.db.add(source)
        await self.db.commit()
        await self.db.refresh(source)
        return source

    async def update(self, source: Source, values: dict) -> Source:
        for field, value in values.items():
            setattr(source, field, value)
        await self.db.commit()
        await self.db.refresh(source)
        return source

    async def delete(self, source: Source) -> None:
        await self.db.delete(source)
        await self.db.commit()
