"""
Interpretação determinística de datas e horários em português (sem dependências)
===============================================================================
Exemplos aceitos: "hoje", "amanhã", "depois de amanhã", "terça", "próxima sexta-feira",
"dia 20", "20/11", "20/11/2026", "20 de novembro", "daqui a 2 semanas",
"às 14h", "14:30", "14h30", "2 da tarde", "9 da manhã", "meio-dia".
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import List, Optional, Tuple

WEEKDAYS = {"segunda": 0, "terca": 1, "quarta": 2, "quinta": 3, "sexta": 4, "sabado": 5, "domingo": 6}
MONTHS = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "abril": 4, "maio": 5, "junho": 6, "julho": 7,
    "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}
NUMBER_WORDS = {"um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3, "quatro": 4, "cinco": 5}


def normalize(text: str) -> str:
    s = "".join(c for c in unicodedata.normalize("NFD", text or "") if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s.lower()).strip()


@dataclass
class ParsedDateTime:
    date: Optional[date] = None
    time: Optional[time] = None
    spans: List[Tuple[int, int]] = field(default_factory=list)


def _add_months(d: date, months: int) -> date:
    y, m = divmod(d.month - 1 + months, 12)
    for day in (d.day, 30, 29, 28):
        try:
            return date(d.year + y, m + 1, day)
        except ValueError:
            continue
    raise ValueError("data inválida")


def _safe_date(y: int, m: int, d: int) -> Optional[date]:
    try:
        return date(y, m, d)
    except ValueError:
        return None


def _parse_date(s: str, today: date) -> Tuple[Optional[date], Optional[Tuple[int, int]]]:
    m = re.search(r"\bdepois de amanha\b", s)
    if m:
        return today + timedelta(days=2), m.span()
    m = re.search(r"\bamanha\b", s)
    if m:
        return today + timedelta(days=1), m.span()
    m = re.search(r"\bhoje\b", s)
    if m:
        return today, m.span()

    m = re.search(r"\bdaqui a (\d+|um|uma|dois|duas|tres|quatro|cinco) (dias?|semanas?|mes|meses)\b", s)
    if m:
        n = int(m.group(1)) if m.group(1).isdigit() else NUMBER_WORDS[m.group(1)]
        unit = m.group(2)
        if unit.startswith("dia"):
            return today + timedelta(days=n), m.span()
        if unit.startswith("semana"):
            return today + timedelta(weeks=n), m.span()
        return _add_months(today, n), m.span()

    m = re.search(r"\b(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?\b", s)
    if m:
        d, mo = int(m.group(1)), int(m.group(2))
        if m.group(3):
            y = int(m.group(3))
            y = y + 2000 if y < 100 else y
            return _safe_date(y, mo, d), m.span()
        cand = _safe_date(today.year, mo, d)
        if cand and cand < today:
            cand = _safe_date(today.year + 1, mo, d)
        return cand, m.span()

    month_re = "|".join(MONTHS)
    m = re.search(rf"\b(?:dia )?(\d{{1,2}}) de ({month_re})(?: de (\d{{4}}))?\b", s)
    if m:
        d, mo = int(m.group(1)), MONTHS[m.group(2)]
        y = int(m.group(3)) if m.group(3) else today.year
        cand = _safe_date(y, mo, d)
        if cand and not m.group(3) and cand < today:
            cand = _safe_date(y + 1, mo, d)
        return cand, m.span()

    m = re.search(r"\bdia (\d{1,2})\b", s)
    if m:
        d = int(m.group(1))
        cand = _safe_date(today.year, today.month, d)
        if cand is None or cand < today:
            nxt = _add_months(today.replace(day=1), 1)
            cand = _safe_date(nxt.year, nxt.month, d)
        return cand, m.span()

    wd_re = "|".join(WEEKDAYS)
    m = re.search(rf"\b(?:(?:na |no )?(?:proxima|proximo) )?({wd_re})(?:[- ]feira)?(?: que vem)?\b(?! (?:dose|vez|via|opcao))", s)
    if m:
        delta = (WEEKDAYS[m.group(1)] - today.weekday()) % 7 or 7
        return today + timedelta(days=delta), m.span()

    return None, None


def _period_hour(h: int, period: Optional[str]) -> int:
    if period in ("tarde", "noite") and h < 12:
        return h + 12
    if period == "manha" and h == 12:
        return 0
    return h


def _parse_time(s: str) -> Tuple[Optional[time], Optional[Tuple[int, int]]]:
    m = re.search(r"\bmeio[- ]dia\b", s)
    if m:
        return time(12, 0), m.span()
    m = re.search(r"\b(\d{1,2})(?::|h)(\d{2})\b", s)
    if m and int(m.group(1)) < 24 and int(m.group(2)) < 60:
        return time(int(m.group(1)), int(m.group(2))), m.span()
    m = re.search(r"\b(?:as |a )?(\d{1,2})(?: ?h(?:oras?)?)? da (manha|tarde|noite)\b", s)
    if m and int(m.group(1)) <= 12:
        return time(_period_hour(int(m.group(1)), m.group(2)), 0), m.span()
    m = re.search(r"\b(\d{1,2}) ?(?:h|horas)\b", s)
    if m and int(m.group(1)) < 24:
        return time(int(m.group(1)), 0), m.span()
    m = re.search(r"\b(?:as|a partir das) (\d{1,2})\b", s)
    if m and int(m.group(1)) < 24:
        return time(int(m.group(1)), 0), m.span()
    return None, None


def parse_pt_datetime(text: str, now: Optional[datetime] = None) -> ParsedDateTime:
    now = now or datetime.now()
    s = normalize(text)
    result = ParsedDateTime()
    d, span = _parse_date(s, now.date())
    if span:
        result.date = d
        result.spans.append(span)
        # Remove o trecho da data para que "dia 20" não seja lido como horário
        s = s[: span[0]] + " " * (span[1] - span[0]) + s[span[1]:]
    t, tspan = _parse_time(s)
    if tspan:
        result.time = t
        result.spans.append(tspan)
    return result
