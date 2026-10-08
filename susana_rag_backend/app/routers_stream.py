import json
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

import app.main  # Import the module to get the updated global
from app.rag.retriever import is_relevant

logger = logging.getLogger("susana.stream")
router = APIRouter()

class ChatMessageItem(BaseModel):
    text: str
    isUser: bool

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: list[ChatMessageItem] = []

@router.post("/api/chat/stream")
async def chat_stream_endpoint(req: ChatRequest):
    pipeline = app.main.pipeline
    guardrails = app.main.guardrails
    
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline inicializando.")

    msg = req.message.strip()

    # 1. Guardrails
    if guardrails.is_clinical(msg):
        def clinical_block_gen():
            yield json.dumps({"type": "chunk", "content": "Desculpe, não posso ajudar com essa questão. A Susana fornece apenas informações administrativas do SUS-DF. "}) + "\n"
            yield json.dumps({"type": "done", "is_blocked": True}) + "\n"
        return StreamingResponse(clinical_block_gen(), media_type="application/x-ndjson")

    # 2. Intent Routing & Context
    from app.rag.intent import IntentRouter
    
    intent = IntentRouter.classify(msg, has_history=bool(req.history))
    
    if intent == "VAGUE_PROGRAM":
        def vague_program_gen():
            yield json.dumps({"type": "chunk", "content": "O SUS possui diversos programas (Dignidade Menstrual, Farmácia Popular, etc). Você está procurando informações sobre qual deles?"}) + "\n"
            yield json.dumps({"type": "done", "is_blocked": True}) + "\n"
        return StreamingResponse(vague_program_gen(), media_type="application/x-ndjson")

    if intent == "GREETING_OR_TOO_SHORT":
        def greeting_gen():
            yield json.dumps({"type": "chunk", "content": "Olá! Posso ajudar com informações sobre UBS, UPAs, Vacinação e outros serviços do SUS-DF. O que você procura?"}) + "\n"
            yield json.dumps({"type": "done", "is_blocked": True}) + "\n"
        return StreamingResponse(greeting_gen(), media_type="application/x-ndjson")

    if intent == "NEEDS_LOCATION":
        def location_gen():
            yield json.dumps({"type": "chunk", "content": "Posso ajudar a encontrar uma unidade, mas não tenho acesso automático à sua localização. Por favor, me diga em qual Região Administrativa (ex: Taguatinga, Samambaia, Asa Sul) você está."}) + "\n"
            yield json.dumps({"type": "done", "is_blocked": True}) + "\n"
        return StreamingResponse(location_gen(), media_type="application/x-ndjson")

    search_query = msg
    if intent == "NEEDS_HISTORY":
        last_user_msg = next((m.text for m in reversed(req.history) if m.isUser), "")
        if last_user_msg:
            search_query = f"{last_user_msg} {msg}"

    vec = pipeline.embedder.encode_queries([search_query])[0]
    results = pipeline.retriever.search(vec, k=pipeline.top_k, query_text=search_query)

    # Permitimos que todas as queries cheguem ao LLM para que ele decida
    # se usa o contexto ou o conhecimento geral (Opção B).
    
    best_source = results[0].source if results else None

    def llm_gen():
        llm_query = msg
        if req.history:
            history_text = "\n".join([("Cidadão: " if m.isUser else "Susana: ") + m.text for m in req.history[-4:]])
            llm_query = f"HISTÓRICO RECENTE DA CONVERSA:\n{history_text}\n\nPERGUNTA ATUAL DO CIDADÃO: {msg}"
            
        try:
            full_response = ""
            for piece in pipeline.llm.stream(llm_query, results):
                full_response += piece
                yield json.dumps({"type": "chunk", "content": piece}) + "\n"
            
            citations = []
            for i, res in enumerate(results, start=1):
                if f"[{i}]" in full_response:
                    citations.append({"title": res.source, "url": res.url})
            
            primary_source = citations[0]["title"] if citations else None
            yield json.dumps({"type": "done", "source": primary_source, "citations": citations, "is_blocked": False}) + "\n"
        except Exception as e:
            logger.error("Error streaming LLM: %s", e)
            yield json.dumps({"type": "chunk", "content": f"\n\n[Fallback Extrativo]:\n{results[0].text}"}) + "\n"
            yield json.dumps({"type": "done", "source": best_source, "error": True}) + "\n"

    return StreamingResponse(llm_gen(), media_type="application/x-ndjson")
