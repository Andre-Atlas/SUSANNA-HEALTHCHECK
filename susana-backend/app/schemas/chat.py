import uuid
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class ChatStatus(str, Enum):
    ANSWERED = "answered"
    NEEDS_CLARIFICATION = "needs_clarification"
    OUT_OF_SCOPE = "out_of_scope"
    NO_EVIDENCE = "no_evidence"
    ERROR = "error"


class ChatContext(BaseModel):
    ra: str | None = Field(default=None, max_length=100)
    cep: str | None = Field(default=None, max_length=20)


class ChatRequest(BaseModel):
    session_id: uuid.UUID
    message: str = Field(min_length=1, max_length=4000)
    context: ChatContext | None = None

    @field_validator("message")
    @classmethod
    def clean_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("A mensagem não pode ser vazia.")
        return value


class SourceReference(BaseModel):
    id: uuid.UUID
    title: str
    source: str
    url: str
    updated_at: str | None = None


class EvidenceReference(BaseModel):
    chunk_id: uuid.UUID
    content: str
    score: float
    source: SourceReference


class Clarification(BaseModel):
    field: str
    question: str


class ChatResponse(BaseModel):
    session_id: uuid.UUID
    reply: str
    status: ChatStatus
    intent: str | None = None
    sources: list[SourceReference] = Field(default_factory=list)
    evidence: list[EvidenceReference] = Field(default_factory=list)
    clarification: Clarification | None = None
