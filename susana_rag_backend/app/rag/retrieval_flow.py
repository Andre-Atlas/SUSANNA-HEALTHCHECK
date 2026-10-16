"""Busca com segunda chance focada: quando o vocabulário popular aciona um tema oficial específico
(mordedura, SAMU, ouvidoria...), a consulta completa pode ser diluída pelo resto da frase
("o cachorro do vizinho mordeu minha perna, qual hospital?"). Também buscamos só os termos oficiais
e ficamos com o conjunto mais próximo."""
from __future__ import annotations

from typing import Any, Optional, Sequence

from app.rag.normalizer import context_expansions


def focus_query(nlu_res: Any) -> Optional[str]:
    terms = context_expansions(nlu_res.original_query)
    if not terms:
        return None
    ra = f"{nlu_res.ra_display} DF " if getattr(nlu_res, "ra", "geral_df") != "geral_df" else ""
    return (ra + " ".join(terms)).strip()


def search_best(retriever: Any, embedder: Any, nlu_res: Any, k: int, where_filter: Optional[dict]) -> Sequence[Any]:
    """Resultados da consulta completa; se houver tema específico, usa a consulta focada quando ela chegar mais perto."""
    main_q = nlu_res.expanded_query
    results = retriever.search(embedder.encode_queries([main_q])[0], k=k, query_text=main_q, where_filter=where_filter)
    focus = focus_query(nlu_res)
    if focus:
        alt = retriever.search(embedder.encode_queries([focus])[0], k=k, query_text=focus, where_filter=where_filter)
        if alt and (not results or alt[0].distance < results[0].distance):
            return alt
    return results
