"""
Router FastAPI para Vigilância Epidemiológica do DF
===================================================
Endpoints de monitoramento de arboviroses, endemias, ISTs e agravos sazonais.
"""
from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from app.surveillance.schemas import (
    ConditionDashboardResponse,
    SurveillanceCategory,
    SurveillanceCondition,
    SurveillanceSummaryResponse,
)
from app.surveillance.service import SurveillanceService

router = APIRouter(prefix="/api/surveillance", tags=["Vigilância Epidemiológica"])
_service = SurveillanceService()


@router.get("/summary", response_model=SurveillanceSummaryResponse)
def get_surveillance_summary():
    """Retorna o panorama geral da vigilância em saúde no DF."""
    return _service.get_summary()


@router.get("/categories", response_model=List[SurveillanceCategory])
def list_categories():
    """Retorna a lista de categorias epidemiológicas monitoradas."""
    return _service.get_categories()


@router.get("/conditions", response_model=List[SurveillanceCondition])
def list_conditions(
    category_id: Optional[str] = Query(None, description="Filtrar por ID da categoria")
):
    """Retorna os agravos epidemiológicos monitorados."""
    return _service.get_conditions(category_id=category_id)


@router.get("/dashboard/{condition_id}", response_model=ConditionDashboardResponse)
def get_condition_dashboard(condition_id: str):
    """
    Retorna o pacote consolidado de dashboard para o agravo selecionado:
    KPIs, série temporal (SE 36 a 45), ranking por RA, diretrizes de conduta e unidades.
    """
    resp = _service.get_condition_dashboard(condition_id)
    if not resp:
        raise HTTPException(
            status_code=404,
            detail=f"Condição epidemiológica '{condition_id}' não encontrada.",
        )
    return resp
