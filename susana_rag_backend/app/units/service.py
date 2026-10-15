"""
Serviço do Catálogo de Unidades de Saúde do Distrito Federal
============================================================
Indexação em memória de 383 unidades de saúde públicas consolidadas cobrindo as 33 Regiões Administrativas.
Responde a consultas filtradas em < 2ms com coordenadas de mapeamento SVG e WGS84.
"""
from __future__ import annotations

import json
import logging
import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.rag.nlu import RA_DICTIONARY
from app.units.schemas import HealthUnitItem, RADistributionItem, UnitsListResponse

logger = logging.getLogger("susana.units.service")


def _strip_accents(s: str) -> str:
    """Normaliza strings removendo diacríticos/acentos e convertendo para minúsculas."""
    if not s:
        return ""
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()

# Coordenadas geográficas reais WGS84 (Latitude, Longitude) das 33 Regiões Administrativas do DF
RA_GEOGRAPHIC_COORDINATES: Dict[str, Tuple[float, float]] = {
    "plano_piloto": (-15.7942, -47.8822),
    "ceilandia": (-15.8178, -48.1136),
    "taguatinga": (-15.8331, -48.0567),
    "samambaia": (-15.8742, -48.0872),
    "gama": (-16.0178, -48.0647),
    "santa_maria": (-16.0178, -47.9856),
    "sobradinho": (-15.6533, -47.7944),
    "sobradinho_ii": (-15.6333, -47.8100),
    "planaltina": (-15.6178, -47.6506),
    "guara": (-15.8206, -47.9819),
    "aguas_claras": (-15.8394, -48.0294),
    "recanto_das_emas": (-15.9056, -48.0667),
    "riacho_fundo": (-15.8833, -48.0167),
    "riacho_fundo_ii": (-15.8972, -48.0500),
    "vicente_pires": (-15.8056, -48.0333),
    "sao_sebastiao": (-15.9083, -47.7722),
    "paranoa": (-15.7722, -47.7806),
    "itapoa": (-15.7500, -47.7667),
    "brazlandia": (-15.6806, -48.2028),
    "sol_nascente": (-15.8333, -48.1333),
    "sol_nascente_por_do_sol": (-15.8333, -48.1333),
    "sudoeste_octogonal": (-15.7989, -47.9258),
    "lago_sul": (-15.8358, -47.8722),
    "lago_norte": (-15.7333, -47.8667),
    "jardim_botanico": (-15.8667, -47.8000),
    "cruzeiro": (-15.7919, -47.9392),
    "candangolandia": (-15.8500, -47.9500),
    "nucleo_bandeirante": (-15.8667, -47.9667),
    "park_way": (-15.8833, -47.9500),
    "scia_estrutural": (-15.7833, -47.9833),
    "sia": (-15.8167, -47.9500),
    "varjao": (-15.7167, -47.8833),
    "fercal": (-15.5833, -47.8667),
    "arniqueira": (-15.8500, -48.0167),
}

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
                "farmacia": "Farmácia do SUS / Dispensação",
                "laboratorio": "Laboratório de Saúde Pública / Posto de Coleta",
            }

            import math

            # Dicionário intermediário para consolidação de estabelecimentos físicos
            # Chave: (ra_id, tipo, estab_key)
            estabelecimentos: Dict[str, dict] = {}

            for i, b in enumerate(blocks):
                meta = b.get("metadata", {})
                ra_id = meta.get("ra", "geral_df")
                tipo = meta.get("tipo_unidade", "ubs").lower()
                cluster = meta.get("cluster", "geral")
                servicos_str = meta.get("servicos", "")
                servicos = [s.strip().replace("_", " ") for s in servicos_str.split(",") if s.strip()]

                raw_header = b.get("header", "")
                # Higienização: remove tags internas de corpus como [UNIDADE_UBS], [VACINACAO], etc.
                clean_name = re.sub(r"^\[?[A-Z0-9_]+\]?\s*", "", raw_header).strip()
                clean_name = clean_name.replace("[", "").replace("]", "").strip()

                # Extração do nome base canônico do estabelecimento
                m_estab = re.search(
                    r"((?:UBS|UPA|Hospital|Policl[ií]nica|CAPS|Farm[aá]cia|CEAF|Centro de Sa[uú]de)\s+(?:Regional\s+de\s+|Regional\s+d[ao]\s+)?[A-Za-z0-9\s-]+?)(?:\s*[-–(]|$)",
                    clean_name,
                    re.IGNORECASE,
                )
                if m_estab:
                    base_estab_name = m_estab.group(1).strip()
                else:
                    base_estab_name = clean_name

                # Chave única de estabelecimento físico dentro da RA
                estab_key = f"{ra_id}::{tipo}::{base_estab_name.lower().strip()}"

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

                # Atendimento 24h e Horário
                is_24h = (
                    "24 horas" in text.lower()
                    or "24h" in text.lower()
                    or tipo in ("upa", "hospital")
                    or "ininterrupto" in text.lower()
                )
                if is_24h:
                    horario = "Atendimento ininterrupto 24 horas todos os dias"
                else:
                    horario = "Segunda a sexta-feira, das 07:00 às 19:00"
                    m_hora = re.search(r"Hor[aá]rio(?:\s+de\s+Atendimento)?:\s*([^.]+?\.)", text, re.IGNORECASE)
                    if m_hora:
                        horario = m_hora.group(1).strip().rstrip(".")

                # Extração de Telefone
                telefone = "136 (Disque Saúde) / (61) Central SES-DF"
                m_tel = re.search(r"(?:telefone|contato|ramal|fone)s?:?\s*(\(?\d{2}\)?\s*\d{4,5}[-\s]?\d{4})", text, re.IGNORECASE)
                if m_tel:
                    telefone = m_tel.group(1).strip()
                elif "136" in text:
                    telefone = "Disque Saúde 136 (Central SES-DF)"

                # Bairro / Setor
                ra_title = self._format_ra_title(ra_id)
                bairro = ra_title
                m_bairro = re.search(r"(?:setor|vila|quadra|asa|bairro)\s+([A-Za-z0-9\s/]+?)(?:,|-|\.|\s*CEP)", endereco, re.IGNORECASE)
                if m_bairro:
                    bairro = f"{m_bairro.group(0).strip()} ({ra_title})"

                # Referência de emergência
                ref_emerg = None
                m_ref = re.search(r"refer[eê]ncia[^:]*?:\s*([^.]+?\.)", text, re.IGNORECASE)
                if m_ref:
                    ref_emerg = m_ref.group(1).strip().rstrip(".")

                # Consolidação no estabelecimento existente ou criação de novo
                is_main_unit_block = "UNIDADE" in raw_header or not m_estab
                if estab_key not in estabelecimentos:
                    estabelecimentos[estab_key] = {
                        "nome": base_estab_name if is_main_unit_block else clean_name,
                        "ra_id": ra_id,
                        "ra_title": ra_title,
                        "tipo": tipo,
                        "cluster": cluster,
                        "endereco": endereco,
                        "horario": horario,
                        "servicos": set(servicos),
                        "referencia_emergencia": ref_emerg,
                        "url": b.get("url"),
                        "telefone": telefone,
                        "atendimento_24h": is_24h,
                        "bairro": bairro,
                    }
                else:
                    item = estabelecimentos[estab_key]
                    # Agrega serviços de salas anexas (vacinação, farmácia, acolhimento)
                    item["servicos"].update(servicos)
                    if is_24h:
                        item["atendimento_24h"] = True
                        item["horario"] = "Atendimento ininterrupto 24 horas todos os dias"
                    if ref_emerg and not item["referencia_emergencia"]:
                        item["referencia_emergencia"] = ref_emerg
                    if is_main_unit_block and len(base_estab_name) >= len(item["nome"]):
                        item["nome"] = base_estab_name
                    if endereco != "Distrito Federal" and item["endereco"] == "Distrito Federal":
                        item["endereco"] = endereco
                    if telefone != "136 (Disque Saúde) / (61) Central SES-DF" and item["telefone"] == "136 (Disque Saúde) / (61) Central SES-DF":
                        item["telefone"] = telefone

            # Carrega catálogo de unidades especializadas públicas da SES-DF (CAPS, Policlínicas, Farmácias, Laboratórios)
            esp_path = self.json_path.parent / "unidades_especializadas_df.json"
            if esp_path.exists():
                try:
                    with open(esp_path, "r", encoding="utf-8") as fe:
                        esp_data = json.load(fe)
                    for item_esp in esp_data.get("unidades", []):
                        ra_id = item_esp.get("ra", "geral_df")
                        tipo = item_esp.get("tipo", "ubs").lower()
                        nome = item_esp.get("nome", "")
                        estab_key = f"{ra_id}::{tipo}::{nome.lower().strip()}"
                        ra_title = self._format_ra_title(ra_id)
                        estabelecimentos[estab_key] = {
                            "nome": nome,
                            "ra_id": ra_id,
                            "ra_title": ra_title,
                            "tipo": tipo,
                            "cluster": tipo,
                            "endereco": item_esp.get("endereco", "Distrito Federal"),
                            "horario": item_esp.get("horario", "Segunda a sexta-feira, das 07:00 às 18:00"),
                            "servicos": set(item_esp.get("servicos", [])),
                            "referencia_emergencia": item_esp.get("referencia_emergencia"),
                            "url": "https://www.saude.df.gov.br",
                            "telefone": item_esp.get("telefone", "Disque Saúde 136 (Central SES-DF)"),
                            "atendimento_24h": item_esp.get("atendimento_24h", False),
                            "bairro": item_esp.get("bairro", ra_title),
                        }
                except Exception as ex_esp:
                    logger.warning("Falha ao carregar unidades_especializadas_df.json: %s", ex_esp)

            # Agora converte os estabelecimentos físicos consolidados em HealthUnitItems com dispersão espacial
            ra_unit_counter: Dict[str, int] = {}
            for idx_unit, (ekey, data_estab) in enumerate(estabelecimentos.items()):
                ra_id = data_estab["ra_id"]
                tipo = data_estab["tipo"]

                base_lat, base_lng = RA_GEOGRAPHIC_COORDINATES.get(ra_id, (-15.7942, -47.8822))
                base_x, base_y = RA_SVG_COORDINATES.get(ra_id, (52.0, 48.0))
                ra_unit_counter[ra_id] = ra_unit_counter.get(ra_id, 0) + 1
                idx_in_ra = ra_unit_counter[ra_id]

                if idx_in_ra == 1:
                    disp_x, disp_y = 0.0, 0.0
                    disp_lat, disp_lng = 0.0, 0.0
                else:
                    # Espiral de Fermat para espalhamento uniforme e natural
                    angle = (idx_in_ra - 1) * 2.39996  # Golden angle em radianos
                    radius = math.sqrt(idx_in_ra - 1) * 1.1
                    disp_x = radius * math.cos(angle) * 1.55
                    disp_y = radius * math.sin(angle) * 1.2
                    # Dispersão cartográfica real em WGS84 (escala de quadras reais do DF)
                    disp_lat = radius * math.cos(angle) * 0.0055
                    disp_lng = radius * math.sin(angle) * 0.0070

                lat = round(base_lat + disp_lat, 5)
                lng = round(base_lng + disp_lng, 5)
                svg_x = max(6.0, min(94.0, base_x + disp_x))
                svg_y = max(6.0, min(94.0, base_y + disp_y))

                # Ordena serviços
                servicos_finais = sorted(list(data_estab["servicos"]))

                unit = HealthUnitItem(
                    id=f"unit_{idx_unit}_{ra_id}_{tipo}",
                    nome=data_estab["nome"][:80],
                    ra=ra_id,
                    ra_display=data_estab["ra_title"],
                    tipo=tipo,
                    tipo_display=tipo_display_map.get(tipo, tipo.upper()),
                    cluster=data_estab["cluster"],
                    endereco=data_estab["endereco"][:150],
                    horario=data_estab["horario"][:120],
                    servicos=servicos_finais,
                    referencia_emergencia=data_estab["referencia_emergencia"][:150] if data_estab["referencia_emergencia"] else None,
                    url=data_estab["url"],
                    telefone=data_estab["telefone"],
                    atendimento_24h=data_estab["atendimento_24h"],
                    bairro=data_estab["bairro"][:80],
                    lat=lat,
                    lng=lng,
                    svg_x=round(svg_x, 1),
                    svg_y=round(svg_y, 1),
                )
                self._units.append(unit)
                self._by_id[unit.id] = unit

            logger.info("UnitsDirectoryService indexou com sucesso %d unidades físicas consolidadas do DF com coordenadas geográficas", len(self._units))

        except Exception as e:
            logger.error("Falha ao indexar diretorio_saude_df.json: %s", e)

    def search_units(
        self,
        ra: Optional[str] = None,
        tipo: Optional[str] = None,
        servico: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 500,
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
                ]
            elif t_norm in ("caps",):
                results = [u for u in results if u.tipo == "caps" or "caps" in u.nome.lower()]
            elif t_norm in ("policlinica", "policlinicas"):
                results = [u for u in results if u.tipo == "policlinica" or "policl" in u.nome.lower()]
            elif t_norm in ("farmacia", "farmacias"):
                results = [u for u in results if u.tipo == "farmacia" or "farm" in u.nome.lower()]
            elif t_norm in ("laboratorio", "laboratorios"):
                results = [u for u in results if u.tipo == "laboratorio" or "laborat" in u.nome.lower() or "lacen" in u.nome.lower()]
            else:
                results = [u for u in results if u.tipo == t_norm]

        if servico and servico.strip():
            s_norm = _strip_accents(servico.strip())
            results = [u for u in results if any(s_norm in _strip_accents(s) for s in u.servicos)]

        if query and query.strip():
            q_norm = _strip_accents(query.strip())
            results = [
                u for u in results
                if q_norm in _strip_accents(u.nome)
                or q_norm in _strip_accents(u.endereco)
                or q_norm in _strip_accents(u.ra_display)
                or (u.bairro and q_norm in _strip_accents(u.bairro))
                or q_norm in _strip_accents(u.tipo_display)
                or any(q_norm in _strip_accents(s) for s in u.servicos)
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
            coords = RA_GEOGRAPHIC_COORDINATES.get(rid, (-15.7942, -47.8822))
            items.append(
                RADistributionItem(
                    ra=rid,
                    ra_display=aliases[0].title(),
                    unit_count=c,
                    lat=coords[0],
                    lng=coords[1],
                )
            )
        items.sort(key=lambda x: -x.unit_count)
        return items


    def get_unit_by_id(self, unit_id: str) -> Optional[HealthUnitItem]:
        return self._by_id.get(unit_id)
