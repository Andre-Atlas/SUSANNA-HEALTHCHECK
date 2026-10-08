"""
RAG Pipeline — Orquestrador único do fluxo Susana.

As duas rotas HTTP (/api/chat e /api/chat/stream) usam este mesmo fluxo:
  1. Guardrail clínico
  2. Cache semântico
  3. Busca vetorial + limiar de relevância
  4. Geração via LLM (com fallback extrativo)
  5. Escolha da fonte (trecho citado pelo LLM)
  6. Log no MLflow (sem texto da pergunta, por padrão — LGPD)
"""
from __future__ import annotations

import hashlib
import logging
import re
import time
from typing import Dict, Iterator, Optional, Sequence

import mlflow

from app.ports import LLMPort, LLMUnavailable, RetrievedChunk
from app.rag.embeddings import Embedder
from app.rag.glossary import expand_acronyms
from app.rag.retriever import ChromaRetriever, SemanticCache

logger = logging.getLogger("susana.rag")

BLOCKED_MESSAGE = (
    "Desculpe, não posso ajudar com essa questão. "
    "A Susana fornece apenas informações administrativas e institucionais da SES-DF. "
    "Para orientações clínicas, procure uma Unidade Básica de Saúde (UBS) ou ligue para o SAMU 192."
)

NO_RESULT_MESSAGE = (
    "Não encontrei informação suficiente nas fontes oficiais disponíveis "
    "para responder a essa pergunta. Tente reformular ou pergunte sobre "
    "unidades de saúde, vacinação, ou serviços da SES-DF."
)

FALLBACK_NOTICE = (
    "⚠️ [Aviso: O gerador de texto está indisponível. "
    "Abaixo constam trechos diretos dos documentos oficiais.]\n\n"
)

_CITATION = re.compile(r"\[(\d+)\]")
# Frase de recusa exigida pela regra 2 do prompt (app/llm/prompts.py)
_LLM_REFUSAL = re.compile(r"não encontrei essa informação nas fontes oficiais", re.I)

Event = Dict[str, object]


def pick_source(text: str, results: Sequence[RetrievedChunk]) -> Optional[str]:
    """Fonte do trecho citado pelo LLM (último [n] válido); sem citação, usa o mais próximo.
    Se o LLM recusou ("Não encontrei essa informação..."), não há fonte a exibir."""
    if not results or _LLM_REFUSAL.search(text):
        return None
    for n in reversed(_CITATION.findall(text)):
        idx = int(n) - 1
        if 0 <= idx < len(results):
            return results[idx].source
    return results[0].source


