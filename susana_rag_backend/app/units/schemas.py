"""Schemas Pydantic para o Catálogo e Mapa de Unidades de Saúde do DF."""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel


class HealthUnitItem(BaseModel):
    id: str
    nome: str
    ra: str
    ra_display: str
    tipo: str  # ubs, upa, hospital, caps, policlinica, regional, farmacia, laboratorio
    tipo_display: str
    cluster: str
    endereco: str
    horario: str
    servicos: List[str]
    referencia_emergencia: Optional[str] = None
    url: Optional[str] = None
    telefone: Optional[str] = None
    atendimento_24h: bool = False
    bairro: Optional[str] = None
    lat: float = -15.7942  # Latitude geográfica real WGS84
    lng: float = -47.8822  # Longitude geográfica real WGS84
    svg_x: float  # Coordenada percentual legada
    svg_y: float  # Coordenada percentual legada


class UnitsListResponse(BaseModel):
    total: int
    ra_filter: Optional[str] = None
    tipo_filter: Optional[str] = None
    units: List[HealthUnitItem]


class RADistributionItem(BaseModel):
    ra: str
    ra_display: str
    unit_count: int
    lat: Optional[float] = None
    lng: Optional[float] = None
