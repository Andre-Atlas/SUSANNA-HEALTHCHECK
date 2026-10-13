"""Rotas FastAPI para Múltiplas Sessões e Histórico de Chat."""
from __future__ import annotations

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends

from app.chat_sessions.schemas import (
    ChatMessageItem,
    ChatSessionSummary,
    CreateSessionRequest,
    SaveMessageRequest,
)
from app.chat_sessions.storage import ChatSessionStorage

logger = logging.getLogger("susana.chat_sessions.router")
router = APIRouter(prefix="/api/chat/sessions", tags=["chat_sessions"])

_session_storage: Optional[ChatSessionStorage] = None


def get_chat_session_storage() -> ChatSessionStorage:
    global _session_storage
    if _session_storage is None:
        _session_storage = ChatSessionStorage()
    return _session_storage


@router.get("", response_model=List[ChatSessionSummary])
def list_sessions(
    citizen_id: Optional[str] = None,
    storage: ChatSessionStorage = Depends(get_chat_session_storage),
):
    sessions = storage.list_sessions(citizen_id)
    if not sessions:
        # Cria automaticamente uma primeira sessão de boas-vindas
        s = storage.create_session(CreateSessionRequest(citizen_id=citizen_id, title="Atendimento SUS-DF"))
        return [s]
    return sessions


@router.post("", response_model=ChatSessionSummary)
def create_session(
    req: CreateSessionRequest,
    storage: ChatSessionStorage = Depends(get_chat_session_storage),
):
    return storage.create_session(req)


@router.get("/{session_id}/messages", response_model=List[ChatMessageItem])
def get_session_messages(
    session_id: str,
    storage: ChatSessionStorage = Depends(get_chat_session_storage),
):
    return storage.get_messages(session_id)


@router.post("/messages", response_model=ChatMessageItem)
def save_message(
    req: SaveMessageRequest,
    storage: ChatSessionStorage = Depends(get_chat_session_storage),
):
    return storage.save_message(req)


@router.delete("/{session_id}")
def delete_session(
    session_id: str,
    storage: ChatSessionStorage = Depends(get_chat_session_storage),
):
    success = storage.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    return {"status": "deleted", "id": session_id}