class RAGPipeline:
    def __init__(
        self,
        llm: LLMPort,
        embedder: Embedder,
        retriever: ChromaRetriever,
        guardrails=None,
        semantic_cache: Optional[SemanticCache] = None,
        similarity_threshold: float = 0.70,
        top_k: int = 3,
        mlflow_enabled: bool = True,
        mlflow_log_query_text: bool = False,
    ):
        self.llm = llm
        self.embedder = embedder
        self.retriever = retriever
        self.guardrails = guardrails
        self.semantic_cache = semantic_cache
        self.similarity_threshold = similarity_threshold
        self.top_k = top_k
        self.mlflow_enabled = mlflow_enabled
        self.mlflow_log_query_text = mlflow_log_query_text

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------
    def query(self, message: str) -> Dict[str, object]:
        """Resposta completa (rota /api/chat)."""
        text, done = "", {}
        for ev in self.query_stream(message, stream_llm=False):
            if ev["type"] == "chunk":
                text += str(ev["content"])
            else:
                done = ev
        return {
            "response": text,
            "source": done.get("source"),
            "is_blocked": bool(done.get("is_blocked", False)),
            "cached": bool(done.get("cached", False)),
        }

    def query_stream(self, message: str, stream_llm: bool = True) -> Iterator[Event]:
        """Eventos {"type": "chunk", "content"} ... {"type": "done", ...} (rota /api/chat/stream)."""
        t0 = time.perf_counter()
        log: Dict[str, object] = {"outcome": "answered", "llm_used": False, "cached": False}

        # 1. Guardrail clínico
        if self.guardrails is not None:
            decision = self.guardrails.check(message)
            if decision.blocked:
                yield {"type": "chunk", "content": BLOCKED_MESSAGE}
                yield {"type": "done", "source": None, "is_blocked": True}
                self._log(message, t0, {**log, "outcome": "blocked", "guardrail_reason": decision.reason})
                return

        # 2. Cache semântico (o vetor usa a pergunta com siglas expandidas; o LLM recebe a original)
        vec = self.embedder.encode_queries([expand_acronyms(message)])[0]
        if self.semantic_cache is not None:
            cached = self.semantic_cache.get(vec)
            if cached:
                logger.info("CACHE HIT: %s...", message[:60])
                yield {"type": "chunk", "content": cached["response"]}
                yield {"type": "done", "source": cached["source"], "is_blocked": False, "cached": True}
                self._log(message, t0, {**log, "outcome": "cache_hit", "cached": True})
                return

        # 3. Busca vetorial + limiar
        results = self.retriever.search(vec, k=self.top_k)
        top_distance = results[0].distance if results else None
        if not results or results[0].distance > self.similarity_threshold:
            logger.info("LOW RELEVANCE (dist > %.2f): %s...", self.similarity_threshold, message[:60])
            yield {"type": "chunk", "content": NO_RESULT_MESSAGE}
            yield {"type": "done", "source": None, "is_blocked": False}
            self._cache_put(vec, NO_RESULT_MESSAGE, None)
            self._log(message, t0, {**log, "outcome": "no_result", "top_distance": top_distance})
            return

        # 4. Geração (com fallback extrativo)
        text, error = "", False
        t_llm = time.perf_counter()
        try:
            if stream_llm:
                for piece in self.llm.stream(message, results):
                    text += piece
                    yield {"type": "chunk", "content": piece}
            else:
                text = self.llm.generate(message, results).text
                yield {"type": "chunk", "content": text}
            log["llm_used"] = True
        except Exception as e:  # LLMUnavailable ou erro inesperado: o cidadão nunca fica sem resposta
            level = logging.WARNING if isinstance(e, LLMUnavailable) else logging.ERROR
            logger.log(level, "LLM falhou, ativando fallback extrativo. Motivo: %r", e)
            error = True
            fallback = ("\n\n" if text else "") + FALLBACK_NOTICE + "\n\n".join(r.text for r in results)
            text += fallback
            yield {"type": "chunk", "content": fallback}
        llm_ms = int((time.perf_counter() - t_llm) * 1000)

        # 5. Fonte citada
        source = pick_source(text, results)
        done: Event = {"type": "done", "source": source, "is_blocked": False}
        if error:
            done["error"] = True
        yield done

        # Fallback não vai para o cache: na próxima vez o LLM pode estar de volta
        if not error:
            self._cache_put(vec, text, source)
        self._log(message, t0, {**log, "outcome": "fallback" if error else "answered",
                                "top_distance": top_distance, "llm_latency_ms": llm_ms, "source": source})

    # ------------------------------------------------------------------
    def _cache_put(self, vec, response: str, source: Optional[str]) -> None:
        if self.semantic_cache is not None:
            self.semantic_cache.put(vec, {"response": response, "source": source})

    def _log(self, message: str, t0: float, data: Dict[str, object]) -> None:
        if not self.mlflow_enabled:
            return
        params = {
            "outcome": data["outcome"],
            "llm_used": data["llm_used"],
            "cached": data["cached"],
            "query_sha256": hashlib.sha256(message.encode("utf-8")).hexdigest()[:16],
            "query_chars": len(message),
        }
        if self.mlflow_log_query_text:
            params["query"] = message[:200]
        for key in ("guardrail_reason", "source"):
            if data.get(key):
                params[key] = str(data[key])[:250]
        metrics = {"latency_s": time.perf_counter() - t0}
        for key in ("top_distance", "llm_latency_ms"):
            if data.get(key) is not None:
                metrics[key] = float(data[key])
        try:
            with mlflow.start_run(run_name="query", nested=True):
                mlflow.log_params(params)
                mlflow.log_metrics(metrics)
        except Exception as e:
            logger.debug("Falha ao logar no MLflow: %s", e)
