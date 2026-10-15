"""
Modelos Pydantic para Vigilância Epidemiológica (SUS-DF)
========================================================
Tipos estruturados para categorias, condições, séries temporais e KPIs.
"""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class SurveillanceCategory(BaseModel):
    id: str
    nome: str
    slug: str
    icone: str
    descricao: str
    cor_badge: str
    total_agravos: int = 0


class SurveillanceCondition(BaseModel):
    id: str
    category_id: str
    nome: str
    codigo_cid10: str
    tipo_agravo: str
    descricao: str
    nivel_alerta: str = Field(..., description="baixo, atencao, alerta, critico")
    sazonalidade: str
    vetor_ou_transmissao: str
    taxa_incidencia_100k: float
    total_casos_ano: int
    variacao_semanal_pct: float
    faixa_etaria_predominante: str


class TimeSeriesPoint(BaseModel):
    semana_epidemio: str
    numero_semana: int
    rotulo: str
    casos: int
    taxa_movel: float
    status: str


class RegionCaseDistribution(BaseModel):
    ra_id: str
    ra_nome: str
    casos: int
    taxa_incidencia_100k: float
    percentual_distrital: float
    nivel_risco: str


class GuidelineItem(BaseModel):
    tipo: str = Field(..., description="sinal_alarme, prevencao, conduta")
    titulo: str
    descricao: str
    severidade: Optional[str] = "moderada"


class UnidadeReferenciaItem(BaseModel):
    tipo_servico: str
    nome_exemplo: str
    papel_clinico: str
    endereco_resumo: str


class DashboardKPIs(BaseModel):
    total_casos_ano: int
    casos_ultima_semana: int
    variacao_semanal_pct: float
    tendencia: str = Field(..., description="alta, queda, estavel")
    taxa_incidencia_distrital_100k: float
    obitos_confirmados: int
    ra_hotspot_id: str
    ra_hotspot_nome: str
    ra_hotspot_casos: int
    nivel_alerta_geral: str


class ConditionDashboardResponse(BaseModel):
    condition: SurveillanceCondition
    kpis: DashboardKPIs
    time_series: List[TimeSeriesPoint]
    regions: List[RegionCaseDistribution]
    guidelines: List[GuidelineItem]
    unidades_referencia: List[UnidadeReferenciaItem]
    fonte_oficial: str
    ano_vigente: int
    data_atualizacao: str


class SurveillanceSummaryResponse(BaseModel):
    total_categorias: int
    total_agravos_monitorados: int
    categorias: List[SurveillanceCategory]
    agravos_criticos: List[str]
    fonte_oficial: str
    atualizado_em: str
