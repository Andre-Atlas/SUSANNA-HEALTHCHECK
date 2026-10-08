"""Rota de streaming (NDJSON) — usada pelo frontend. A lógica fica toda em RAGPipeline.query_stream."""
import json
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

import app.main  # lê o `pipeline` global no momento da requisição (ele é criado no lifespan)

logger = logging.getLogger("susana.stream")
router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


@router.post("/api/chat/stream")
async def chat_stream_endpoint(req: ChatRequest):
    pipeline = app.main.pipeline
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline inicializando.")

    msg = req.message.strip()

    def events():
        try:
            for ev in pipeline.query_stream(msg):
                yield json.dumps(ev, ensure_ascii=False) + "\n"
        except Exception:
            logger.exception("Erro no streaming para query: %s", msg[:80])
            yield json.dumps({"type": "chunk", "content": "Erro interno ao processar sua pergunta. Tente novamente."}, ensure_ascii=False) + "\n"
            yield json.dumps({"type": "done", "source": None, "is_blocked": False, "error": True}) + "\n"

    return StreamingResponse(events(), media_type="application/x-ndjson")
