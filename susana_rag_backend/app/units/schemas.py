"""Schemas Pydantic para o Catálogo e Mapa de Unidades de Saúde do DF."""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel


class HealthUnitItem(BaseModel):
    id: str
    nome: str
    ra: str
    ra_display: str
    tipo: str  # ubs, upa, hospital, caps, policlinica, regional, farmacia
    tipo_display: str
    cluster: str
    endereco: str
    horario: str
    servicos: List[str]
    referencia_emergencia: Optional[str] = None
    url: Optional[str] = None
    svg_x: float  # Coordenada percentual no mapa SVG (0 a 100)
    svg_y: float  # Coordenada percentual no mapa SVG (0 a 100)


class UnitsListResponse(BaseModel):
    total: int
    ra_filter: Optional[str] = None
    tipo_filter: Optional[str] = None
    units: List[HealthUnitItem]


class RADistributionItem(BaseModel):
    ra: str
    ra_display: str
    unit_count: int
