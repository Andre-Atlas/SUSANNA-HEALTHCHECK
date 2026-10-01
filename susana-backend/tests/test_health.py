from types import SimpleNamespace

import httpx
import pytest

from app.api.v1 import health


class _Database:
    async def execute(self, _statement):
        return self

    async def scalar(self, _statement):
        return 0

    def first(self):
        return ("0.8.5",)


class _OllamaResponse:
    is_success = True

    def __init__(self, models):
        self.models = models

    def json(self):
        return {"models": [{"name": name} for name in self.models]}


class _OllamaClient:
    models = []

    def __init__(self, **_kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        pass

    async def get(self, _url):
        return _OllamaResponse(self.models)


@pytest.mark.asyncio
async def test_dependencies_reports_unconfigured_ollama_models(monkeypatch):
    monkeypatch.setattr(
        health,
        "get_settings",
        lambda: SimpleNamespace(
            ollama_base_url="http://localhost:11434",
            ollama_model="",
            embedding_model="",
        ),
    )
    monkeypatch.setattr(httpx, "AsyncClient", _OllamaClient)

    result = await health.dependencies(_Database())

    assert result["postgres"] == "ok"
    assert result["pgvector"] == "ok"
    assert result["indexed_documents"] == "0"
    assert result["ollama"] == "error"
    assert result["ollama_chat"] == "not_configured"
    assert result["ollama_embeddings"] == "not_configured"


@pytest.mark.asyncio
async def test_dependencies_reports_ready_when_both_models_are_installed(monkeypatch):
    monkeypatch.setattr(
        health,
        "get_settings",
        lambda: SimpleNamespace(
            ollama_base_url="http://localhost:11434",
            ollama_model="llama3.2:3b",
            embedding_model="nomic-embed-text:latest",
        ),
    )
    monkeypatch.setattr(httpx, "AsyncClient", _OllamaClient)
    monkeypatch.setattr(
        _OllamaClient,
        "models",
        ["llama3.2:3b", "nomic-embed-text:latest"],
    )

    result = await health.dependencies(_Database())

    assert result["ollama"] == "ok"
    assert result["ollama_chat"] == "ok"
    assert result["ollama_embeddings"] == "ok"