import logging
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession

from app.providers.base import EmbeddingProvider, LLMProvider
from app.schemas.chat import (
    ChatContext, ChatResponse, ChatStatus, Clarification, EvidenceReference, SourceReference,
)
from app.services.prompt_builder import build_prompt
from app.services.retrieval_service import RetrievalService
from app.services.scope_service import ScopeService

logger = logging.getLogger(__name__)
_SESSIONS: dict[str, list[str]] = defaultdict(list)


class ChatService:
    def __init__(self, db: AsyncSession, llm: LLMProvider, embeddings: EmbeddingProvider):
        self.db = db
        self.llm = llm
        self.retrieval = RetrievalService(db, embeddings)
        self.scope = ScopeService()

    async def process(self, session_id: str, message: str, context: ChatContext | None) -> ChatResponse:
        scope, intent = self.scope.classify(message)
        if scope == "out_of_scope":
            return ChatResponse(
                session_id=session_id,
                reply=("Posso ajudar com informações sobre serviços e acesso ao SUS no "
                       "Distrito Federal, mas não realizo diagnóstico ou prescrição."),
                status=ChatStatus.OUT_OF_SCOPE,
                intent=intent,
            )
        if scope == "needs_clarification":
            return ChatResponse(
                session_id=session_id,
                reply=("Posso ajudar com informações do SUS no Distrito Federal. "
                       "Tente informar a unidade, serviço ou situação que você deseja consultar."),
                status=ChatStatus.NEEDS_CLARIFICATION,
                intent=intent,
                clarification=Clarification(
                    field="question", question="Qual serviço ou informação do SUS-DF você procura?"
                ),
            )
        try:
            evidence = await self.retrieval.search(message)
        except Exception:
            logger.exception("Falha no retrieval para a sessão %s", session_id)
            return ChatResponse(
                session_id=session_id,
                reply="Não consegui consultar a base de informações neste momento.",
                status=ChatStatus.ERROR,
                intent=intent,
            )
        if not evidence:
            return ChatResponse(
                session_id=session_id,
                reply="Não encontrei evidências suficientes nas fontes disponíveis para responder com segurança.",
                status=ChatStatus.NO_EVIDENCE,
                intent=intent,
            )

        previous = "\n".join(_SESSIONS[session_id][-4:])
        prompt = build_prompt(message, context, evidence, previous)
        try:
            reply = await self.llm.generate(prompt)
        except Exception:
            logger.exception("Falha no LLM para a sessão %s", session_id)
            return ChatResponse(
                session_id=session_id,
                reply="Não consegui gerar a resposta neste momento.",
                status=ChatStatus.ERROR,
                intent=intent,
            )

        _SESSIONS[session_id].append(f"Usuário: {message}\nAssistente: {reply}")
        source_map = {}
        evidence_refs = []
        for item in evidence:
            source_key = str(item["source_id"])
            source = source_map.setdefault(source_key, SourceReference(
                id=item["source_id"],
                title=item["document_title"],
                source=item["source_name"],
                url=item["source_url"],
                updated_at=item["source_updated_at"].isoformat() if item["source_updated_at"] else None,
            ))
            evidence_refs.append(EvidenceReference(
                chunk_id=item["chunk_id"], content=item["content"], score=round(item["score"], 4), source=source
            ))
        return ChatResponse(
            session_id=session_id,
            reply=reply,
            status=ChatStatus.ANSWERED,
            intent=intent,
            sources=list(source_map.values()),
            evidence=evidence_refs,
        )
