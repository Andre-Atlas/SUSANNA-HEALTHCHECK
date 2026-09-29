import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.establishment import Establishment


class EstablishmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(
        self,
        *,
        unit_type: str | None = None,
        ra: str | None = None,
        cep: str | None = None,
        name: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Establishment]:
        stmt = select(Establishment)
        if unit_type:
            stmt = stmt.where(Establishment.type.ilike(f"%{unit_type}%"))
        if ra:
            stmt = stmt.where(Establishment.ra.ilike(f"%{ra}%"))
        if cep:
            stmt = stmt.where(Establishment.cep == cep)
        if name:
            stmt = stmt.where(Establishment.name.ilike(f"%{name}%"))
        stmt = stmt.order_by(Establishment.name).offset(offset).limit(limit)
        return list((await self.db.execute(stmt)).scalars().all())

    async def get(self, unit_id: uuid.UUID) -> Establishment | None:
        return await self.db.get(Establishment, unit_id)

    async def create(self, unit: Establishment) -> Establishment:
        self.db.add(unit)
        await self.db.commit()
        await self.db.refresh(unit)
        return unit

    async def update(self, unit: Establishment, values: dict) -> Establishment:
        for field, value in values.items():
            setattr(unit, field, value)
        await self.db.commit()
        await self.db.refresh(unit)
        return unit

    async def delete(self, unit: Establishment) -> None:
        await self.db.delete(unit)
        await self.db.commit()
