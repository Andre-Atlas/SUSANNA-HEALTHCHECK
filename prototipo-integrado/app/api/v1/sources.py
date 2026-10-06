import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.source_repository import SourceRepository
from app.schemas.source import SourceCreate, SourceRead, SourceUpdate
from app.services.source_service import SourceService

router = APIRouter(prefix="/fontes", tags=["Fontes"])


def source_service(db: AsyncSession) -> SourceService:
    return SourceService(SourceRepository(db))


@router.get("", response_model=list[SourceRead], summary="Lista fontes")
async def list_sources(db: AsyncSession = Depends(get_db)):
    return await source_service(db).list()


@router.get("/{source_id}", response_model=SourceRead, summary="Obtém fonte")
async def get_source(source_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    source = await source_service(db).get(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Fonte não encontrada.")
    return source


@router.post("", response_model=SourceRead, status_code=status.HTTP_201_CREATED, summary="Cria fonte")
async def create_source(payload: SourceCreate, db: AsyncSession = Depends(get_db)):
    return await source_service(db).create(payload)


@router.put("/{source_id}", response_model=SourceRead, summary="Atualiza fonte")
async def update_source(
    source_id: uuid.UUID, payload: SourceUpdate, db: AsyncSession = Depends(get_db)
):
    service = source_service(db)
    source = await service.get(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Fonte não encontrada.")
    return await service.update(source, payload)


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove fonte")
async def delete_source(source_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = source_service(db)
    source = await service.get(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Fonte não encontrada.")
    try:
        await service.delete(source)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
