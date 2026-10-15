"""Rotas FastAPI para Múltiplas Sessões e Histórico de Chat.

O titular é identificado pelo token Bearer (nunca por ``citizen_id`` enviado pelo cliente).
Sessões de visitantes (citizen_id NULL) só são acessíveis por quem conhece o id.
"""
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
from app.citizen.auth import get_current_citizen_optional
from app.citizen.schemas import CitizenProfileResponse

logger = logging.getLogger("susana.chat_sessions.router")
router = APIRouter(prefix="/api/chat/sessions", tags=["chat_sessions"])

_session_storage: Optional[ChatSessionStorage] = None


def get_chat_session_storage() -> ChatSessionStorage:
    global _session_storage
    if _session_storage is None:
        _session_storage = ChatSessionStorage()
    return _session_storage


def _require_access(storage: ChatSessionStorage, session_id: str, citizen: Optional[CitizenProfileResponse]) -> None:
    exists, owner = storage.get_session_owner(session_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    if owner is not None and (citizen is None or citizen.id != owner):
        # 404 para não revelar a existência de sessões de terceiros
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")


@router.get("", response_model=List[ChatSessionSummary])
def list_sessions(
    citizen: Optional[CitizenProfileResponse] = Depends(get_current_citizen_optional),
    storage: ChatSessionStorage = Depends(get_chat_session_storage),
):
    if citizen is None:
        return []
    sessions = storage.list_sessions(citizen.id)
    if not sessions:
        # Cria automaticamente uma primeira sessão de boas-vindas para o titular
        return [storage.create_session(CreateSessionRequest(citizen_id=citizen.id, title="Atendimento SUS-DF"))]
    return sessions


@router.post("", response_model=ChatSessionSummary)
def create_session(
    req: CreateSessionRequest,
    citizen: Optional[CitizenProfileResponse] = Depends(get_current_citizen_optional),
    storage: ChatSessionStorage = Depends(get_chat_session_storage),
):
    req.citizen_id = citizen.id if citizen else None
    return storage.create_session(req)


@router.get("/{session_id}/messages", response_model=List[ChatMessageItem])
def get_session_messages(
    session_id: str,
    citizen: Optional[CitizenProfileResponse] = Depends(get_current_citizen_optional),
    storage: ChatSessionStorage = Depends(get_chat_session_storage),
):
    _require_access(storage, session_id, citizen)
    return storage.get_messages(session_id)


@router.post("/messages", response_model=ChatMessageItem)
def save_message(
    req: SaveMessageRequest,
    citizen: Optional[CitizenProfileResponse] = Depends(get_current_citizen_optional),
    storage: ChatSessionStorage = Depends(get_chat_session_storage),
):
    _require_access(storage, req.session_id, citizen)
    return storage.save_message(req)


@router.delete("/{session_id}")
def delete_session(
    session_id: str,
    citizen: Optional[CitizenProfileResponse] = Depends(get_current_citizen_optional),
    storage: ChatSessionStorage = Depends(get_chat_session_storage),
):
    _require_access(storage, session_id, citizen)
    storage.delete_session(session_id)
    return {"status": "deleted", "id": session_id}
