import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.service import Service


class ServiceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(
        self,
        *,
        category: str | None = None,
        name: str | None = None,
        establishment_id: uuid.UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Service]:
        stmt = select(Service)
        if category:
            stmt = stmt.where(Service.category.ilike(f"%{category}%"))
        if name:
            stmt = stmt.where(Service.name.ilike(f"%{name}%"))
        if establishment_id:
            stmt = stmt.where(Service.establishment_id == establishment_id)
        stmt = stmt.order_by(Service.name).offset(offset).limit(limit)
        return list((await self.db.execute(stmt)).scalars().all())

    async def get(self, service_id: uuid.UUID) -> Service | None:
        return await self.db.get(Service, service_id)

    async def create(self, service: Service) -> Service:
        self.db.add(service)
        await self.db.commit()
        await self.db.refresh(service)
        return service

    async def update(self, service: Service, values: dict) -> Service:
        for field, value in values.items():
            setattr(service, field, value)
        await self.db.commit()
        await self.db.refresh(service)
        return service

    async def delete(self, service: Service) -> None:
        await self.db.delete(service)
        await self.db.commit()
