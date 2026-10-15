"""Detecção de pedidos de agendamento e extração dos campos do evento."""
from __future__ import annotations

from datetime import datetime

import pytest

from app.agenda.intent import detect_scheduling_intent, extract_event
from app.agenda.schemas import AgendaProposal

NOW = datetime(2026, 10, 15, 9, 0)


@pytest.mark.parametrize("msg", [
    "marca uma consulta no dentista amanhã às 10h",
    "me lembra de tomar o remédio todo dia às 8h",
    "tenho exame de sangue dia 20 às 7h30",
    "agendar vacina da gripe próxima terça",
    "coloca na agenda retorno com a pediatra 20/11",
])
def test_detects_scheduling_requests(msg):
    assert detect_scheduling_intent(msg, NOW)


@pytest.mark.parametrize("msg", [
    "como agendar consulta na UBS?",
    "onde tomar vacina",
    "quais documentos levar para marcar consulta?",
    "qual o horário da UBS de Ceilândia",
    "o que é a vacina pentavalente",
])
def test_ignores_informational_questions(msg):
    assert not detect_scheduling_intent(msg, NOW)


def test_extracts_full_consultation():
    p = extract_event("marca uma consulta no dentista amanhã às 10h na UBS 2 de Taguatinga", NOW)
    assert (p.tipo, p.titulo, p.data_evento, p.horario) == ("consulta", "Consulta – Dentista", "2026-10-16", "10:00")
    assert p.unidade_saude == "UBS 2 de Taguatinga"
    assert p.faltando == []
    assert "Confirmar" in p.texto_confirmacao


def test_daily_medication_defaults_to_today():
    p = extract_event("me lembra de tomar o remédio todo dia às 8h", NOW)
    assert p.tipo == "medicamento" and p.recorrencia == "diaria"
    assert p.data_evento == "2026-10-15" and p.horario == "08:00"


def test_missing_fields_are_requested_and_merged_on_follow_up():
    first = extract_event("quero marcar um exame de ultrassom", NOW)
    assert first.faltando == ["data", "horario"]
    assert "Para qual dia" in first.texto_confirmacao
    second = extract_event("dia 22", NOW, base=AgendaProposal(**first.model_dump()))
    assert second.titulo == "Exame – Ultrassom" and second.data_evento == "2026-10-22"
    assert second.faltando == ["horario"]
    third = extract_event("às 15h", NOW, base=second)
    assert third.horario == "15:00" and third.faltando == []
