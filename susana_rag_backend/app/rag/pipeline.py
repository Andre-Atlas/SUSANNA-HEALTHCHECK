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

EMERGENCY_NO_RESULT_MESSAGE = (
    "Se for uma emergência, ligue agora para o SAMU: 192 (gratuito), ou vá à UPA 24 horas ou ao pronto-socorro "
    "do hospital mais próximo. " + NO_RESULT_MESSAGE
)


def no_result_message(text: str) -> str:
    """Mensagem de ausência de resposta; em urgência, traz sempre o SAMU 192 antes de qualquer coisa."""
    from app.rag.normalizer import detect_urgency

    return EMERGENCY_NO_RESULT_MESSAGE if detect_urgency(text) else NO_RESULT_MESSAGE


class RAGPipeline:
    def __init__(
        self,
        llm: LLMPort,
        embedder: Embedder,
        retriever: ChromaRetriever,
        semantic_cache: Optional[SemanticCache] = None,
        similarity_threshold: float = 0.65,
        confident_threshold: float = 0.35,
        top_k: int = 3,
        mlflow_enabled: bool = True,
        online_search: Optional[Any] = None,
    ):
        self.llm = llm
        self.embedder = embedder
        self.retriever = retriever
        self.semantic_cache = semantic_cache
        self.similarity_threshold = similarity_threshold
        self.confident_threshold = confident_threshold
        self.top_k = top_k
        self.mlflow_enabled = mlflow_enabled
        self.online_search = online_search

    def query(self, message: str, history: Optional[Sequence[Any]] = None) -> Dict[str, object]:
        """
        Executa a busca RAG:
        1. Inferência de NLU (Intenção, Região Administrativa, Persona, Filtro e Expansão)
        2. Cache Semântico
        3. Busca Vetorial Filtrada com Fallback Hierárquico
        4. Geração via LLM (com fallback extrativo)
        5. Log no MLflow
        """
        t0 = time.perf_counter()

        from app.rag.nlu import NaturalLanguageInferencer

        # 1. Inferência de NLU
        nlu_res = NaturalLanguageInferencer.infer(message, history=history)
        effective_query = nlu_res.expanded_query

        from app.rag.normalizer import looks_off_topic

        if looks_off_topic(message):
            logger.info("OFF TOPIC: %s...", message[:60])
            return {
                "response": NO_RESULT_MESSAGE,
                "source": None,
                "citations": [],
                "nlu": {"ra": nlu_res.ra, "ra_display": nlu_res.ra_display, "intent": nlu_res.intent,
                        "persona": nlu_res.persona, "cluster": nlu_res.cluster},
            }

        # 2. Embed query
        vec = self.embedder.encode_queries([effective_query])[0]

        # 3. Cache Hit?
        if self.semantic_cache is not None:
            cached = self.semantic_cache.get(vec)
            if cached:
                logger.info("CACHE HIT: %s...", message[:60])
                res_dict = dict(cached)
                res_dict["cached"] = True
                res_dict["nlu"] = {
                    "ra": nlu_res.ra,
                    "ra_display": nlu_res.ra_display,
                    "intent": nlu_res.intent,
                    "persona": nlu_res.persona,
                    "cluster": nlu_res.cluster,
                }
                return res_dict

        # 4. Busca Vetorial Filtrada e Hierárquica (com segunda chance focada no tema oficial)
        from app.rag.retrieval_flow import search_best

        try:
            results = search_best(self.retriever, self.embedder, nlu_res, self.top_k, nlu_res.metadata_filter)
        except TypeError:
            results = self.retriever.search(vec, k=self.top_k, query_text=effective_query)

        def _check_relevant(chunks: Sequence[RetrievedChunk]) -> bool:
            return is_relevant(chunks, effective_query, self.similarity_threshold, self.confident_threshold) or is_relevant(chunks, message, self.similarity_threshold, self.confident_threshold)

        if not _check_relevant(results):
            # Fallback seguro para busca global sem filtro caso o filtro tenha restringido demais
            if nlu_res.metadata_filter:
                try:
                    fallback_results = search_best(self.retriever, self.embedder, nlu_res, self.top_k, None)
                except TypeError:
                    fallback_results = self.retriever.search(vec, k=self.top_k, query_text=effective_query)
                if _check_relevant(fallback_results):
                    results = fallback_results

        if not _check_relevant(results) and getattr(self, "online_search", None) is not None:
            try:
                import asyncio
                import concurrent.futures

                def _run_coro_safe(coro):
                    try:
                        loop = asyncio.get_running_loop()
                    except RuntimeError:
                        loop = None
                    if loop and loop.is_running():
                        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                            return pool.submit(asyncio.run, coro).result()
                    return asyncio.run(coro)

                online_chunks = _run_coro_safe(self.online_search.search_async(message))
                if online_chunks:
                    logger.info("Online Search complementou com %d chunks oficiais para '%s'", len(online_chunks), message[:60])
                    results = list(online_chunks)
            except Exception as ex:
                logger.warning("Falha na execução do online search: %s", ex)

        if not _check_relevant(results):
            logger.info("LOW RELEVANCE: (dist > %.2f) para: %s...", self.similarity_threshold, message[:60])
            out = {
                "response": no_result_message(message),
                "source": None,
                "citations": [],
                "nlu": {
                    "ra": nlu_res.ra,
                    "ra_display": nlu_res.ra_display,
                    "intent": nlu_res.intent,
                    "persona": nlu_res.persona,
                    "cluster": nlu_res.cluster,
                },
            }
            if self.semantic_cache is not None:
                self.semantic_cache.put(vec, out)
            return out

        best_source = results[0].source

        # 5. Geração LLM (Fallback Extrativo)
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
            "nlu": {
                "ra": nlu_res.ra,
                "ra_display": nlu_res.ra_display,
                "intent": nlu_res.intent,
                "persona": nlu_res.persona,
                "cluster": nlu_res.cluster,
            },
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
