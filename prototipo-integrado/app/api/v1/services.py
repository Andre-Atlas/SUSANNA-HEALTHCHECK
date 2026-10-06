import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.establishment_repository import EstablishmentRepository
from app.repositories.service_repository import ServiceRepository
from app.schemas.service import ServiceCreate, ServiceRead, ServiceUpdate
from app.services.service_service import ServiceService

router = APIRouter(prefix="/servicos", tags=["Serviços"])


def get_service_service(db: AsyncSession) -> ServiceService:
    return ServiceService(ServiceRepository(db), EstablishmentRepository(db))


@router.get("", response_model=list[ServiceRead], summary="Lista serviços")
async def list_services(
    category: str | None = None,
    name: str | None = None,
    establishment_id: uuid.UUID | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await get_service_service(db).list(
        category=category,
        name=name,
        establishment_id=establishment_id,
        limit=limit,
        offset=offset,
    )


@router.get("/{service_id}", response_model=ServiceRead, summary="Obtém serviço")
async def get_service(service_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = await get_service_service(db).get(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Serviço não encontrado.")
    return service


@router.post("", response_model=ServiceRead, status_code=status.HTTP_201_CREATED, summary="Cria serviço")
async def create_service(payload: ServiceCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await get_service_service(db).create(payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/{service_id}", response_model=ServiceRead, summary="Atualiza serviço")
async def update_service(
    service_id: uuid.UUID, payload: ServiceUpdate, db: AsyncSession = Depends(get_db)
):
    service = get_service_service(db)
    entity = await service.get(service_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Serviço não encontrado.")
    try:
        return await service.update(entity, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove serviço")
async def delete_service(service_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = get_service_service(db)
    entity = await service.get(service_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Serviço não encontrado.")
    await service.delete(entity)
