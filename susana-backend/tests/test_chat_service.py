import uuid

import pytest

from app.schemas.chat import ChatContext
from app.providers.fakes import FakeEmbeddingProvider, FakeLLMProvider
from app.services.chat_service import ChatService


@pytest.mark.asyncio
async def test_fake_providers_are_deterministic():
    embedding = FakeEmbeddingProvider(dimensions=8)
    a = await embedding.embed("abc")
    b = await embedding.embed("abc")
    assert a == b
    assert len(a) == 8
    assert (await FakeLLMProvider().generate("prompt")).startswith("Resposta de teste")


def test_session_id_is_uuid_compatible():
    assert isinstance(uuid.uuid4(), uuid.UUID)


@pytest.mark.asyncio
async def test_structured_chat_evidence_uses_unit_id_not_chunk_id(monkeypatch):
    service = ChatService(
        db=object(),
        llm=FakeLLMProvider(),
        embeddings=FakeEmbeddingProvider(dimensions=8),
    )
    unit_id = uuid.uuid4()
    source_id = uuid.uuid4()

    async def structured_evidence(*_args):
        return [
            {
                "content": "UBS de teste em Samambaia.",
                "source_id": source_id,
                "source_name": "SES-DF",
                "source_url": "https://saude.df.gov.br/",
                "document_title": "UBS de teste",
                "source_updated_at": None,
                "structured": True,
                "score": 1.0,
                "unit_id": unit_id,
            }
        ]

    monkeypatch.setattr(service, "_structured_evidence", structured_evidence)
    session_id = str(uuid.uuid4())
    response = await service.process(
        session_id,
        "Quais UBS existem em Samambaia?",
        ChatContext(ra="Samambaia"),
    )
    service.clear_session(session_id)

    assert response.evidence[0].unit_id == unit_id
    assert response.evidence[0].chunk_id is None
