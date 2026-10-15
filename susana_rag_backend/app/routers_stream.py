import json
import logging
from typing import Optional, List, Sequence, Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

import app.main  # Import the module to get the updated global
from app.ports import RetrievedChunk
from app.rag.retriever import is_relevant
from app.agenda.intent import detect_scheduling_intent, extract_event
from app.agenda.storage import AgendaStorage, ProposalError, get_agenda_storage
from app.citizen.auth import get_current_citizen_optional
from app.citizen.schemas import DEFAULT_RA, CitizenProfileResponse

logger = logging.getLogger("susana.stream")
router = APIRouter()

class ChatMessageItem(BaseModel):
    text: Optional[str] = None
    content: Optional[str] = None
    isUser: Optional[bool] = None
    role: Optional[str] = None

    def get_text(self) -> str:
        return self.text or self.content or ""

    def is_user(self) -> bool:
        if self.isUser is not None:
            return self.isUser
        if self.role is not None:
            return self.role.lower() in ("user", "human", "citizen")
        return True

class ChatRequest(BaseModel):
    message: Optional[str] = None
    question: Optional[str] = None
    history: List[ChatMessageItem] = []
    # Proposta de agenda aguardando dados (ex.: o chat perguntou o horário)
    pending_proposal_id: Optional[str] = None


def _ndjson(*events: dict) -> StreamingResponse:
    def gen():
        for ev in events:
            yield json.dumps(ev, ensure_ascii=False) + "\n"
    return StreamingResponse(gen(), media_type="application/x-ndjson")


def _scheduling_response(
    msg: str,
    req: ChatRequest,
    citizen: Optional[CitizenProfileResponse],
    agenda: AgendaStorage,
) -> Optional[StreamingResponse]:
    """Responde pedidos de agendamento/lembrete com uma proposta a confirmar."""
    base = None
    if req.pending_proposal_id and citizen is not None:
        try:
            base = agenda.get_proposal(citizen.id, req.pending_proposal_id)
        except ProposalError:
            base = None
    if base is None and not detect_scheduling_intent(msg):
        return None
    if base is not None and not detect_scheduling_intent(msg):
        # Resposta curta a uma pergunta da proposta ("às 15h", "dia 22")
        from app.agenda.dateparse import parse_pt_datetime
        parsed = parse_pt_datetime(msg)
        if parsed.date is None and parsed.time is None:
            return None

    if citizen is None:
        return _ndjson(
            {"type": "chunk", "content": "Posso guardar esse lembrete na sua agenda! Para isso, entre ou crie uma conta — é rápido e opcional. Com ela também aviso sobre vacinas pendentes."},
            {"type": "done", "source": "Agenda SUSANNA", "citations": [], "is_blocked": False,
             "options": [{"label": "Entrar ou criar conta", "action": "open_auth"}]},
        )

    proposal = agenda.save_proposal(citizen.id, extract_event(msg, base=base))
    logger.info("Proposta de agenda criada (tipo=%s, faltando=%s)", proposal.tipo, proposal.faltando)
    return _ndjson(
        {"type": "chunk", "content": proposal.texto_confirmacao},
        {"type": "agenda_proposal", "proposal": proposal.model_dump()},
        {"type": "done", "source": "Agenda SUSANNA", "citations": [], "options": [], "is_blocked": False},
    )


