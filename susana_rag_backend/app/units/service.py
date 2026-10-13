"""
Serviço do Catálogo de Unidades de Saúde do Distrito Federal
============================================================
Indexação em memória de 346 blocos reais de saúde cobrindo as 33 Regiões Administrativas.
Responde a consultas filtradas em < 2ms com coordenadas de mapeamento SVG.
"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.rag.nlu import RA_DICTIONARY
from app.units.schemas import HealthUnitItem, RADistributionItem, UnitsListResponse

logger = logging.getLogger("susana.units.service")

# Coordenadas geográficas percentuais aproximadas (0 a 100) na malha do Distrito Federal
RA_SVG_COORDINATES: Dict[str, Tuple[float, float]] = {
    "plano_piloto": (52.0, 48.0),
    "ceilandia": (28.0, 52.0),
    "taguatinga": (35.0, 55.0),
    "samambaia": (30.0, 63.0),
    "gama": (42.0, 78.0),
    "santa_maria": (50.0, 82.0),
    "sobradinho": (58.0, 28.0),
    "sobradinho_ii": (57.0, 24.0),
    "planaltina": (72.0, 22.0),
    "guara": (46.0, 56.0),
    "aguas_claras": (39.0, 58.0),
    "recanto_das_emas": (25.0, 68.0),
    "riacho_fundo": (38.0, 65.0),
    "riacho_fundo_ii": (34.0, 68.0),
    "vicente_pires": (40.0, 50.0),
    "sao_sebastiao": (68.0, 60.0),
    "paranoa": (66.0, 42.0),
    "itapoa": (67.0, 40.0),
    "brazlandia": (22.0, 28.0),
    "sol_nascente": (25.0, 54.0),
    "sol_nascente_por_do_sol": (25.0, 54.0),
    "sudoeste_octogonal": (48.0, 50.0),
    "lago_sul": (58.0, 56.0),
    "lago_norte": (58.0, 40.0),
    "jardim_botanico": (62.0, 64.0),
    "cruzeiro": (49.0, 48.0),
    "candangolandia": (48.0, 60.0),
    "nucleo_bandeirante": (45.0, 62.0),
    "park_way": (46.0, 68.0),
    "scia_estrutural": (42.0, 46.0),
    "sia": (45.0, 51.0),
    "varjao": (56.0, 42.0),
    "fercal": (55.0, 18.0),
    "arniqueira": (38.0, 62.0),
}


class UnitsDirectoryService:
    """Carrega e indexa em memória o diretório real de saúde pública do DF."""

    def __init__(self, json_path: Optional[Path] = None):
        if json_path is None:
            backend_dir = Path(__file__).resolve().parent.parent.parent
            self.json_path = backend_dir / "data" / "corpus" / "diretorio_saude_df.json"
        else:
            self.json_path = json_path
        self._units: List[HealthUnitItem] = []
        self._by_id: Dict[str, HealthUnitItem] = {}
        self._load_and_index()

    def _format_ra_title(self, ra_id: str) -> str:
        for rid, aliases in RA_DICTIONARY:
            if rid == ra_id:
                return aliases[0].title()
        return ra_id.replace("_", " ").title()

    def _load_and_index(self) -> None:
        if not self.json_path.exists():
            logger.warning("Arquivo diretorio_saude_df.json não encontrado em %s", self.json_path)
            return

        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            blocks = data.get("blocks", [])

            tipo_display_map = {
                "ubs": "Unidade Básica de Saúde (UBS)",
                "upa": "Unidade de Pronto Atendimento (UPA 24h)",
                "hospital": "Hospital Regional (24h)",
                "regional": "Coordenação Regional de Atenção Primária",
                "caps": "Centro de Atenção Psicossocial (CAPS)",
                "policlinica": "Policlínica de Especialidades",
                "farmacia": "Farmácia de Alto Custo (CEAF)",
            }

            for i, b in enumerate(blocks):
                meta = b.get("metadata", {})
                ra_id = meta.get("ra", "geral_df")
                tipo = meta.get("tipo_unidade", "ubs").lower()
                cluster = meta.get("cluster", "geral")
                servicos_str = meta.get("servicos", "")
                servicos = [s.strip().replace("_", " ") for s in servicos_str.split(",") if s.strip()]

                # Extração de endereço e horário do texto oficial
                text = b.get("text", "")
                endereco = "Distrito Federal"
                m_end = re.search(r"endere[cç]o:?\s*([^.]+?\.\s*|[^.]+?,)", text, re.IGNORECASE)
                if m_end:
                    endereco = m_end.group(1).strip().rstrip(",.")
                else:
                    m_loc = re.search(r"localizad[ao]\s*(?:no|na|em)\s*([^.]+?\.)", text, re.IGNORECASE)
                    if m_loc:
                        endereco = m_loc.group(1).strip().rstrip(".")

                horario = "Segunda a sexta-feira, das 07:00 às 19:00"
                if "24 horas" in text or tipo in ("upa", "hospital"):
                    horario = "Atendimento ininterrupto 24 horas todos os dias"
                else:
                    m_hora = re.search(r"Hor[aá]rio(?:\s+de\s+Atendimento)?:\s*([^.]+?\.)", text, re.IGNORECASE)
                    if m_hora:
                        horario = m_hora.group(1).strip().rstrip(".")

                # Referência de emergência
                ref_emerg = None
                m_ref = re.search(r"refer[eê]ncia[^:]*?:\s*([^.]+?\.)", text, re.IGNORECASE)
                if m_ref:
                    ref_emerg = m_ref.group(1).strip().rstrip(".")

                # Coordenadas SVG baseadas na RA com pequena dispersão para não sobrepor
                base_x, base_y = RA_SVG_COORDINATES.get(ra_id, (50.0, 50.0))
                disp_x = ((i % 5) - 2) * 1.5
                disp_y = (((i // 5) % 5) - 2) * 1.5
                svg_x = max(5.0, min(95.0, base_x + disp_x))
                svg_y = max(5.0, min(95.0, base_y + disp_y))

                unit = HealthUnitItem(
                    id=f"unit_{i}_{ra_id}_{tipo}",
                    nome=b.get("header", "").replace("[", "").replace("]", "").strip()[:80],
                    ra=ra_id,
                    ra_display=self._format_ra_title(ra_id),
                    tipo=tipo,
                    tipo_display=tipo_display_map.get(tipo, tipo.upper()),
                    cluster=cluster,
                    endereco=endereco[:150],
                    horario=horario[:120],
                    servicos=servicos,
                    referencia_emergencia=ref_emerg[:150] if ref_emerg else None,
                    url=b.get("url"),
                    svg_x=round(svg_x, 1),
                    svg_y=round(svg_y, 1),
                )
                self._units.append(unit)
                self._by_id[unit.id] = unit

            logger.info("UnitsDirectoryService indexou com sucesso %d unidades do DF", len(self._units))
        except Exception as e:
            logger.error("Falha ao indexar diretorio_saude_df.json: %s", e)

    def search_units(
        self,
        ra: Optional[str] = None,
        tipo: Optional[str] = None,
        servico: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 100,
    ) -> UnitsListResponse:
        results = self._units

        if ra and ra.lower() not in ("todas", "geral_df", ""):
            ra_norm = ra.lower().strip().replace(" ", "_")
            results = [u for u in results if u.ra == ra_norm or ra_norm in u.ra]

        if tipo and tipo.lower() not in ("todos", "todas", ""):
            t_norm = tipo.lower().strip()
            if t_norm in ("hospital", "hospitais", "regional"):
                results = [
                    u for u in results
                    if u.tipo in ("regional", "hospital")
                    or "hospital" in u.nome.lower()
                    or (u.referencia_emergencia and "hospital" in u.referencia_emergencia.lower())
                ]
            else:
                results = [u for u in results if u.tipo == t_norm]

        if servico and servico.strip():
            s_norm = servico.lower().strip()
            results = [u for u in results if any(s_norm in s.lower() for s in u.servicos)]

        if query and query.strip():
            q_norm = query.lower().strip()
            results = [
                u for u in results
                if q_norm in u.nome.lower() or q_norm in u.endereco.lower() or q_norm in u.ra_display.lower()
            ]

        return UnitsListResponse(
            total=len(results),
            ra_filter=ra,
            tipo_filter=tipo,
            units=results[:limit],
        )

    def get_ra_distribution(self) -> List[RADistributionItem]:
        counts: Dict[str, int] = {}
        for u in self._units:
            counts[u.ra] = counts.get(u.ra, 0) + 1

        items = []
        for rid, aliases in RA_DICTIONARY:
            c = counts.get(rid, 0)
            items.append(
                RADistributionItem(
                    ra=rid,
                    ra_display=aliases[0].title(),
                    unit_count=c,
                )
            )
        items.sort(key=lambda x: -x.unit_count)
        return items

    def get_unit_by_id(self, unit_id: str) -> Optional[HealthUnitItem]:
        return self._by_id.get(unit_id)
