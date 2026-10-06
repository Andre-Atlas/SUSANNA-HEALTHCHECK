import logging
from collections import defaultdict
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.providers.base import EmbeddingProvider, LLMProvider
from app.repositories.establishment_repository import EstablishmentRepository
from app.repositories.service_repository import ServiceRepository
from app.repositories.source_repository import SourceRepository
from app.schemas.chat import (
    ChatContext,
    ChatResponse,
    ChatStatus,
    Clarification,
    EvidenceReference,
    SourceReference,
)
from app.services.prompt_builder import build_prompt
from app.services.retrieval_service import RetrievalService
from app.services.scope_service import ScopeDecision, ScopeService
from app.services.structured_search_service import StructuredSearchService

logger = logging.getLogger(__name__)
_SESSIONS: dict[str, list[dict]] = defaultdict(list)
_MAX_SESSION_MESSAGES = 12


class ChatService:
    def __init__(self, db: AsyncSession, llm: LLMProvider, embeddings: EmbeddingProvider):
        self.db = db
        self.llm = llm
        self.scope = ScopeService()
        self.retrieval = RetrievalService(db, embeddings)
        self.structured = StructuredSearchService(
            EstablishmentRepository(db),
            ServiceRepository(db),
        )
        self.sources = SourceRepository(db)

    def _session_context(self, session_id: str) -> dict:
        context: dict = {}
        for item in reversed(_SESSIONS[session_id]):
            item_context = item.get("context") or {}
            for key, value in item_context.items():
                if value and key not in context:
                    context[key] = value
            if context.get("ra") and context.get("cep"):
                break
        return context

    def _save_turn(self, session_id: str, message: str, reply: str, context: dict) -> None:
        _SESSIONS[session_id].append(
            {
                "user": message,
                "assistant": reply,
                "context": context,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        del _SESSIONS[session_id][:-_MAX_SESSION_MESSAGES]

    async def _structured_evidence(self, decision: ScopeDecision, context: dict, message: str) -> list[dict]:
        if decision.intent not in {"unit_search", "vaccination", "unit_services"}:
            return []

        # Só consulta a rede estruturada quando há algum critério territorial ou
        # identificação explícita de unidade. Evita retornar uma lista arbitrária
        # para perguntas como "onde posso me vacinar?" sem localização.
        lowered = self.scope.normalize(message)
        unit_type = None
        if "ubs" in lowered:
            unit_type = "UBS"
        elif "upa" in lowered:
            unit_type = "UPA"
        elif "hospital" in lowered:
            unit_type = "Hospital"
        elif "caps" in lowered:
            unit_type = "CAPS"
        elif decision.intent == "vaccination":
            # Na ausência de outro tipo explícito, a consulta estruturada de vacinação
            # usa UBS, mas somente quando há localização/nome para filtrar.
            unit_type = "UBS"

        # Tipo sozinho não identifica uma unidade concreta; sem localização ou nome
        # explícito, evita retornar os primeiros registros arbitrariamente.
        has_structured_filter = bool(context.get("ra") or context.get("cep") or context.get("unit_name"))
        if not has_structured_filter:
            return []

        units = await self.structured.search_units(
            unit_type=unit_type,
            ra=context.get("ra"),
            cep=context.get("cep"),
            name=context.get("unit_name"),
            limit=5,
        )

        evidence: list[dict] = []
        for unit in units:
            source = await self.sources.get(unit.source_id) if unit.source_id else None
            if not source:
                continue

            if decision.intent == "unit_services":
                services = await self.structured.services_for_unit(unit.id, limit=20)
                if not services:
                    continue
                content = (
                    f"Unidade: {unit.name}. Tipo: {unit.type}. "
                    f"Região Administrativa: {unit.ra or 'não informada'}. "
                    "Serviços cadastrados: "
                    + "; ".join(
                        f"{service.name}" + (f" — {service.description}" if service.description else "")
                        for service in services
                    )
                    + "."
                )
                item = {
                    "content": content,
                    "source_id": source.id,
                    "source_name": source.name,
                    "source_url": source.url,
                    "document_title": unit.name,
                    "source_updated_at": None,
                    "structured": True,
                    "score": 1.0,
                    "unit_id": unit.id,
                }
            else:
                item = self.structured.unit_evidence(unit)
                item["source_name"] = source.name
                item["source_url"] = source.url
                item["document_title"] = unit.name
                item["score"] = 1.0
                item["unit_id"] = unit.id
            evidence.append(item)
        return evidence

    async def _get_previous_intent(self, session_id: str) -> str | None:
        turns = _SESSIONS[session_id]
        return turns[-1].get("intent") if turns else None

    @staticmethod
    def clear_session(session_id: str) -> None:
        _SESSIONS.pop(session_id, None)

    async def process(self, session_id: str, message: str, context: ChatContext | None) -> ChatResponse:
        supplied_context = context.model_dump(exclude_none=True) if context else {}
        previous_context = self._session_context(session_id)
        merged_context = {**previous_context, **supplied_context}

        extracted_ra = self.scope.extract_ra(message)
        if extracted_ra and not supplied_context.get("ra"):
            merged_context["ra"] = extracted_ra

        previous_intent = await self._get_previous_intent(session_id)
        decision = self.scope.classify(message, previous_intent=previous_intent)

        if decision.scope == "out_of_scope":
            reply = (
                "Posso ajudar com informações sobre serviços e acesso ao SUS no Distrito Federal, "
                "mas não realizo diagnóstico, prescrição ou orientação clínica personalizada."
            )
            self._save_turn(session_id, message, reply, merged_context)
            return ChatResponse(
                session_id=session_id,
                reply=reply,
                status=ChatStatus.OUT_OF_SCOPE,
                intent=decision.intent,
            )

        if decision.scope == "needs_clarification":
            reply = (
                "Posso ajudar com informações do SUS no Distrito Federal. "
                "Informe o serviço, unidade ou situação que você deseja consultar."
            )
            self._save_turn(session_id, message, reply, merged_context)
            return ChatResponse(
                session_id=session_id,
                reply=reply,
                status=ChatStatus.NEEDS_CLARIFICATION,
                intent=decision.intent,
                clarification=Clarification(
                    field="question",
                    question="Qual serviço ou informação do SUS-DF você procura?",
                ),
            )

        evidence: list[dict] = []
        try:
            evidence.extend(await self._structured_evidence(decision, merged_context, message))
            # RAG participa sempre que a intenção puder exigir explicação textual.
            if decision.intent not in {"unit_search"} or not evidence:
                evidence.extend(await self.retrieval.search(message))
        except Exception:
            logger.exception("Falha na consulta para a sessão %s", session_id)
            return ChatResponse(
                session_id=session_id,
                reply="Não consegui consultar a base de informações neste momento.",
                status=ChatStatus.ERROR,
                intent=decision.intent,
            )

        # Duplicatas por conteúdo + origem não ajudam o modelo e poluem as evidências.
        unique: dict[tuple[str, str], dict] = {}
        for item in evidence:
            key = (item["content"], str(item.get("source_id")))
            unique[key] = item
        evidence = list(unique.values())

        if not evidence:
            reply = "Não encontrei evidências suficientes nas fontes disponíveis para responder com segurança."
            self._save_turn(session_id, message, reply, merged_context)
            return ChatResponse(
                session_id=session_id,
                reply=reply,
                status=ChatStatus.NO_EVIDENCE,
                intent=decision.intent,
            )

        previous_turns = _SESSIONS[session_id][-4:]
        previous_text = "\n\n".join(
            f"Usuário: {turn['user']}\nAssistente: {turn['assistant']}" for turn in previous_turns
        )
        prompt = build_prompt(
            message,
            ChatContext(**{k: v for k, v in merged_context.items() if k in {"ra", "cep"}}),
            evidence,
            previous_text,
        )

        try:
            reply = await self.llm.generate(prompt)
        except Exception:
            logger.exception("Falha no LLM para a sessão %s", session_id)
            return ChatResponse(
                session_id=session_id,
                reply="Não consegui gerar a resposta neste momento.",
                status=ChatStatus.ERROR,
                intent=decision.intent,
            )

        self._save_turn(session_id, message, reply, {**merged_context})
        _SESSIONS[session_id][-1]["intent"] = decision.intent

        source_map: dict[str, SourceReference] = {}
        evidence_refs: list[EvidenceReference] = []
        for item in evidence:
            source_id = item.get("source_id")
            if not source_id or not item.get("source_name") or not item.get("source_url"):
                continue
            source_key = str(source_id)
            source = source_map.setdefault(
                source_key,
                SourceReference(
                    id=source_id,
                    title=item["document_title"],
                    source=item["source_name"],
                    url=item["source_url"],
                    updated_at=(
                        item["source_updated_at"].isoformat()
                        if item.get("source_updated_at")
                        else None
                    ),
                ),
            )
            evidence_refs.append(
                EvidenceReference(
                    content=item["content"],
                    score=round(float(item.get("score", 1.0)), 4),
                    source=source,
                    chunk_id=item.get("chunk_id"),
                    unit_id=item.get("unit_id"),
                )
            )

        return ChatResponse(
            session_id=session_id,
            reply=reply,
            status=ChatStatus.ANSWERED,
            intent=decision.intent,
            sources=list(source_map.values()),
            evidence=evidence_refs,
        )
