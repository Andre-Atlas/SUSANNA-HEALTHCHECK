"""
Serviço de Negócios e Agregação de Vigilância Epidemiológica (SUS-DF)
=====================================================================
Calcula KPIs, tendências, taxas e rankings a partir de dados oficiais.
"""
from __future__ import annotations

import logging
import time
import threading
from typing import Dict, List, Optional, Tuple

from app.surveillance.schemas import (
    ConditionDashboardResponse,
    DashboardKPIs,
    SurveillanceCategory,
    SurveillanceCondition,
    SurveillanceSummaryResponse,
)
from app.surveillance.storage import SurveillanceStorage

logger = logging.getLogger("susana.surveillance.service")


class SurveillanceService:
    def __init__(self, storage: Optional[SurveillanceStorage] = None, cache_ttl: int = 3600):
        self.storage = storage or SurveillanceStorage()
        self.cache_ttl = cache_ttl
        self._lock = threading.RLock()
        self._summary_cache: Optional[Tuple[float, SurveillanceSummaryResponse]] = None
        self._categories_cache: Optional[Tuple[float, List[SurveillanceCategory]]] = None
        self._conditions_cache: Dict[str, Tuple[float, List[SurveillanceCondition]]] = {}
        self._dashboard_cache: Dict[str, Tuple[float, Optional[ConditionDashboardResponse]]] = {}

    def get_summary(self) -> SurveillanceSummaryResponse:
        now = time.time()
        with self._lock:
            if self._summary_cache and (now - self._summary_cache[0]) < self.cache_ttl:
                return self._summary_cache[1]

        categories = self.storage.list_categories()
        all_conditions = self.storage.list_conditions()

        criticos = [
            c.nome
            for c in all_conditions
            if c.nivel_alerta in ("alerta", "critico")
        ]

        resp = SurveillanceSummaryResponse(
            total_categorias=len(categories),
            total_agravos_monitorados=len(all_conditions),
            categorias=categories,
            agravos_criticos=criticos,
            fonte_oficial="SES-DF / SVS / SINAN / InfoGripe (Boletins Oficiais 2024-2026)",
            atualizado_em="Outubro de 2026",
        )

        with self._lock:
            self._summary_cache = (now, resp)
        return resp

    def get_categories(self) -> List[SurveillanceCategory]:
        now = time.time()
        with self._lock:
            if self._categories_cache and (now - self._categories_cache[0]) < self.cache_ttl:
                return self._categories_cache[1]

        cats = self.storage.list_categories()
        with self._lock:
            self._categories_cache = (now, cats)
        return cats

    def get_conditions(self, category_id: Optional[str] = None) -> List[SurveillanceCondition]:
        now = time.time()
        cache_key = category_id or "__all__"
        with self._lock:
            if cache_key in self._conditions_cache and (now - self._conditions_cache[cache_key][0]) < self.cache_ttl:
                return self._conditions_cache[cache_key][1]

        conds = self.storage.list_conditions(category_id=category_id)
        with self._lock:
            self._conditions_cache[cache_key] = (now, conds)
        return conds

    def get_condition_dashboard(self, condition_id: str) -> Optional[ConditionDashboardResponse]:
        now = time.time()
        with self._lock:
            if condition_id in self._dashboard_cache and (now - self._dashboard_cache[condition_id][0]) < self.cache_ttl:
                return self._dashboard_cache[condition_id][1]

        data = self.storage.get_condition(condition_id)
        if not data:
            return None

        # Monta Condition
        condition = SurveillanceCondition(
            id=data["id"],
            category_id=data["category_id"],
            nome=data["nome"],
            codigo_cid10=data["codigo_cid10"],
            tipo_agravo=data["tipo_agravo"],
            descricao=data["descricao"],
            nivel_alerta=data["nivel_alerta"],
            sazonalidade=data["sazonalidade"],
            vetor_ou_transmissao=data["vetor_ou_transmissao"],
            taxa_incidencia_100k=data["taxa_incidencia_100k"],
            total_casos_ano=data["total_casos_ano"],
            variacao_semanal_pct=data["variacao_semanal_pct"],
            faixa_etaria_predominante=data["faixa_etaria_predominante"],
        )

        time_series = data.get("time_series", [])
        regions = data.get("regions", [])
        guidelines = data.get("guidelines", [])
        unidades = data.get("unidades_referencia", [])

        # Cálculo de KPIs dinâmicos
        casos_ult = time_series[-1].casos if time_series else 0
        var_pct = data["variacao_semanal_pct"]
        if len(time_series) >= 2:
            c_ant = time_series[-2].casos
            c_atu = time_series[-1].casos
            if c_ant > 0:
                var_calc = round(((c_atu - c_ant) / c_ant) * 100, 1)
                var_pct = var_calc

        if var_pct > 3.0:
            tendencia = "alta"
        elif var_pct < -3.0:
            tendencia = "queda"
        else:
            tendencia = "estavel"

        hotspot_id = regions[0].ra_id if regions else "df_geral"
        hotspot_nome = regions[0].ra_nome if regions else "Distrito Federal"
        hotspot_casos = regions[0].casos if regions else 0

        kpis = DashboardKPIs(
            total_casos_ano=data["total_casos_ano"],
            casos_ultima_semana=casos_ult,
            variacao_semanal_pct=var_pct,
            tendencia=tendencia,
            taxa_incidencia_distrital_100k=data["taxa_incidencia_100k"],
            obitos_confirmados=data.get("obitos_confirmados", 0),
            ra_hotspot_id=hotspot_id,
            ra_hotspot_nome=hotspot_nome,
            ra_hotspot_casos=hotspot_casos,
            nivel_alerta_geral=data["nivel_alerta"],
        )

        resp = ConditionDashboardResponse(
            condition=condition,
            kpis=kpis,
            time_series=time_series,
            regions=regions,
            guidelines=guidelines,
            unidades_referencia=unidades,
            fonte_oficial="SES-DF · Subsecretaria de Vigilância à Saúde (SVS/SINAN)",
            ano_vigente=2026,
            data_atualizacao="Semana Epidemiológica 45/2026",
        )

        with self._lock:
            self._dashboard_cache[condition_id] = (now, resp)
        return resp
