import uuid

from app.models.service import Service
from app.repositories.establishment_repository import EstablishmentRepository
from app.repositories.service_repository import ServiceRepository
from app.schemas.service import ServiceCreate, ServiceUpdate


class ServiceService:
    def __init__(self, repository: ServiceRepository, establishments: EstablishmentRepository):
        self.repository = repository
        self.establishments = establishments

    async def list(self, **filters) -> list[Service]:
        return await self.repository.list(**filters)

    async def get(self, service_id: uuid.UUID) -> Service | None:
        return await self.repository.get(service_id)

    async def create(self, payload: ServiceCreate) -> Service:
        if payload.establishment_id and not await self.establishments.get(payload.establishment_id):
            raise ValueError("Unidade associada não encontrada.")
        return await self.repository.create(Service(**payload.model_dump()))

    async def update(self, service: Service, payload: ServiceUpdate) -> Service:
        if payload.establishment_id and not await self.establishments.get(payload.establishment_id):
            raise ValueError("Unidade associada não encontrada.")
        return await self.repository.update(service, payload.model_dump())

    async def delete(self, service: Service) -> None:
        await self.repository.delete(service)
