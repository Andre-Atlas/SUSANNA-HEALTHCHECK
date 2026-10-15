"""Cadastro opcional, login CPF + senha, sessões persistentes e LGPD."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.citizen.security import hash_password, verify_password
from app.main import app
from tests.conftest import generate_valid_cpf

client = TestClient(app)


def test_password_hash_roundtrip():
    stored = hash_password("segura123", iterations=1000)
    assert stored.startswith("pbkdf2_sha256$1000$")
    assert verify_password("segura123", stored)
    assert not verify_password("errada123", stored)
    assert not verify_password("segura123", None)


def test_minimal_register_returns_token_and_partial_profile(register_user):
    headers, body, _ = register_user()
    assert body["citizen"]["perfil_completo"] is False
    assert body["citizen"]["data_nascimento"] is None
    assert body["citizen"]["ra_display"] == "Distrito Federal"
    me = client.get("/api/citizen/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["id"] == body["citizen"]["id"]


def test_me_without_token_is_401_no_demo_user():
    resp = client.get("/api/citizen/me")
    assert resp.status_code == 401
    assert client.get("/api/citizen/me", headers={"Authorization": "Bearer invalido"}).status_code == 401


def test_register_rejects_weak_password_and_duplicate(register_user):
    weak = client.post("/api/citizen/register", json={"nome_completo": "Ana", "cpf": generate_valid_cpf(), "senha": "123"})
    assert weak.status_code == 422
    _, _, payload = register_user()
    dup = client.post("/api/citizen/register", json=payload)
    assert dup.status_code == 409


def test_login_generic_error_and_rate_limit(register_user):
    _, _, payload = register_user()
    for _ in range(5):
        r = client.post("/api/citizen/login", json={"cpf": payload["cpf"], "senha": "errada999"})
        assert r.status_code == 401
        assert r.json()["detail"] == "CPF ou senha incorretos."
    blocked = client.post("/api/citizen/login", json={"cpf": payload["cpf"], "senha": payload["senha"]})
    assert blocked.status_code == 429


def test_remember_me_controls_session_length(register_user):
    _, _, payload = register_user()
    now = datetime.now(timezone.utc)
    short = client.post("/api/citizen/login", json={"cpf": payload["cpf"], "senha": payload["senha"]}).json()
    long_ = client.post("/api/citizen/login", json={"cpf": payload["cpf"], "senha": payload["senha"], "lembrar": True}).json()
    assert short["remember"] is False and long_["remember"] is True
    assert datetime.fromisoformat(short["expires_at"]) - now < timedelta(hours=25)
    assert datetime.fromisoformat(long_["expires_at"]) - now > timedelta(days=29)


def test_expired_session_is_rejected(register_user, citizen_storage):
    headers, _, _ = register_user()
    with citizen_storage._get_connection() as conn:
        conn.execute("UPDATE auth_sessions SET expires_at = ?", ((datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(),))
    assert client.get("/api/citizen/me", headers=headers).status_code == 401


def test_logout_revokes_token(register_user):
    headers, _, _ = register_user()
    assert client.post("/api/citizen/logout", headers=headers).status_code == 200
    assert client.get("/api/citizen/me", headers=headers).status_code == 401


def test_update_profile_conditions_and_gestante_sync(register_user):
    headers, _, _ = register_user()
    r = client.patch(
        "/api/citizen/me",
        headers=headers,
        json={"data_nascimento": "1990-03-10", "sexo_biologico": "F", "ra_residencia": "ceilandia",
              "condicoes": ["diabetes", "gestante"], "telefone": "(61) 99999-1234"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["gestante"] is True and data["perfil_completo"] is True
    assert data["telefone"] == "61999991234"
    # Sexo masculino remove a condição gestante
    r2 = client.patch("/api/citizen/me", headers=headers, json={"sexo_biologico": "M"}).json()
    assert r2["gestante"] is False and r2["condicoes"] == ["diabetes"]
    bad = client.patch("/api/citizen/me", headers=headers, json={"condicoes": ["inexistente"]})
    assert bad.status_code == 422


def test_users_cannot_touch_each_other(register_user):
    h1, b1, _ = register_user()
    h2, b2, _ = register_user()
    client.patch("/api/citizen/me", headers=h2, json={"ra_residencia": "gama"})
    assert client.get("/api/citizen/me", headers=h1).json()["ra_residencia"] == "geral_df"


def test_change_password_and_delete_account(register_user):
    headers, _, payload = register_user()
    bad = client.post("/api/citizen/me/password", headers=headers, json={"senha_atual": "errada123", "nova_senha": "nova12345"})
    assert bad.status_code == 403
    ok = client.post("/api/citizen/me/password", headers=headers, json={"senha_atual": payload["senha"], "nova_senha": "nova12345"})
    assert ok.status_code == 200
    login = client.post("/api/citizen/login", json={"cpf": payload["cpf"], "senha": "nova12345"})
    assert login.status_code == 200

    assert client.request("DELETE", "/api/citizen/me", headers=headers, json={"senha": "errada"}).status_code == 403
    assert client.request("DELETE", "/api/citizen/me", headers=headers, json={"senha": "nova12345"}).status_code == 200
    assert client.get("/api/citizen/me", headers=headers).status_code == 401
    assert client.post("/api/citizen/login", json={"cpf": payload["cpf"], "senha": "nova12345"}).status_code == 401


def test_responses_never_leak_password_hash(register_user):
    headers, body, _ = register_user()
    assert "password_hash" not in str(body)
    assert "pbkdf2" not in client.get("/api/citizen/me", headers=headers).text


def test_conditions_catalog():
    items = client.get("/api/citizen/conditions").json()
    ids = {i["id"] for i in items}
    assert {"diabetes", "gestante", "hipertensao"} <= ids
