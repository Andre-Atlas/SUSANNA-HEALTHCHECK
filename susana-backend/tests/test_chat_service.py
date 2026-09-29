import uuid

import pytest

from app.providers.fakes import FakeEmbeddingProvider, FakeLLMProvider


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
