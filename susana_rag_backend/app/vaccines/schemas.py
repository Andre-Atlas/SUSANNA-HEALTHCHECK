"""Schemas para o Guia Oficial de Vacinação por Idade (PNI / SES-DF)."""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel


class VaccineItem(BaseModel):
    id: str
    nome: str
    sigla: Optional[str] = None
    faixa_etaria: str  # recem_nascido, crianca, adolescente, adulto, idoso, gestante
    faixa_etaria_display: str
    idade_recomendada: str
    doses: str
    doencas_prevenidas: str
    orientacoes: str
    onde_tomar: str = "Salas de vacinação de todas as UBSs do DF"


class VaccineGuideResponse(BaseModel):
    total: int
    faixa_etaria_filtro: Optional[str] = None
    vacinas: List[VaccineItem]
    campanhas_ativas: List[dict]


class PersonalizedVaccineRecommendation(BaseModel):
    idade_anos: int
    faixa_etaria: str
    gestante: bool
    vacinas_recomendadas: List[VaccineItem]
    proxima_dose_alerta: Optional[str] = None