@router.post("/api/chat/stream")
async def chat_stream_endpoint(
    req: ChatRequest,
    citizen: Optional[CitizenProfileResponse] = Depends(get_current_citizen_optional),
    agenda: AgendaStorage = Depends(get_agenda_storage),
):
    pipeline = app.main.pipeline
    guardrails = app.main.guardrails

    raw_msg = req.message or req.question or ""
    msg = raw_msg.strip()
    if not msg:
        raise HTTPException(status_code=422, detail="Mensagem não pode ser vazia.")

    # 1. Contextualização Conversacional Multi-Turn e Normalização Popular
    from app.rag.conversation import ConversationalContextManager, expand_popular_terms
    contextualized_msg = ConversationalContextManager.contextualize(msg, req.history)
    logger.info("Chat stream input: '%s' | Contextualized: '%s'", msg, contextualized_msg)

    # 2. Agenda: pedidos de lembrete/agendamento viram proposta a confirmar.
    # Avaliado antes do guardrail clínico: registrar "tomar o remédio às 8h" não é
    # orientação clínica, e o modelo de linguagem não participa dessa resposta.
    scheduling = _scheduling_response(msg, req, citizen, agenda)
    if scheduling is not None:
        return scheduling

    # 3. Guardrails (avaliado com contexto expandido)
    if guardrails.is_clinical(contextualized_msg):
        def clinical_block_gen():
            yield json.dumps({"type": "chunk", "content": "Desculpe, não posso ajudar com essa questão. A SUSANNA fornece apenas informações administrativas do SUS-DF. "}) + "\n"
            yield json.dumps({"type": "done", "is_blocked": True, "options": []}) + "\n"
        return StreamingResponse(clinical_block_gen(), media_type="application/x-ndjson")

    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline inicializando.")

    # 4. Intent Routing & Context
    from app.rag.intent import IntentRouter
    
    intent = IntentRouter.classify(msg, has_history=bool(req.history))
    
    if intent == "VAGUE_PROGRAM" and not req.history:
        def vague_program_gen():
            yield json.dumps({"type": "chunk", "content": "O SUS possui diversos programas (Dignidade Menstrual, Farmácia Popular, etc). Você está procurando informações sobre qual deles?"}) + "\n"
            options = [
                {"label": "💊 Farmácia Popular", "query": "como funciona a Farmácia Popular no DF?"},
                {"label": "🩸 Dignidade Menstrual", "query": "como retirar absorventes pelo SUS?"},
            ]
            yield json.dumps({"type": "done", "is_blocked": True, "options": options}) + "\n"
        return StreamingResponse(vague_program_gen(), media_type="application/x-ndjson")

    if intent == "GREETING_OR_TOO_SHORT" and not req.history:
        def greeting_gen():
            yield json.dumps({"type": "chunk", "content": "Olá! Sou a SUSANNA. Posso ajudar com informações sobre UBSs, UPAs, Vacinação, Medicamentos e outros serviços do SUS-DF. Como posso ajudar você hoje?"}) + "\n"
            options = [
                {"label": "📍 Encontrar UBS", "query": "onde encontrar uma UBS mais próxima?"},
                {"label": "💉 Vacinas disponíveis", "query": "quais vacinas estão disponíveis nas UBSs?"},
                {"label": "💊 Pegar medicamentos", "query": "como retirar remédios na farmácia da UBS?"},
            ]
            yield json.dumps({"type": "done", "is_blocked": True, "options": options}) + "\n"
        return StreamingResponse(greeting_gen(), media_type="application/x-ndjson")

    from app.rag.nlu import NaturalLanguageInferencer
    nlu_res = NaturalLanguageInferencer.infer(contextualized_msg, history=req.history)
    # RA do perfil como padrão quando a mensagem não cita a região
    if citizen is not None and nlu_res.ra == "geral_df" and citizen.ra_residencia != DEFAULT_RA:
        nlu_res.ra = citizen.ra_residencia
        nlu_res.ra_display = citizen.ra_display
        nlu_res.metadata_filter = {"$or": [{"ra": citizen.ra_residencia}, {"ra": "geral_df"}]}
    effective_search_query = nlu_res.expanded_query

    profile_block = None
    if citizen is not None:
        from app.agenda.router import pending_for
        from app.llm.profile_context import build_profile_block
        try:
            pending_names = [v.nome for v in pending_for(citizen, agenda)]
        except Exception:
            pending_names = []
        profile_block = build_profile_block(citizen, pending_names)

    if intent == "NEEDS_LOCATION" and nlu_res.ra == "geral_df" and not req.history:
        def location_gen():
            yield json.dumps({"type": "chunk", "content": "Posso ajudar a encontrar a unidade mais próxima! Por favor, me diga em qual Região Administrativa você está (ex: Ceilândia, Taguatinga, Samambaia, Asa Sul, Gama, Santa Maria, Sobradinho) para indicar o local exato."}) + "\n"
            options = [
                {"label": "📍 Ceilândia", "query": "quais as UBSs em Ceilândia?"},
                {"label": "📍 Taguatinga", "query": "quais as UBSs em Taguatinga?"},
                {"label": "📍 Samambaia", "query": "quais as UBSs em Samambaia?"},
                {"label": "📍 Asa Norte / Sul", "query": "quais as UBSs no Plano Piloto?"},
            ]
            yield json.dumps({"type": "done", "is_blocked": True, "options": options}) + "\n"
        return StreamingResponse(location_gen(), media_type="application/x-ndjson")

    def _retrieve_chunks():
        v = pipeline.embedder.encode_queries([effective_search_query])[0]
        chunks = pipeline.retriever.search(
            v,
            k=pipeline.top_k,
            query_text=effective_search_query,
            where_filter=nlu_res.metadata_filter,
        )
        def _check_relevant(res: Sequence[RetrievedChunk]) -> bool:
            return is_relevant(res, effective_search_query, pipeline.similarity_threshold, pipeline.confident_threshold) or is_relevant(res, contextualized_msg, pipeline.similarity_threshold, pipeline.confident_threshold)

        if not _check_relevant(chunks):
            if nlu_res.metadata_filter:
                fallback_chunks = pipeline.retriever.search(
                    v,
                    k=pipeline.top_k,
                    query_text=effective_search_query,
                    where_filter=None,
                )
                if _check_relevant(fallback_chunks):
                    chunks = fallback_chunks
        return chunks

    results = await run_in_threadpool(_retrieve_chunks)

    def _check_results_relevant(res: Sequence[RetrievedChunk]) -> bool:
        return is_relevant(res, effective_search_query, pipeline.similarity_threshold, pipeline.confident_threshold) or is_relevant(res, contextualized_msg, pipeline.similarity_threshold, pipeline.confident_threshold)

    if not results or not _check_results_relevant(results):
        online_search = getattr(pipeline, "online_search", None)
        if online_search is not None:
            try:
                online_chunks = await online_search.search_async(contextualized_msg)
                if online_chunks:
                    logger.info("Online search complementou stream com %d chunks para '%s'", len(online_chunks), contextualized_msg[:60])
                    results = online_chunks
            except Exception as ex:
                logger.debug("Falha na busca online durante streaming: %s", ex)

    if not results or not _check_results_relevant(results):
        from app.rag.pipeline import NO_RESULT_MESSAGE
        def no_result_stream_gen():
            yield json.dumps({"type": "chunk", "content": NO_RESULT_MESSAGE}) + "\n"
            yield json.dumps({"type": "done", "source": None, "citations": [], "options": [], "is_blocked": False}) + "\n"
        return StreamingResponse(no_result_stream_gen(), media_type="application/x-ndjson")

    best_source = results[0].source if results else None

    def llm_gen():
        llm_query = msg
        if req.history:
            history_text = "\n".join([("Cidadão: " if m.is_user() else "SUSANNA: ") + m.get_text() for m in req.history[-4:]])
            llm_query = f"HISTÓRICO RECENTE DA CONVERSA:\n{history_text}\n\nPERGUNTA ATUAL DO CIDADÃO: {msg}"
        if profile_block:
            llm_query = f"{profile_block}\n\n{llm_query}"
            
        try:
            full_response = ""
            for piece in pipeline.llm.stream(llm_query, results):
                full_response += piece
                yield json.dumps({"type": "chunk", "content": piece}) + "\n"
            
            # Citações limpas com URL oficial resolvida
            def _resolve_official_url(title: str, url: Optional[str]) -> str:
                if url and url.startswith("http"):
                    return url
                t = title.lower()
                if "vacina" in t:
                    return "https://www.gov.br/saude/pt-br/vacinacao/calendario"
                if "farmacia" in t or "medicamento" in t:
                    return "https://www.saude.df.gov.br/componente-especializado"
                if "ubs" in t or "unidade" in t or "hospital" in t:
                    return "https://www.saude.df.gov.br/unidades-de-saude"
                if "samu" in t or "emergencia" in t:
                    return "https://www.saude.df.gov.br/samu-192"
                if "dengue" in t or "vigilancia" in t:
                    return "https://www.saude.df.gov.br/dengue"
                return "https://www.saude.df.gov.br"

            citations = []
            for res in results[:3]:
                if res.source and res.source not in [c["title"] for c in citations]:
                    resolved_url = _resolve_official_url(res.source, res.url)
                    citations.append({"title": res.source, "url": resolved_url})
            
            # Chips de opções interativas dinâmicas
            options_chips = ConversationalContextManager.build_interactive_chips(
                current_query=contextualized_msg,
                response_text=full_response,
                retrieved_sources=[r.source for r in results],
            )

            primary_source = citations[0]["title"] if citations else (best_source or "Secretaria de Saúde do DF (SES-DF)")
            yield json.dumps({
                "type": "done",
                "source": primary_source,
                "citations": citations,
                "options": options_chips,
                "is_blocked": False,
            }) + "\n"
        except Exception as e:
            logger.error("Error streaming LLM: %s", e)
            fallback_text = f"\n\n[Informações oficiais recuperadas]:\n{results[0].text}" if results else "\n\nConsulte uma UBS próxima ou ligue 160."
            yield json.dumps({"type": "chunk", "content": fallback_text}) + "\n"
            yield json.dumps({"type": "done", "source": best_source, "error": True, "options": []}) + "\n"

    return StreamingResponse(llm_gen(), media_type="application/x-ndjson")
