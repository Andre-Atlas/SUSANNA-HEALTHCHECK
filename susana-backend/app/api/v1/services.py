import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceRead, ServiceUpdate

router = APIRouter(prefix="/servicos", tags=["Serviços"])


@router.get("", response_model=list[ServiceRead])
async def list_services(
    category: str | None = None,
    name: str | None = None,
    establishment_id: uuid.UUID | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Service)
    if category: stmt = stmt.where(Service.category.ilike(f"%{category}%"))
    if name: stmt = stmt.where(Service.name.ilike(f"%{name}%"))
    if establishment_id: stmt = stmt.where(Service.establishment_id == establishment_id)
    stmt = stmt.order_by(Service.name).offset(offset).limit(limit)
    return list((await db.execute(stmt)).scalars().all())


@router.get("/{service_id}", response_model=ServiceRead)
async def get_service(service_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = await db.get(Service, service_id)
    if not service: raise HTTPException(404, "Serviço não encontrado.")
    return service


@router.post("", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
async def create_service(payload: ServiceCreate, db: AsyncSession = Depends(get_db)):
    service = Service(**payload.model_dump()); db.add(service); await db.commit(); await db.refresh(service)
    return service


@router.put("/{service_id}", response_model=ServiceRead)
async def update_service(service_id: uuid.UUID, payload: ServiceUpdate, db: AsyncSession = Depends(get_db)):
    service = await db.get(Service, service_id)
    if not service: raise HTTPException(404, "Serviço não encontrado.")
    for field, value in payload.model_dump().items(): setattr(service, field, value)
    await db.commit(); await db.refresh(service)
    return service


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(service_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = await db.get(Service, service_id)
    if not service: raise HTTPException(404, "Serviço não encontrado.")
    await db.delete(service); await db.commit()
