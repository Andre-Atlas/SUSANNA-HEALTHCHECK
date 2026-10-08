"""Diretório estruturado de unidades (ideia do StructuredSearchService da branch develop_sam).

A busca semântica entrega só 3 trechos, então nunca lista "todas as UBS de Samambaia" (são 13).
Este módulo carrega em memória as tabelas de unidades de CORPUS/Arquivos e, quando a pergunta
cita um TIPO de unidade e uma REGIÃO ADMINISTRATIVA, monta um trecho-evidência com a lista
completa — que entra como trecho [1] para o LLM, com citação ao arquivo de origem.

Não substitui a busca: perguntas sem tipo + região seguem só pelo RAG.
"""
from __future__ import annotations

import csv
import logging
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from app.ports import RetrievedChunk

logger = logging.getLogger("susana.directory")

# arquivo (stem) → rótulo do tipo de unidade
UNIT_FILES: Dict[str, str] = {
    "Unidade_Básica_de_Saúde": "UBS",
    "UBS_-_Consultório_na_rua": "UBS — Consultório na Rua",
    "UBS_-_Saúde_Indígena": "UBS — Saúde Indígena",
    "UBS_-_Unidades_Prisionais": "UBS — Unidade Prisional",
    "Unidades_de_Pronto_Atendi": "UPA",
    "Hospitais": "Hospital",
    "Centros_de_Atenção_Psicos": "CAPS",
    "Policlínicas": "Policlínica",
    "Centros_Especializados": "Centro Especializado",
    "Outras_Unidades_de_Saúde": "Outra unidade",
}
NAME_COLUMNS = ("Estabelecimento", "Centros Especializado", "Unidades de Pronto Atendimento")
HOURS_COLUMNS = ("Horário", "Horários de Fucionamento")

# termo na pergunta (normalizado) → tipos aceitos
TYPE_PATTERNS = [
    (r"\b(ubs|postos?|postinhos?|unidades? basicas?|centros? de saude)\b", {"UBS"}),
    (r"\b(upas?|pronto atendimento)\b", {"UPA"}),
    (r"\bhospita(l|is)\b", {"Hospital"}),
    (r"\b(caps|saude mental|psicossocia(l|is))\b", {"CAPS"}),
    (r"\bpoliclinicas?\b", {"Policlínica"}),
    (r"\bcentros? especializados?\b", {"Centro Especializado"}),
]
# serviço pedido que filtra UBS por coluna SIM/NÃO
SERVICE_FILTERS = [
    (r"\bvacin", "Sala Vacina", "sala de vacina"),
    (r"\bfarmacia", "Farmácia", "farmácia"),
    (r"\b(coleta|exame de sangue)", "Coleta de Material", "coleta de material"),
]
RA_ALIASES = {"sol nascente": "SOL NASCENTE/POR DO SOL", "por do sol": "SOL NASCENTE/POR DO SOL",
              "asa sul": "PLANO PILOTO", "asa norte": "PLANO PILOTO", "brasilia": "PLANO PILOTO",
              "recanto": "RECANTO DAS EMAS", "scia": "ESTRUTURAL"}
MAX_LISTED = 15


def _norm(text: str) -> str:
    text = "".join(c for c in unicodedata.normalize("NFD", text.lower()) if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9/ ]+", " ", text)).strip()


@dataclass(frozen=True)
class Unit:
    kind: str
    name: str
    ra: str
    address: str
    cep: str
    hours: str
    flags: Dict[str, str]
    source_file: str


