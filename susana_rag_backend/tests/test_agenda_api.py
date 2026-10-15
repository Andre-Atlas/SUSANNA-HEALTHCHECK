"""API da Agenda e agendamento via chat com confirmação."""
from __future__ import annotations

import json
from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _stream(message, headers=None, **extra):
    resp = client.post("/api/chat/stream", headers=headers or {}, json={"message": message, **extra})
    assert resp.status_code == 200, resp.text
    return [json.loads(line) for line in resp.text.splitlines() if line.strip()]


def test_agenda_requires_login():
    assert client.get("/api/agenda/overview").status_code == 401


def test_event_crud_and_ownership(register_user):
    h1, _, _ = register_user()
    h2, _, _ = register_user()
    day = (date.today() + timedelta(days=3)).isoformat()
    created = client.post("/api/agenda/events", headers=h1, json={"tipo": "exame", "titulo": "Hemograma", "data_evento": day, "horario": "07:30"})
    assert created.status_code == 201, created.text
    eid = created.json()["id"]

    assert client.patch(f"/api/agenda/events/{eid}", headers=h2, json={"status": "concluido"}).status_code == 404
    assert client.delete(f"/api/agenda/events/{eid}", headers=h2).status_code == 404
    assert client.get("/api/agenda", headers=h2).json() == []

    upd = client.patch(f"/api/agenda/events/{eid}", headers=h1, json={"horario": "08:00"})
    assert upd.json()["horario"] == "08:00"
    ov = client.get("/api/agenda/overview", headers=h1).json()
    assert [e["id"] for e in ov["eventos"]] == [eid]
    assert ov["perfil_incompleto"] is True
    assert client.post("/api/agenda/events", headers=h1, json={"tipo": "exame", "titulo": "X", "data_evento": "31/12", "horario": "25:00"}).status_code == 422
    assert client.delete(f"/api/agenda/events/{eid}", headers=h1).status_code == 200


def test_pending_vaccines_and_mark_as_taken(register_user):
    headers, _, _ = register_user(data_nascimento="1958-03-01", sexo_biologico="F")
    pend = client.get("/api/agenda/vaccines/pending", headers=headers).json()
    assert any(v["vaccine_id"] == "vac_influenza_anual" for v in pend)

    rec = client.post("/api/agenda/vaccines/records", headers=headers, json={"vaccine_id": "vac_influenza_anual"})
    assert rec.status_code == 201
    pend2 = client.get("/api/agenda/vaccines/pending", headers=headers).json()
    assert all(v["vaccine_id"] != "vac_influenza_anual" for v in pend2)
    assert client.post("/api/agenda/vaccines/records", headers=headers, json={"vaccine_id": "vac_inexistente"}).status_code == 422

    assert client.delete(f"/api/agenda/vaccines/records/{rec.json()['id']}", headers=headers).status_code == 200
    sched = client.post("/api/agenda/vaccines/vac_influenza_anual/schedule", headers=headers,
                        json={"data_evento": (date.today() + timedelta(days=2)).isoformat()})
    assert sched.status_code == 201 and sched.json()["tipo"] == "vacina"


def test_anonymous_scheduling_message_offers_login():
    events = _stream("marca uma consulta no dentista amanhã às 10h")
    assert not any(e["type"] == "agenda_proposal" for e in events)
    done = events[-1]
    assert done["options"][0]["action"] == "open_auth"


def test_chat_proposal_confirm_flow(register_user):
    headers, _, _ = register_user()
    other, _, _ = register_user()
    events = _stream("marca uma consulta no dentista amanhã às 10h", headers)
    proposal = next(e["proposal"] for e in events if e["type"] == "agenda_proposal")
    assert proposal["titulo"] == "Consulta – Dentista" and proposal["faltando"] == []
    pid = proposal["proposal_id"]

    # Nada é gravado antes da confirmação
    assert client.get("/api/agenda", headers=headers).json() == []
    assert client.post(f"/api/agenda/proposals/{pid}/confirm", headers=other, json={}).status_code == 404

    ok = client.post(f"/api/agenda/proposals/{pid}/confirm", headers=headers, json={"horario": "10:30"})
    assert ok.status_code == 201, ok.text
    assert ok.json()["origem"] == "chat" and ok.json()["horario"] == "10:30"
    assert client.post(f"/api/agenda/proposals/{pid}/confirm", headers=headers, json={}).status_code == 409


def test_chat_follow_up_completes_pending_proposal(register_user):
    headers, _, _ = register_user()
    first = _stream("quero marcar um exame de ultrassom", headers)
    p1 = next(e["proposal"] for e in first if e["type"] == "agenda_proposal")
    assert p1["faltando"] == ["data", "horario"]
    second = _stream("depois de amanhã às 15h", headers, pending_proposal_id=p1["proposal_id"])
    p2 = next(e["proposal"] for e in second if e["type"] == "agenda_proposal")
    assert p2["proposal_id"] == p1["proposal_id"] and p2["faltando"] == []
    assert p2["horario"] == "15:00"


def test_medication_reminder_is_not_blocked_by_clinical_guardrail(register_user):
    headers, _, _ = register_user()
    events = _stream("me lembra de tomar o remédio todo dia às 8h", headers)
    proposal = next(e["proposal"] for e in events if e["type"] == "agenda_proposal")
    assert proposal["tipo"] == "medicamento" and proposal["recorrencia"] == "diaria"
