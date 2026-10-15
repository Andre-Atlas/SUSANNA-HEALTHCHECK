"""Interpretação de datas e horários em português (referência: quinta, 15/10/2026 09:00)."""
from __future__ import annotations

from datetime import date, datetime, time

import pytest

from app.agenda.dateparse import parse_pt_datetime

NOW = datetime(2026, 10, 15, 9, 0)


@pytest.mark.parametrize(
    "text, expected_date, expected_time",
    [
        ("amanhã", date(2026, 10, 16), None),
        ("hoje às 18h", date(2026, 10, 15), time(18, 0)),
        ("depois de amanhã", date(2026, 10, 17), None),
        ("próxima terça às 14h", date(2026, 10, 20), time(14, 0)),
        ("terça-feira", date(2026, 10, 20), None),
        ("na quinta que vem", date(2026, 10, 22), None),
        ("dia 20", date(2026, 10, 20), None),
        ("dia 10", date(2026, 11, 10), None),
        ("dia 20 às 10", date(2026, 10, 20), time(10, 0)),
        ("20/11", date(2026, 11, 20), None),
        ("05/01", date(2027, 1, 5), None),
        ("20/11/2026 14:30", date(2026, 11, 20), time(14, 30)),
        ("3 de dezembro", date(2026, 12, 3), None),
        ("daqui a 2 semanas", date(2026, 10, 29), None),
        ("daqui a três dias", date(2026, 10, 18), None),
        ("2 da tarde", None, time(14, 0)),
        ("9 da manhã", None, time(9, 0)),
        ("14h30", None, time(14, 30)),
        ("meio-dia", None, time(12, 0)),
        ("segunda dose da vacina", None, None),
    ],
)
def test_parse_pt_datetime(text, expected_date, expected_time):
    parsed = parse_pt_datetime(text, NOW)
    assert parsed.date == expected_date
    assert parsed.time == expected_time
