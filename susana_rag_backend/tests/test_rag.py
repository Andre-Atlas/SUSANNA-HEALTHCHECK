"""
Testes do RAG Pipeline — Susana
================================
Cobre: busca vetorial, guardrails, cache, healthcheck, input validation.
"""
import time
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    """TestClient como context manager para disparar lifespan (index_documents)."""
    with TestClient(app) as c:
        yield c


# ===========================================================================
# Healthcheck (B-4)
# ===========================================================================
class TestHealthcheck:
    def test_health_returns_ok(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["pipeline_ready"] is True


# ===========================================================================
# Guardrails — bloqueio clínico (B-2)
# ===========================================================================
class TestGuardrails:
    def test_blocks_diagnosis_request(self, client):
        r = client.post("/api/chat", json={"message": "Que remédio devo tomar para dor de cabeça?"})
        assert r.status_code == 200
        data = r.json()
        assert data["is_blocked"] is True
        assert "informações administrativas" in data["response"]

    def test_blocks_symptom_report(self, client):
        r = client.post("/api/chat", json={"message": "Estou sentindo muita febre e dor no corpo"})
        assert r.status_code == 200
        data = r.json()
        assert data["is_blocked"] is True

    def test_allows_administrative_with_clinical_word(self, client):
        """'horário' é override administrativo mesmo que 'tratamento' apareça."""
        r = client.post("/api/chat", json={"message": "Qual o horário de funcionamento da UBS?"})
        assert r.status_code == 200
        data = r.json()
        assert data["is_blocked"] is False

    def test_allows_pharmacy_query(self, client):
        """Perguntar sobre farmácia do SUS não é clínico."""
        r = client.post("/api/chat", json={"message": "Onde fica a farmácia do SUS?"})
        assert r.status_code == 200
        data = r.json()
        assert data["is_blocked"] is False

    def test_allows_vaccination_query(self, client):
        r = client.post("/api/chat", json={"message": "Calendário de vacinação para idosos"})
        assert r.status_code == 200
        data = r.json()
        assert data["is_blocked"] is False


# ===========================================================================
# RAG — busca vetorial real (B-1)
# ===========================================================================
class TestRAGRetrieval:
    def test_finds_samu_info(self, client):
        r = client.post("/api/chat", json={"message": "SAMU 192"})
        assert r.status_code == 200
        data = r.json()
        assert data["is_blocked"] is False
        assert data["source"] is not None
        assert "SAMU" in data["source"]

    def test_finds_vaccination_info(self, client):
        r = client.post("/api/chat", json={"message": "vacinas para idosos acima de 60 anos"})
        assert r.status_code == 200
        data = r.json()
        assert data["is_blocked"] is False
        assert data["source"] is not None

    def test_finds_pharmacy_info(self, client):
        r = client.post("/api/chat", json={"message": "Onde retirar medicamento pelo SUS?"})
        assert r.status_code == 200
        data = r.json()
        assert data["is_blocked"] is False

    def test_out_of_context_returns_no_source(self, client):
        """Perguntas totalmente fora do domínio retornam fallback sem alucinação."""
        r = client.post("/api/chat", json={"message": "Como fazer bolo de chocolate?"})
        assert r.status_code == 200
        data = r.json()
        assert data["is_blocked"] is False


# ===========================================================================
# Cache semântico (B-9)
# ===========================================================================
class TestSemanticCache:
    def test_second_query_is_faster(self, client):
        """A segunda chamada da mesma pergunta deve vir do cache."""
        msg = {"message": "Endereço da UBS 1 Asa Sul"}

        # Primeira chamada — popula cache
        r1 = client.post("/api/chat", json=msg)
        assert r1.status_code == 200

        # Segunda chamada — deve ser cache hit
        t0 = time.perf_counter()
        r2 = client.post("/api/chat", json=msg)
        t1 = time.perf_counter()

        assert r2.status_code == 200
        assert (t1 - t0) < 2.0


# ===========================================================================
# Input Validation (B-6)
# ===========================================================================
class TestInputValidation:
    def test_empty_message_rejected(self, client):
        r = client.post("/api/chat", json={"message": ""})
        assert r.status_code == 422

    def test_missing_message_field(self, client):
        r = client.post("/api/chat", json={})
        assert r.status_code == 422


# ===========================================================================
# Latency tracking
# ===========================================================================
class TestLatencyTracking:
    def test_response_includes_latency(self, client):
        r = client.post("/api/chat", json={"message": "Horário da UBS"})
        assert r.status_code == 200
        data = r.json()
        assert "latency_ms" in data
        assert isinstance(data["latency_ms"], int)
        assert data["latency_ms"] >= 0
