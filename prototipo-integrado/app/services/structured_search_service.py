from app.models.establishment import Establishment
from app.models.service import Service
from app.repositories.establishment_repository import EstablishmentRepository
from app.repositories.service_repository import ServiceRepository


class StructuredSearchService:
    def __init__(self, establishments: EstablishmentRepository, services: ServiceRepository):
        self.establishments = establishments
        self.services = services

    async def search_units(
        self,
        *,
        unit_type: str | None = None,
        ra: str | None = None,
        cep: str | None = None,
        name: str | None = None,
        limit: int = 5,
    ) -> list[Establishment]:
        return await self.establishments.list(
            unit_type=unit_type,
            ra=ra,
            cep=cep,
            name=name,
            limit=limit,
        )

    async def services_for_unit(self, unit_id, limit: int = 20) -> list[Service]:
        return await self.services.list(establishment_id=unit_id, limit=limit)

    @staticmethod
    def unit_evidence(unit: Establishment) -> dict:
        content = (
            f"Unidade: {unit.name}. Tipo: {unit.type}. "
            f"Região Administrativa: {unit.ra or 'não informada'}. "
            f"Endereço: {unit.address}. "
            f"CEP: {unit.cep or 'não informado'}. "
            f"Telefone: {unit.phone or 'não informado'}. "
            f"Horário: {unit.opening_hours or 'não informado'}."
        )
        return {
            "content": content,
            "source_id": unit.source_id,
            "source_name": None,
            "source_url": None,
            "document_title": unit.name,
            "source_updated_at": None,
            "structured": True,
        }
