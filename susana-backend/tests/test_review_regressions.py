import uuid
from types import SimpleNamespace

import pytest

from app.db.base import Base
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.models.source import Source
from app.providers.fakes import FakeEmbeddingProvider
from app.services.rag_service import DocumentAlreadyProcessingError, RAGService
from app.services.retrieval_service import RetrievalService


class _Rows:
    def __init__(self, rows):
        self.rows = rows

    def all(self):
        return self.rows


class _UpdateResult:
    rowcount = 0


class _AlreadyProcessingSession:
    async def execute(self, _statement):
        return _UpdateResult()

    async def rollback(self):
        pass

    async def get(self, _model, _record_id):
        return object()


class _RetrievalSession:
    async def execute(self, _statement):
        row = (
            SimpleNamespace(id=uuid.uuid4(), content="Evidência recuperada"),
            SimpleNamespace(
                id=uuid.uuid4(),
                title="Documento oficial",
                url="https://saude.df.gov.br/documento",
                source_updated_at=None,
                status="indexed",
            ),
            SimpleNamespace(
                id=uuid.uuid4(), name="SES-DF", url="https://saude.df.gov.br/"
            ),
            0.1,
        )
        return _Rows([row])


@pytest.mark.asyncio
async def test_ingestion_claim_rejects_duplicate_processing():
    service = RAGService(_AlreadyProcessingSession(), FakeEmbeddingProvider(dimensions=8))

    with pytest.raises(DocumentAlreadyProcessingError):
        await service.ingest_document(uuid.uuid4())


@pytest.mark.asyncio
async def test_retrieval_returns_document_url_as_evidence_link():
    service = RetrievalService(_RetrievalSession(), FakeEmbeddingProvider(dimensions=8))

    results = await service.search("pergunta")

    assert results[0]["source_url"] == "https://saude.df.gov.br/documento"


def test_orm_metadata_matches_removed_category_and_unique_chunk_index():
    assert "categories" not in Base.metadata.tables
    assert any(
        index.name == "uq_document_chunks_document_chunk_index" and index.unique
        for index in DocumentChunk.__table__.indexes
    )


def test_created_timestamps_are_immutable_on_orm_updates():
    assert Source.__table__.c.created_at.onupdate is None
    assert Document.__table__.c.created_at.onupdate is None
    assert Document.__table__.c.collected_at.onupdate is None