from fastapi.testclient import TestClient

from app.main import app


def test_root():
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "Susana API"


def test_openapi_and_routes():
    paths = TestClient(app).get("/openapi.json").json()["paths"]
    expected = {
        "/api/v1/health", "/api/v1/chat", "/api/v1/unidades", "/api/v1/servicos",
        "/api/v1/fontes", "/api/v1/rag/documents", "/api/v1/rag/search", "/api/v1/ckan/packages",
    }
    assert expected.issubset(paths)
