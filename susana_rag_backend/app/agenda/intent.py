"""
Detecção e extração de pedidos de agendamento/lembrete no chat
==============================================================
Determinístico: o modelo de linguagem não grava nada. O chat devolve uma
proposta (``AgendaProposal``) que só vira evento quando o cidadão confirma.
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from app.agenda.dateparse import normalize, parse_pt_datetime
from app.agenda.schemas import AgendaProposal

_VERB = re.compile(
    r"\b(marca|marcar|marque|marcou|agenda|agendar|agende|agendei|lembra|lembrar|lembre|lembrete|"
    r"anota|anotar|anote|salva|salvar|coloca|colocar|adiciona|adicionar|"
    r"tenho (?:uma |um )?(?:consulta|exame|retorno)|vou tomar|preciso tomar|tenho que tomar)\b"
)
_QUESTION = re.compile(r"^(como|onde|qual|quais|quando|posso|e possivel|da pra|o que|quem|aonde|existe)\b")

_TYPE_KEYWORDS = [
    ("medicamento", r"\b(remedio|medicamento|comprimido|capsula|insulina|pilula)\b"),
    ("vacina", r"\b(vacina|vacinar|dose|imunizacao)\b"),
    ("exame", r"\b(exame|ultrassom|ultrassonografia|raio[- ]?x|mamografia|preventivo|papanicolau|"
              r"eletrocardiograma|hemograma|glicemia|tomografia|ressonancia|sangue)\b"),
    ("consulta", r"\b(consulta|medico|medica|dentista|retorno|pre[- ]natal|ginecologista|pediatra|"
                 r"cardiologista|oftalmologista|dermatologista|psicologo|psicologa|nutricionista|"
                 r"ortopedista|fisioterapia|clinico)\b"),
]
_SPECIALTIES = {
    "dentista": "Dentista", "pre-natal": "Pré-natal", "pre natal": "Pré-natal", "ginecologista": "Ginecologista",
    "pediatra": "Pediatra", "cardiologista": "Cardiologista", "oftalmologista": "Oftalmologista",
    "dermatologista": "Dermatologista", "psicologo": "Psicólogo(a)", "psicologa": "Psicólogo(a)",
    "nutricionista": "Nutricionista", "ortopedista": "Ortopedista", "fisioterapia": "Fisioterapia",
    "clinico": "Clínico geral", "retorno": "Retorno",
    "ultrassom": "Ultrassom", "ultrassonografia": "Ultrassom", "mamografia": "Mamografia",
    "preventivo": "Preventivo", "papanicolau": "Preventivo", "eletrocardiograma": "Eletrocardiograma",
    "hemograma": "Hemograma", "glicemia": "Glicemia", "tomografia": "Tomografia",
    "ressonancia": "Ressonância", "sangue": "Exame de sangue", "raio-x": "Raio-X", "raio x": "Raio-X",
    "raiox": "Raio-X", "insulina": "Insulina", "influenza": "Influenza", "gripe": "Influenza",
}
_TYPE_LABEL = {"consulta": "Consulta", "exame": "Exame", "vacina": "Vacina", "medicamento": "Tomar medicamento", "outro": "Lembrete"}
_UNIT = re.compile(
    r"\b(?i:UBS|UPA|Hospital|Policl[ií]nica|CAPS|Centro de Sa[úu]de)\b"
    r"(?:\s*(?:n[ºo°.]*\s*)?\d+)?"
    r"(?:\s+[A-ZÀ-Ú][\wÀ-ú]*)*"
    r"(?:\s+(?:d[aeo]s?|em)\s+[A-ZÀ-Ú][\wÀ-ú]*(?:\s+[A-ZÀ-Ú][\wÀ-ú]*)*)?"
)
_WEEKDAY_PT = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]


def detect_scheduling_intent(message: str, now: Optional[datetime] = None) -> bool:
    s = normalize(message)
    if not _VERB.search(s):
        return False
    parsed = parse_pt_datetime(message, now)
    has_date = parsed.date is not None or parsed.time is not None
    if _QUESTION.search(s) and not has_date:
        return False  # pergunta informativa ("como agendar consulta?") segue para o RAG
    has_type = any(re.search(p, s) for _, p in _TYPE_KEYWORDS)
    return has_date or has_type or "agenda" in s or "lembrete" in s


def _detect_type(s: str) -> Optional[str]:
    for tipo, pattern in _TYPE_KEYWORDS:
        if re.search(pattern, s):
            return tipo
    return None


def _detect_specialty(s: str) -> Optional[str]:
    for key, label in _SPECIALTIES.items():
        if re.search(rf"\b{re.escape(key)}\b", s):
            return label
    return None


def _detect_unit(message: str) -> Optional[str]:
    m = _UNIT.search(message)
    if m:
        first, _, rest = re.sub(r"\s+", " ", m.group(0)).strip().partition(" ")
        first = first.upper() if first.lower() in ("ubs", "upa", "caps") else first.capitalize()
        return f"{first} {rest}".strip()
    from app.rag.nlu import RA_DICTIONARY
    s = normalize(message)
    for _rid, aliases in RA_DICTIONARY:
        for alias in aliases:
            if len(alias) > 3 and re.search(rf"\b{re.escape(normalize(alias))}\b", s):
                display = next((a for a in aliases if a != normalize(a) and normalize(a) == normalize(aliases[0])), aliases[0])
                return f"Unidade em {display.title()}"
    return None


def _detect_recurrence(s: str) -> Optional[str]:
    if re.search(r"\b(todo dia|todos os dias|diariamente|toda manha|toda noite)\b", s):
        return "diaria"
    if re.search(r"\b(toda semana|semanalmente|toda (segunda|terca|quarta|quinta|sexta|sabado|domingo))\b", s):
        return "semanal"
    return None


def _confirmation_text(p: AgendaProposal) -> str:
    if "data" in p.faltando:
        return f"Claro! Para qual dia devo anotar **{p.titulo}**?"
    d = datetime.strptime(p.data_evento, "%Y-%m-%d")
    quando = f"{_WEEKDAY_PT[d.weekday()]}, {d.strftime('%d/%m')}"
    if p.recorrencia == "diaria":
        quando = f"todos os dias a partir de {d.strftime('%d/%m')}"
    if "horario" in p.faltando:
        return f"Anotado: **{p.titulo}** em {quando}. Qual o horário?"
    onde = f" — {p.unidade_saude}" if p.unidade_saude else ""
    hora = f" às {p.horario}" if p.horario else ""
    return (
        f"Posso adicionar à sua agenda: **{p.titulo}**, {quando}{hora}{onde}. "
        "Confira os dados abaixo e toque em Confirmar."
    )


def extract_event(message: str, now: Optional[datetime] = None, base: Optional[AgendaProposal] = None) -> AgendaProposal:
    now = now or datetime.now()
    s = normalize(message)
    parsed = parse_pt_datetime(message, now)
    p = base.model_copy() if base else AgendaProposal()

    tipo = _detect_type(s)
    specialty = _detect_specialty(s)
    if tipo or not base:
        p.tipo = tipo or (base.tipo if base else "consulta")
        label = _TYPE_LABEL.get(p.tipo, "Lembrete")
        if specialty and p.tipo == "medicamento":
            p.titulo = f"{label} – {specialty}"
        elif specialty:
            p.titulo = specialty if specialty in ("Exame de sangue", "Retorno") else f"{label} – {specialty}"
        else:
            p.titulo = label
    p.recorrencia = _detect_recurrence(s) or p.recorrencia
    p.unidade_saude = _detect_unit(message) or p.unidade_saude
    if parsed.date:
        p.data_evento = parsed.date.isoformat()
    elif not p.data_evento and p.recorrencia:
        p.data_evento = now.date().isoformat()
    if parsed.time:
        p.horario = parsed.time.strftime("%H:%M")

    p.faltando = []
    if not p.data_evento:
        p.faltando.append("data")
    if not p.horario and p.tipo != "vacina":
        p.faltando.append("horario")
    p.texto_confirmacao = _confirmation_text(p)
    return p
