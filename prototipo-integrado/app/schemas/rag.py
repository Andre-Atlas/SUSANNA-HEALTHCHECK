import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class DocumentCreate(BaseModel):
    source_id: uuid.UUID
    title: str = Field(min_length=1, max_length=300)
    category: str = Field(min_length=1, max_length=100)
    url: HttpUrl
    content: str = Field(min_length=1)
    published_at: datetime | None = None
    source_updated_at: datetime | None = None


class DocumentUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    category: str = Field(min_length=1, max_length=100)
    url: HttpUrl
    content: str = Field(min_length=1)
    published_at: datetime | None = None
    source_updated_at: datetime | None = None


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source_id: uuid.UUID
    title: str
    category: str
    url: str
    published_at: datetime | None
    source_updated_at: datetime | None
    collected_at: datetime
    status: str
    content_hash: str | None
    created_at: datetime
    updated_at: datetime | None


class IngestResponse(BaseModel):
    document_id: uuid.UUID
    status: str
    chunks_created: int


class ChunkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_id: uuid.UUID
    chunk_index: int
    content: str
    created_at: datetime


class RagSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)


class RagSearchSource(BaseModel):
    name: str
    url: str


class RagSearchResult(BaseModel):
    document_id: uuid.UUID
    chunk_id: uuid.UUID
    score: float
    content: str
    source: RagSearchSource


class RagSearchResponse(BaseModel):
    query: str
    results: list[RagSearchResult]
