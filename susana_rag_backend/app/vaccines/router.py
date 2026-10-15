"""Router da API para o Guia Oficial de Vacinação e Campanhas do DF (PNI / SES-DF)."""
from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Query

from app.vaccines.schemas import (
    PersonalizedVaccineRecommendation,
    VaccineGuideResponse,
)
from app.vaccines.service import VaccineGuideService

router = APIRouter(prefix="/api/vaccines", tags=["Vaccines"])
_service = VaccineGuideService()


@router.get("/guide", response_model=VaccineGuideResponse)
async def get_vaccine_guide(
    faixa_etaria: Optional[str] = Query(
        None,
        description="Filtro de faixa etária: recem_nascido, crianca, adolescente, adulto, idoso, gestante",
    ),
):
    """Retorna o Guia Oficial de Vacinação por Idade do PNI/SES-DF e campanhas ativas."""
    return _service.get_vaccines(faixa_etaria=faixa_etaria)


@router.get("/recommendations", response_model=PersonalizedVaccineRecommendation)
async def get_personalized_recommendation(
    data_nascimento: str = Query(..., description="Data de nascimento do cidadão no formato AAAA-MM-DD"),
    gestante: bool = Query(False, description="Indica se a cidadã é gestante"),
    condicoes: Optional[str] = Query(None, description="Condições de saúde separadas por vírgula"),
):
    """Retorna as vacinas recomendadas de forma personalizada baseada na idade e perfil do cidadão."""
    return _service.get_personalized_recommendation(
        birth_date_str=data_nascimento,
        is_pregnant=gestante,
        condicoes=[c.strip() for c in condicoes.split(",") if c.strip()] if condicoes else None,
    )
