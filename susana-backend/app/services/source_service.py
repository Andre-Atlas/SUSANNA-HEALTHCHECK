from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.source import Source
from app.schemas.source import SourceCreate, SourceUpdate


class SourceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(self) -> list[Source]:
        return list((await self.db.execute(select(Source).order_by(Source.name))).scalars().all())

    async def get(self, source_id):
        return await self.db.get(Source, source_id)

    async def create(self, payload: SourceCreate) -> Source:
        data = payload.model_dump()
        data["url"] = str(payload.url)
        source = Source(**data)
        self.db.add(source)
        await self.db.commit()
        await self.db.refresh(source)
        return source

    async def update(self, source: Source, payload: SourceUpdate) -> Source:
        data = payload.model_dump()
        data["url"] = str(payload.url)
        for field, value in data.items():
            setattr(source, field, value)
        await self.db.commit()
        await self.db.refresh(source)
        return source

    async def delete(self, source: Source) -> None:
        await self.db.delete(source)
        await self.db.commit()
