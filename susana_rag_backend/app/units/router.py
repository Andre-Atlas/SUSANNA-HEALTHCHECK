"""Rotas FastAPI para o Catálogo e Mapa de Unidades de Saúde do DF."""
from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends

from app.units.schemas import HealthUnitItem, RADistributionItem, UnitsListResponse
from app.units.service import UnitsDirectoryService

router = APIRouter(prefix="/api/units", tags=["units"])

_units_service_instance: Optional[UnitsDirectoryService] = None


def get_units_service() -> UnitsDirectoryService:
    global _units_service_instance
    if _units_service_instance is None:
        _units_service_instance = UnitsDirectoryService()
    return _units_service_instance


@router.get("", response_model=UnitsListResponse)
def list_units(
    ra: Optional[str] = None,
    tipo: Optional[str] = None,
    type: Optional[str] = None,
    servico: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = 500,
    service: UnitsDirectoryService = Depends(get_units_service),
):
    """Consulta unidades de saúde públicas do DF filtradas por RA, tipo ou texto."""
    effective_tipo = tipo or type
    return service.search_units(ra=ra, tipo=effective_tipo, servico=servico, query=q, limit=limit)


@router.get("/ras", response_model=List[RADistributionItem])
def list_ras_distribution(
    service: UnitsDirectoryService = Depends(get_units_service),
):
    """Retorna o quantitativo de unidades de saúde em cada uma das 33 RAs do Distrito Federal."""
    return service.get_ra_distribution()


@router.get("/{unit_id}", response_model=HealthUnitItem)
def get_unit_details(
    unit_id: str,
    service: UnitsDirectoryService = Depends(get_units_service),
):
    unit = service.get_unit_by_id(unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unidade de saúde não encontrada.")
    return unit
