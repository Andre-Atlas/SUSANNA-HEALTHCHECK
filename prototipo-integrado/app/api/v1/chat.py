import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.providers.ollama import OllamaProvider
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["IA / Chat"])


@router.post("", response_model=ChatResponse, summary="Processa uma pergunta para a Susana")
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)) -> ChatResponse:
    provider = OllamaProvider()
    service = ChatService(db=db, llm=provider, embeddings=provider)
    return await service.process(str(request.session_id), request.message, request.context)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Limpa o contexto de uma conversa")
async def clear_chat_session(session_id: uuid.UUID) -> None:
    ChatService.clear_session(str(session_id))
