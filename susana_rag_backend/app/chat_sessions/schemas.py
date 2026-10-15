"""Schemas para Gerenciamento de Múltiplas Sessões de Chat (Janelas Separadas)."""
from __future__ import annotations

from typing import Any, List, Optional
from pydantic import BaseModel, Field


class ChatSessionSummary(BaseModel):
    id: str
    citizen_id: Optional[str] = None
    title: str
    last_preview: Optional[str] = None
    created_at: str
    updated_at: str
    message_count: int = 0


class CreateSessionRequest(BaseModel):
    citizen_id: Optional[str] = None
    title: Optional[str] = Field("Nova conversa", max_length=120)


class ChatMessageItem(BaseModel):
    id: str
    session_id: str
    role: str  # 'user' ou 'assistant'
    content: str
    source: Optional[str] = None
    citations: Optional[List[dict]] = None
    options: Optional[List[dict]] = None
    created_at: str


class SaveMessageRequest(BaseModel):
    session_id: str
    role: str
    content: str
    source: Optional[str] = None
    citations: Optional[List[dict]] = None
    options: Optional[List[dict]] = None
