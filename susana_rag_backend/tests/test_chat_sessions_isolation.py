"""Isolamento do histórico de chat entre titulares e visitantes."""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_anonymous_listing_is_empty_and_session_is_private_by_id():
    s = client.post("/api/chat/sessions", json={"title": "Visitante", "citizen_id": "forjado"}).json()
    assert s["citizen_id"] is None
    assert client.get("/api/chat/sessions").json() == []
    # O visitante continua acessando sua sessão pelo id
    assert client.post("/api/chat/sessions/messages", json={"session_id": s["id"], "role": "user", "content": "oi"}).status_code == 200
    assert len(client.get(f"/api/chat/sessions/{s['id']}/messages").json()) == 1


def test_user_cannot_read_or_delete_other_users_session(register_user):
    h1, b1, _ = register_user()
    h2, _, _ = register_user()
    s = client.post("/api/chat/sessions", headers=h1, json={"title": "Minha"}).json()
    assert s["citizen_id"] == b1["citizen"]["id"]

    assert client.get(f"/api/chat/sessions/{s['id']}/messages", headers=h2).status_code == 404
    assert client.get(f"/api/chat/sessions/{s['id']}/messages").status_code == 404
    assert client.post("/api/chat/sessions/messages", headers=h2, json={"session_id": s["id"], "role": "user", "content": "x"}).status_code == 404
    assert client.delete(f"/api/chat/sessions/{s['id']}", headers=h2).status_code == 404
    assert all(x["id"] != s["id"] for x in client.get("/api/chat/sessions", headers=h2).json())
    assert any(x["id"] == s["id"] for x in client.get("/api/chat/sessions", headers=h1).json())
