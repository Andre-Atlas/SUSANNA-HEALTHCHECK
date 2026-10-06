import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.establishment_repository import EstablishmentRepository
from app.repositories.service_repository import ServiceRepository
from app.repositories.source_repository import SourceRepository
from app.schemas.service import ServiceRead
from app.schemas.unit import UnitCreate, UnitRead, UnitUpdate
from app.services.service_service import ServiceService
from app.services.unit_service import UnitService

router = APIRouter(prefix="/unidades", tags=["Rede de Atendimento"])


def unit_service(db: AsyncSession) -> UnitService:
    return UnitService(EstablishmentRepository(db), SourceRepository(db))


def service_service(db: AsyncSession) -> ServiceService:
    return ServiceService(ServiceRepository(db), EstablishmentRepository(db))


@router.get("", response_model=list[UnitRead], summary="Lista unidades de saúde")
async def list_units(
    type: str | None = None,
    ra: str | None = None,
    cep: str | None = None,
    name: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await unit_service(db).list(
        unit_type=type, ra=ra, cep=cep, name=name, limit=limit, offset=offset
    )


@router.get("/{unit_id}", response_model=UnitRead, summary="Obtém uma unidade")
async def get_unit(unit_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    unit = await unit_service(db).get(unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unidade não encontrada.")
    return unit


@router.get("/{unit_id}/servicos", response_model=list[ServiceRead], summary="Lista serviços da unidade")
async def get_unit_services(unit_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    if not await unit_service(db).get(unit_id):
        raise HTTPException(status_code=404, detail="Unidade não encontrada.")
    return await service_service(db).list(establishment_id=unit_id, limit=100)


@router.post("", response_model=UnitRead, status_code=status.HTTP_201_CREATED, summary="Cria unidade")
async def create_unit(payload: UnitCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await unit_service(db).create(payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/{unit_id}", response_model=UnitRead, summary="Atualiza unidade")
async def update_unit(unit_id: uuid.UUID, payload: UnitUpdate, db: AsyncSession = Depends(get_db)):
    service = unit_service(db)
    unit = await service.get(unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unidade não encontrada.")
    try:
        return await service.update(unit, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{unit_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove unidade")
async def delete_unit(unit_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = unit_service(db)
    unit = await service.get(unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unidade não encontrada.")
    await service.delete(unit)
