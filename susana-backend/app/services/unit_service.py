import uuid

from app.models.establishment import Establishment
from app.repositories.establishment_repository import EstablishmentRepository
from app.repositories.source_repository import SourceRepository
from app.schemas.unit import UnitCreate, UnitUpdate


class UnitService:
    def __init__(self, repository: EstablishmentRepository, sources: SourceRepository):
        self.repository = repository
        self.sources = sources

    async def list(self, **filters) -> list[Establishment]:
        return await self.repository.list(**filters)

    async def get(self, unit_id: uuid.UUID) -> Establishment | None:
        return await self.repository.get(unit_id)

    async def create(self, payload: UnitCreate) -> Establishment:
        if payload.source_id and not await self.sources.get(payload.source_id):
            raise ValueError("Fonte associada não encontrada.")
        return await self.repository.create(Establishment(**payload.model_dump()))

    async def update(self, unit: Establishment, payload: UnitUpdate) -> Establishment:
        if payload.source_id and not await self.sources.get(payload.source_id):
            raise ValueError("Fonte associada não encontrada.")
        return await self.repository.update(unit, payload.model_dump())

    async def delete(self, unit: Establishment) -> None:
        await self.repository.delete(unit)
