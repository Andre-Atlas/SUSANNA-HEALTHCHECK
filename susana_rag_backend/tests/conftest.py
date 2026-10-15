"""Fixtures compartilhadas: banco SQLite isolado por teste para cadastro, sessões e agenda."""
from __future__ import annotations

import random

import pytest

from app.agenda.storage import AgendaStorage, get_agenda_storage
from app.chat_sessions.router import get_chat_session_storage
from app.chat_sessions.storage import ChatSessionStorage
from app.citizen.auth import AuthStorage, get_auth_storage
from app.citizen.security import login_rate_limiter
from app.citizen.storage import CitizenStorage, get_citizen_storage


def generate_valid_cpf() -> str:
    prefix = [random.randint(1, 8)] + [random.randint(0, 9) for _ in range(8)]
    for weight_start in (10, 11):
        s = sum(prefix[i] * (weight_start - i) for i in range(len(prefix)))
        d = 11 - (s % 11)
        prefix.append(0 if d >= 10 else d)
    return "".join(str(d) for d in prefix)


@pytest.fixture
def citizen_storage(tmp_path) -> CitizenStorage:
    return CitizenStorage(db_path=tmp_path / "susana_test.db")


@pytest.fixture(autouse=True)
def isolated_app_storage(citizen_storage):
    """Toda rota que usa o SQLite da aplicação passa a usar o banco temporário."""
    from app.main import app

    auth = AuthStorage(citizen_storage)
    agenda = AgendaStorage(citizen_storage)
    sessions = ChatSessionStorage(citizen_storage)
    app.dependency_overrides[get_citizen_storage] = lambda: citizen_storage
    app.dependency_overrides[get_auth_storage] = lambda: auth
    app.dependency_overrides[get_agenda_storage] = lambda: agenda
    app.dependency_overrides[get_chat_session_storage] = lambda: sessions
    login_rate_limiter.reset(*list(login_rate_limiter._failures))
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def register_user():
    """Cria uma conta via API e devolve (headers, resposta)."""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    def _register(**extra):
        payload = {"nome_completo": "Ana Paula de Souza", "cpf": generate_valid_cpf(), "senha": "segura123", **extra}
        resp = client.post("/api/citizen/register", json=payload)
        assert resp.status_code == 201, resp.text
        data = resp.json()
        return {"Authorization": f"Bearer {data['token']}"}, data, payload

    return _register
