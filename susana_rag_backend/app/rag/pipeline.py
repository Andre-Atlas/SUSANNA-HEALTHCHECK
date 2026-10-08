"""
RAG Pipeline — Orquestrador do fluxo Susana com LLM Local e Guardrail.
"""
from __future__ import annotations

import logging
import re
import time
from typing import Dict, Optional, Sequence

import mlflow

from app.ports import LLMPort, LLMUnavailable
from app.rag.embeddings import Embedder
from app.rag.retriever import ChromaRetriever, SemanticCache, is_relevant

logger = logging.getLogger("susana.rag")

NO_RESULT_MESSAGE = (
    "Não encontrei informação suficiente nas fontes oficiais disponíveis "
    "para responder a essa pergunta. Tente reformular ou pergunte sobre "
    "unidades de saúde, vacinação, ou serviços da SES-DF."
)


class RAGPipeline:
    def __init__(
        self,
        llm: LLMPort,
        embedder: Embedder,
        retriever: ChromaRetriever,
        semantic_cache: Optional[SemanticCache] = None,
        similarity_threshold: float = 0.55,
        top_k: int = 3,
        mlflow_enabled: bool = True,
    ):
        self.llm = llm
        self.embedder = embedder
        self.retriever = retriever
        self.semantic_cache = semantic_cache
        self.similarity_threshold = similarity_threshold
        self.top_k = top_k
        self.mlflow_enabled = mlflow_enabled

    def query(self, message: str) -> Dict[str, object]:
        """
        Executa a busca RAG:
        1. Cache Semântico
        2. Busca Vetorial
        3. Geração via LLM (com fallback extrativo)
        4. Log no MLflow
        """
        t0 = time.perf_counter()

        # 1. Embed query
        vec = self.embedder.encode_queries([message])[0]

        # 2. Cache Hit?
        if self.semantic_cache is not None:
            cached = self.semantic_cache.get(vec)
            if cached:
                logger.info("CACHE HIT: %s...", message[:60])
                return {
                    "response": cached["response"],
                    "source": cached["source"],
                    "citations": cached.get("citations", []),
                    "cached": True,
                }

        # 3. Busca Vetorial
        results = self.retriever.search(vec, k=self.top_k, query_text=message)

        if not is_relevant(results, message, self.similarity_threshold):
            logger.info("LOW RELEVANCE: (dist > %.2f) para: %s...", self.similarity_threshold, message[:60])
            out = {"response": NO_RESULT_MESSAGE, "source": None, "citations": []}
            if self.semantic_cache is not None:
                self.semantic_cache.put(vec, out)
            return out

        best_source = results[0].source

        # 4. Geração LLM (Fallback Extrativo)
        llm_used = False
        llm_latency = 0
        try:
            answer = self.llm.generate(message, results)
            response_text = answer.text
            llm_latency = answer.latency_ms
            llm_used = True
        except LLMUnavailable as e:
            logger.warning("LLM falhou, ativando fallback extrativo. Motivo: %s", e)
            # Fallback extrativo
            response_text = "⚠️ [Aviso: O gerador de texto está indisponível. Abaixo constam trechos diretos dos documentos.]\n\n"
            response_text += "\n\n".join(r.text for r in results)

        cited_refs = (
            {int(ref) for ref in re.findall(r"\[(\d+)\]", response_text) if 1 <= int(ref) <= len(results)}
            if llm_used
            else set(range(1, len(results) + 1))
        )
        citations = [
            {
                "ref": ref,
                "id": results[ref - 1].id,
                "title": results[ref - 1].source.removesuffix(
                    f" — {results[ref - 1].url}"
                ) if results[ref - 1].url else results[ref - 1].source,
                "url": results[ref - 1].url,
            }
            for ref in sorted(cited_refs)
        ]

        out = {
            "response": response_text,
            "source": best_source,
            "citations": citations,
            "cached": False,
        }

        # Armazenar no cache
        if self.semantic_cache is not None:
            self.semantic_cache.put(vec, out)

        # 5. MLflow
        if self.mlflow_enabled:
            latency = time.perf_counter() - t0
            try:
                with mlflow.start_run(run_name="query", nested=True):
                    mlflow.log_param("query", message[:200])
                    mlflow.log_metric("latency_s", latency)
                    mlflow.log_metric("llm_latency_ms", llm_latency)
                    mlflow.log_param("llm_used", llm_used)
                    mlflow.log_metric("top_distance", results[0].distance)
                    mlflow.log_param("source", best_source)
            except Exception as e:
                logger.debug("Falha ao logar no MLflow: %s", e)

        return out
