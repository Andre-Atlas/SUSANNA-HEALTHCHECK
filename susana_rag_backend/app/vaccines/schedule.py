"""
Regras determinísticas de vacinas pendentes por perfil
=====================================================
Fonte: Calendário Nacional de Vacinação (PNI/Ministério da Saúde)
https://www.gov.br/saude/pt-br/vacinacao/calendario

As regras usam os ids de ``OFFICIAL_PNI_VACCINES`` (app/vaccines/service.py).
O resultado é uma orientação: a interface sempre recomenda confirmar na UBS,
pois o histórico real fica na caderneta de vacinação do cidadão.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, FrozenSet, Iterable, List, Optional, Sequence

from pydantic import BaseModel

from app.vaccines.service import OFFICIAL_PNI_VACCINES

# Condições que tornam a pessoa público prioritário para Influenza
INFLUENZA_CONDITIONS = frozenset({
    "gestante", "diabetes", "cardiopatia", "asma", "dpoc", "imunossupressao",
    "doenca_renal_cronica", "obesidade", "hiv", "cancer", "deficiencia",
})
PNEUMO23_CONDITIONS = frozenset({"imunossupressao", "cardiopatia", "doenca_renal_cronica", "dpoc", "hiv", "diabetes"})


@dataclass(frozen=True)
class DoseRule:
    vaccine_id: str
    dose_num: int
    label: str
    min_age_months: int
    max_age_months: Optional[int] = None  # exclusivo; None = sem limite
    requires_any: FrozenSet[str] = frozenset()  # condições exigidas (qualquer uma)
    recurring_months: Optional[int] = None  # reforços periódicos (dT, Influenza)
    note: Optional[str] = None


def _r(vid: str, dose: int, label: str, min_m: int, max_m: Optional[int] = None, **kw) -> DoseRule:
    return DoseRule(vid, dose, label, min_m, max_m, **kw)


Y = 12  # meses por ano
DOSE_RULES: List[DoseRule] = [
    _r("vac_bcg", 1, "Dose única", 0, 5 * Y),
    _r("vac_hepb_rn", 1, "Dose ao nascer", 0, 1),
    _r("vac_penta_2m", 1, "1ª dose", 2, 7 * Y),
    _r("vac_penta_2m", 2, "2ª dose", 4, 7 * Y),
    _r("vac_penta_2m", 3, "3ª dose", 6, 7 * Y),
    _r("vac_vip_2m", 1, "1ª dose", 2, 5 * Y),
    _r("vac_vip_2m", 2, "2ª dose", 4, 5 * Y),
    _r("vac_vip_2m", 3, "3ª dose", 6, 5 * Y),
    _r("vac_pneumo10_2m", 1, "1ª dose", 2, 5 * Y),
    _r("vac_pneumo10_2m", 2, "2ª dose", 4, 5 * Y),
    _r("vac_pneumo10_2m", 3, "Reforço", 12, 5 * Y),
    _r("vac_rotavirus_2m", 1, "1ª dose", 2, 4),
    _r("vac_rotavirus_2m", 2, "2ª dose", 4, 8),
    _r("vac_meningo_c_3m", 1, "1ª dose", 3, 5 * Y),
    _r("vac_meningo_c_3m", 2, "2ª dose", 5, 5 * Y),
    _r("vac_meningo_c_3m", 3, "Reforço", 12, 5 * Y),
    _r("vac_fa_9m", 1, "1ª dose", 9, 60 * Y),
    _r("vac_fa_9m", 2, "Reforço (4 anos)", 4 * Y, 5 * Y),
    _r("vac_triplice_viral_12m", 1, "1ª dose", 12, 60 * Y),
    _r("vac_triplice_viral_12m", 2, "2ª dose", 15, 30 * Y),
    _r("vac_hepa_15m", 1, "Dose única", 15, 5 * Y),
    _r("vac_dtp_reforco", 1, "1º reforço", 15, 7 * Y),
    _r("vac_dtp_reforco", 2, "2º reforço", 4 * Y, 7 * Y),
    _r("vac_hpv_adol", 1, "Dose única", 9 * Y, 15 * Y),
    _r("vac_meningo_acwy_adol", 1, "Dose única", 11 * Y, 15 * Y),
    _r("vac_dt_adulto", 1, "Reforço a cada 10 anos", 20 * Y, None, recurring_months=10 * Y,
       note="Confira a data do último reforço na sua caderneta."),
    _r("vac_influenza_anual", 1, "Dose anual", 60 * Y, None, recurring_months=Y),
    _r("vac_influenza_anual", 1, "Dose anual", 6, 6 * Y, recurring_months=Y),
    _r("vac_influenza_anual", 1, "Dose anual (grupo prioritário)", 6, None,
       requires_any=INFLUENZA_CONDITIONS, recurring_months=Y),
    _r("vac_pneumo23_idoso", 1, "Dose", 60 * Y, None,
       note="Verifique a elegibilidade na sua UBS."),
    _r("vac_pneumo23_idoso", 1, "Dose (condição crônica)", 5 * Y, None,
       requires_any=PNEUMO23_CONDITIONS, note="Indicada pelos CRIE; verifique na sua UBS."),
    _r("vac_dtpa_gestante", 1, "Dose a cada gestação (a partir da 20ª semana)", 10 * Y, None,
       requires_any=frozenset({"gestante"}), recurring_months=10),
    _r("vac_hepb_gestante", 1, "Esquema conforme caderneta", 10 * Y, None,
       requires_any=frozenset({"gestante"}), note="Leve a caderneta para avaliar o esquema."),
]

_VACCINE_NAMES: Dict[str, str] = {v["id"]: v["nome"] for v in OFFICIAL_PNI_VACCINES}
VALID_VACCINE_IDS = frozenset(_VACCINE_NAMES)


class PendingVaccine(BaseModel):
    vaccine_id: str
    dose_num: int
    nome: str
    dose_label: str
    status: str  # atrasada | agora | proxima
    data_sugerida: str
    motivo: str


class VaccineRecord(BaseModel):
    id: str
    vaccine_id: str
    dose_num: int
    data_aplicacao: Optional[str] = None
    created_at: str


def add_months(d: date, months: int) -> date:
    y, m = divmod(d.month - 1 + months, 12)
    year, month = d.year + y, m + 1
    days_in_month = [31, 29 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 28,
                     31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]
    return date(year, month, min(d.day, days_in_month))


def _parse(d: Optional[str]) -> Optional[date]:
    if not d:
        return None
    try:
        return datetime.strptime(d[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def _status(due: date, today: date) -> Optional[str]:
    if due <= today:
        return "atrasada" if (today - due).days > 30 else "agora"
    if (due - today).days <= 90:
        return "proxima"
    return None


def compute_pending(
    data_nascimento: Optional[str],
    condicoes: Iterable[str],
    records: Sequence[VaccineRecord],
    today: Optional[date] = None,
) -> List[PendingVaccine]:
    """Retorna, por vacina, a próxima dose pendente segundo o perfil."""
    birth = _parse(data_nascimento)
    if birth is None:
        return []
    today = today or date.today()
    conds = set(condicoes)
    taken: Dict[tuple, List[date]] = {}
    for r in records:
        taken.setdefault((r.vaccine_id, r.dose_num), []).append(_parse(r.data_aplicacao) or _parse(r.created_at) or today)

    pending: Dict[str, PendingVaccine] = {}
    for rule in DOSE_RULES:
        if rule.vaccine_id in pending:
            continue  # mostra só a próxima dose de cada vacina
        if rule.requires_any and not (rule.requires_any & conds):
            continue
        start = add_months(birth, rule.min_age_months)
        if rule.max_age_months is not None and today >= add_months(birth, rule.max_age_months):
            continue
        doses = taken.get((rule.vaccine_id, rule.dose_num))
        if doses:
            if rule.recurring_months is None:
                continue
            start = max(start, add_months(max(doses), rule.recurring_months))
        elif rule.recurring_months is not None and start < today:
            start = today  # sem registro de dose periódica: orientar agora
        status = _status(start, today)
        if status is None:
            continue
        if status == "atrasada" and rule.note and not doses:
            status = "agora"  # sem histórico conhecido: orientar a conferir, não alarmar
        motivo = rule.note or ("Indicada para o seu perfil." if rule.requires_any else "Calendário Nacional de Vacinação.")
        pending[rule.vaccine_id] = PendingVaccine(
            vaccine_id=rule.vaccine_id,
            dose_num=rule.dose_num,
            nome=_VACCINE_NAMES.get(rule.vaccine_id, rule.vaccine_id),
            dose_label=rule.label,
            status=status,
            data_sugerida=start.isoformat(),
            motivo=motivo,
        )
    order = {"atrasada": 0, "agora": 1, "proxima": 2}
    return sorted(pending.values(), key=lambda p: (order[p.status], p.data_sugerida))
