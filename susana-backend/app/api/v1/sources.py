import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.source import Source
from app.schemas.source import SourceCreate, SourceRead, SourceUpdate
from app.services.source_service import SourceService

router = APIRouter(prefix="/fontes", tags=["Fontes"])


@router.get("", response_model=list[SourceRead])
async def list_sources(db: AsyncSession = Depends(get_db)):
    return await SourceService(db).list()


@router.get("/{source_id}", response_model=SourceRead)
async def get_source(source_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    source = await SourceService(db).get(source_id)
    if not source: raise HTTPException(404, "Fonte não encontrada.")
    return source


@router.post("", response_model=SourceRead, status_code=status.HTTP_201_CREATED)
async def create_source(payload: SourceCreate, db: AsyncSession = Depends(get_db)):
    return await SourceService(db).create(payload)


@router.put("/{source_id}", response_model=SourceRead)
async def update_source(source_id: uuid.UUID, payload: SourceUpdate, db: AsyncSession = Depends(get_db)):
    service = SourceService(db); source = await service.get(source_id)
    if not source: raise HTTPException(404, "Fonte não encontrada.")
    return await service.update(source, payload)


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(source_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = SourceService(db); source = await service.get(source_id)
    if not source: raise HTTPException(404, "Fonte não encontrada.")
    await service.delete(source)
