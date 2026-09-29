import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.establishment import Establishment
from app.models.service import Service
from app.schemas.service import ServiceRead
from app.schemas.unit import UnitCreate, UnitRead, UnitUpdate

router = APIRouter(prefix="/unidades", tags=["Rede de Atendimento"])


@router.get("", response_model=list[UnitRead])
async def list_units(
    type: str | None = None,
    ra: str | None = None,
    cep: str | None = None,
    name: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Establishment)
    if type: stmt = stmt.where(Establishment.type.ilike(f"%{type}%"))
    if ra: stmt = stmt.where(Establishment.ra.ilike(f"%{ra}%"))
    if cep: stmt = stmt.where(Establishment.cep == cep)
    if name: stmt = stmt.where(Establishment.name.ilike(f"%{name}%"))
    stmt = stmt.order_by(Establishment.name).offset(offset).limit(limit)
    return list((await db.execute(stmt)).scalars().all())


@router.get("/{unit_id}", response_model=UnitRead)
async def get_unit(unit_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    unit = await db.get(Establishment, unit_id)
    if not unit: raise HTTPException(404, "Unidade não encontrada.")
    return unit


@router.get("/{unit_id}/servicos", response_model=list[ServiceRead])
async def get_unit_services(unit_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    if not await db.get(Establishment, unit_id): raise HTTPException(404, "Unidade não encontrada.")
    stmt = select(Service).where(Service.establishment_id == unit_id).order_by(Service.name)
    return list((await db.execute(stmt)).scalars().all())


@router.post("", response_model=UnitRead, status_code=status.HTTP_201_CREATED)
async def create_unit(payload: UnitCreate, db: AsyncSession = Depends(get_db)):
    unit = Establishment(**payload.model_dump())
    db.add(unit); await db.commit(); await db.refresh(unit)
    return unit


@router.put("/{unit_id}", response_model=UnitRead)
async def update_unit(unit_id: uuid.UUID, payload: UnitUpdate, db: AsyncSession = Depends(get_db)):
    unit = await db.get(Establishment, unit_id)
    if not unit: raise HTTPException(404, "Unidade não encontrada.")
    for field, value in payload.model_dump().items(): setattr(unit, field, value)
    await db.commit(); await db.refresh(unit)
    return unit


@router.delete("/{unit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_unit(unit_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    unit = await db.get(Establishment, unit_id)
    if not unit: raise HTTPException(404, "Unidade não encontrada.")
    await db.delete(unit); await db.commit()