class UnitDirectory:
    def __init__(self, folder: Path):
        self.units: List[Unit] = []
        for stem, kind in UNIT_FILES.items():
            path = folder / f"{stem}.csv"
            if path.exists():
                self.units.extend(self._load(path, kind))
        self.ras = sorted({_norm(u.ra) for u in self.units if u.ra}, key=len, reverse=True)
        logger.info("Diretório de unidades: %d unidades, %d regiões", len(self.units), len(self.ras))

    @staticmethod
    def _load(path: Path, kind: str) -> List[Unit]:
        out = []
        with path.open(encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f, delimiter=";"):
                row = {(k or "").strip(): (v or "").strip() for k, v in row.items()}
                name = next((row[c] for c in NAME_COLUMNS if row.get(c)), "") or f"{kind} ({row.get('Região Administrativa', '')})"
                address = row.get("Endereço", "")
                if row.get("Número"):
                    address = f"{address}, {row['Número']}"
                hours = next((row[c] for c in HOURS_COLUMNS if row.get(c)), "")
                flags = {col: row[col] for col, _, _ in [(c, p, l) for p, c, l in SERVICE_FILTERS] if row.get(col)}
                out.append(Unit(kind, name, row.get("Região Administrativa", ""), address, row.get("CEP", ""),
                                hours, flags, path.name))
        return out

    # ------------------------------------------------------------------
    def find_ra(self, question: str) -> Optional[str]:
        q = f" {_norm(question)} "
        for alias, ra in RA_ALIASES.items():
            if f" {alias} " in q:
                return _norm(ra)
        return next((ra for ra in self.ras if f" {ra} " in q), None)

    def lookup(self, question: str) -> Optional[RetrievedChunk]:
        """Trecho-evidência com as unidades do tipo e região pedidos, ou None."""
        q = _norm(question)
        ra = self.find_ra(question)
        if not ra:
            return None
        kinds = set().union(*[k for p, k in TYPE_PATTERNS if re.search(p, q)]) if any(
            re.search(p, q) for p, _ in TYPE_PATTERNS) else set()
        service = next(((col, label) for p, col, label in SERVICE_FILTERS if re.search(p, q)), None)
        if not kinds and service:
            kinds = {"UBS"}                       # "onde vacinar em Samambaia" → UBS com sala de vacina
        if not kinds:
            return None
        units = [u for u in self.units if _norm(u.ra) == ra and
                 (u.kind in kinds or ("UBS" in kinds and u.kind.startswith("UBS")))]
        if service:
            # só unidades que DECLARAM o serviço (Consultório na Rua etc. não têm a coluna)
            units = [u for u in units if u.flags.get(service[0], "").upper() == "SIM"]
        numbered = re.search(r"\b(ubs|upa|caps|hospital)\s+(\d{1,3})\b", q)
        if numbered:
            # "UBS 2 de Planaltina" → só a unidade 2 (aceita "UBS 02")
            n = int(numbered.group(2))
            wanted = {f"{numbered.group(1)} {v}" for v in (str(n), f"{n:02d}", f"{n:03d}")}
            exact = [u for u in units if any(f" {w} " in f" {_norm(u.name)} " for w in wanted)]
            units = exact or units
        if not units:
            return None
        ra_label = units[0].ra
        kinds_label = ", ".join(sorted({u.kind for u in units}))
        lines = []
        detailed = len(units) <= 3            # poucas unidades: todos os campos; lista longa: compacta
        for i, u in enumerate(units[:MAX_LISTED], 1):
            parts = [f"Endereço: {u.address}" + (f", CEP {u.cep}" if u.cep and detailed else "")]
            if u.hours:
                parts.append(f"Horário: {u.hours}")
            if detailed:
                parts += [f"{col}: {val}" for col, val in u.flags.items()]
            elif service:
                parts.append(f"{service[0]}: SIM")
            lines.append(f"{i}. {u.name} — " + "; ".join(parts))
        if len(units) > MAX_LISTED:
            lines.append(f"... e mais {len(units) - MAX_LISTED} unidades nesta região.")
        files = ", ".join(sorted({u.source_file for u in units}))
        what = f"{kinds_label}" + (f" com {service[1]}" if service else "")
        header = f"[DIRETORIO] {what} em {ra_label} ({len(units)} unidades; {files})"
        text = header + "\n" + "\n".join(lines)
        return RetrievedChunk(id=f"diretorio:{_norm(what)}:{ra}", text=text, source=header, distance=0.0, url=None)
