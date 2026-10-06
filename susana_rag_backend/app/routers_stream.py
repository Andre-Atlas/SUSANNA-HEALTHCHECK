import json
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

import app.main  # Import the module to get the updated global

logger = logging.getLogger("susana.stream")
router = APIRouter()

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)

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

    # 2. RAG
    # We will embed and search manually to yield stream from LLMPort
    vec = pipeline.embedder.encode_queries([msg])[0]
    results = pipeline.retriever.search(vec, k=3)

    if not results or results[0].distance > pipeline.similarity_threshold:
        def no_result_gen():
            yield json.dumps({"type": "chunk", "content": "Não encontrei informação suficiente nas fontes oficiais."}) + "\n"
            yield json.dumps({"type": "done", "source": None, "is_blocked": False}) + "\n"
        return StreamingResponse(no_result_gen(), media_type="application/x-ndjson")

    best_source = results[0].source

    def llm_gen():
        try:
            for piece in pipeline.llm.stream(msg, results):
                yield json.dumps({"type": "chunk", "content": piece}) + "\n"
            yield json.dumps({"type": "done", "source": best_source, "is_blocked": False}) + "\n"
        except Exception as e:
            logger.error("Error streaming LLM: %s", e)
            yield json.dumps({"type": "chunk", "content": f"\n\n[Fallback Extrativo]:\n{results[0].text}"}) + "\n"
            yield json.dumps({"type": "done", "source": best_source, "error": True}) + "\n"

    return StreamingResponse(llm_gen(), media_type="application/x-ndjson")
