"""Retriever vetorial (ChromaDB, espaço cosseno) + cache semântico em memória."""
from __future__ import annotations

import logging
import re
import time
from collections import OrderedDict
from pathlib import Path
from typing import Any, List, Optional, Sequence, Tuple
import unicodedata

import numpy as np

from app.ports import RetrievedChunk
from app.rag.corpus import CorpusBlock
from app.rag.embeddings import Embedder, to_list

logger = logging.getLogger("susana.retriever")
_STOPWORDS = {
    "a", "as", "ao", "aos", "abre", "abrem", "aberta", "aberto", "ate", "como",
    "chamar", "da", "das", "de", "do", "dos", "e", "em", "endereco", "funcionamento",
    "fica", "horario", "horarios", "horas", "ligar", "na", "nas", "no", "nos", "numero",
    "o", "onde", "os", "para", "por", "qual", "que", "sabado", "sabados", "tem",
}


def _search_terms(text: str) -> set[str]:
    text = re.sub(r"\bregistros:\s*\d+\b", " ", text, flags=re.IGNORECASE)
    normalized = "".join(
        char
        for char in unicodedata.normalize("NFKD", text).casefold()
        if not unicodedata.combining(char)
    )
    return {
        term
        for term in re.findall(r"[a-z0-9]+", normalized)
        if (len(term) > 1 or term.isdigit()) and term not in _STOPWORDS
    }


def _numbered_entity(text: str) -> Optional[Tuple[str, str]]:
    normalized = "".join(
        char
        for char in unicodedata.normalize("NFKD", text).casefold()
        if not unicodedata.combining(char)
    )
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    match = re.search(r"\b(ubs|hospital)\s+(\d{1,3})\b", normalized)
    return (match.group(1), str(int(match.group(2)))) if match else None


def is_relevant(results: Sequence[RetrievedChunk], query_text: str, threshold: float) -> bool:
    if not results:
        return False
    if results[0].distance <= threshold:
        return True
    query_entity = _numbered_entity(query_text)
    if query_entity is None or query_entity != _numbered_entity(results[0].text):
        return False
    query_terms = _search_terms(query_text)
    return bool(query_terms) and query_terms <= _search_terms(results[0].text)


class ChromaRetriever:
    def __init__(self, embedder: Embedder, persist_dir: Path, collection_prefix: str = "sus_df"):
        import chromadb

        self.embedder = embedder
        self._client = chromadb.PersistentClient(path=str(persist_dir))
        # Coleção por modelo de embedding: evita misturar dimensões/espaços vetoriais
        self._collection = self._client.get_or_create_collection(
            name=f"{collection_prefix}_{embedder.slug}"[:63],
            metadata={"hnsw:space": "cosine"},
        )

    def count(self) -> int:
        return self._collection.count()

    def index(self, blocks: Sequence[CorpusBlock], batch_size: int = 256) -> int:
        if not blocks:
            return 0
        current_ids = {block.id for block in blocks}
        stored_ids = set(self._collection.get(include=[])["ids"])
        existing = stored_ids & current_ids
        new = [b for b in blocks if b.id not in existing]
        for i in range(0, len(new), batch_size):
            batch = new[i : i + batch_size]
            self._collection.add(
                ids=[b.id for b in batch],
                documents=[b.text for b in batch],
                embeddings=to_list(self.embedder.encode_passages([b.text for b in batch])),
                metadatas=[{"source": b.header, "tag": b.tag, "url": b.url or ""} for b in batch],
            )
        stale_ids = list(stored_ids - current_ids)
        for i in range(0, len(stale_ids), 5000):
            self._collection.delete(ids=stale_ids[i : i + 5000])
        logger.info("Indexação: %d novos / %d total", len(new), self.count())
        return len(new)

    def search(self, query_vec: np.ndarray, k: int = 3, query_text: str = "") -> List[RetrievedChunk]:
        collection_count = self.count()
        if collection_count == 0:
            return []
        candidate_count = min(max(k * 100, 300), collection_count)
        res = self._collection.query(
            query_embeddings=to_list(query_vec.reshape(1, -1)), n_results=candidate_count
        )
        query_terms = _search_terms(query_text)
        candidates: dict[str, Tuple[str, dict[str, Any], float]] = {
            cid: (doc, meta, float(dist))
            for cid, doc, meta, dist in zip(
                res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0]
            )
        }

        def add_document_matches(contains: str, entity: Optional[Tuple[str, str]] = None) -> None:
            matches = self._collection.get(
                where_document={"$contains": contains},
                include=["documents", "metadatas", "embeddings"],
            )
            for cid, doc, meta, embedding in zip(
                matches["ids"], matches["documents"], matches["metadatas"], matches["embeddings"]
            ):
                if entity and _numbered_entity(doc) != entity:
                    continue
                distance = 1.0 - float(np.dot(query_vec, np.asarray(embedding, dtype=np.float32)))
                candidates[cid] = (doc, meta, distance)

        numbered_entity = _numbered_entity(query_text)
        if numbered_entity:
            entity_type, entity_number = numbered_entity
            number = int(entity_number)
            number_variants = {entity_number, f"{number:02d}", f"{number:03d}"}
            for number_variant in number_variants:
                add_document_matches(f"{entity_type.upper()} {number_variant}", numbered_entity)

        rare_terms: dict[str, str] = {}
        for raw_term in re.findall(r"[^\W_]+", query_text, flags=re.UNICODE):
            terms = _search_terms(raw_term)
            if len(terms) == 1:
                normalized_term = next(iter(terms))
                if len(normalized_term) >= 6:
                    rare_terms.setdefault(normalized_term, raw_term)
        for normalized_term, raw_term in sorted(rare_terms.items())[:4]:
            variants = {raw_term.upper(), normalized_term.upper()}
            for variant in variants:
                add_document_matches(variant)

        ranked: List[Tuple[int, int, RetrievedChunk]] = []
        for cid, (doc, meta, dist) in candidates.items():
            source = meta.get("source", "Fonte desconhecida")
            if meta.get("url"):
                source = f"{source} — {meta['url']}"
            chunk = RetrievedChunk(
                id=cid,
                text=doc,
                source=source,
                distance=dist,
                url=meta.get("url") or None,
            )
            overlap = len(query_terms & _search_terms(doc))
            entity_match = int(numbered_entity is not None and _numbered_entity(doc) == numbered_entity)
            ranked.append((overlap, entity_match, chunk))
        ranked.sort(key=lambda item: (-item[0], -item[1], item[2].distance))
        return [chunk for _, _, chunk in ranked[:k]]


class SemanticCache:
    """Cache por similaridade de pergunta (cosseno). Placeholder para Redis Vector Search."""

    def __init__(self, max_distance: float = 0.06, max_size: int = 512, ttl_s: float = 3600.0):
        self.max_distance = max_distance
        self.max_size = max_size
        self.ttl_s = ttl_s
        self._items: "OrderedDict[int, Tuple[np.ndarray, Any, float]]" = OrderedDict()
        self._next = 0

    def get(self, vec: np.ndarray) -> Optional[Any]:
        now = time.time()
        best_key, best_dist = None, 2.0
        for key, (v, _, ts) in list(self._items.items()):
            if now - ts > self.ttl_s:
                del self._items[key]
                continue
            d = 1.0 - float(np.dot(v, vec))
            if d < best_dist:
                best_key, best_dist = key, d
        if best_key is not None and best_dist <= self.max_distance:
            self._items.move_to_end(best_key)
            return self._items[best_key][1]
        return None

    def put(self, vec: np.ndarray, value: Any) -> None:
        self._items[self._next] = (vec, value, time.time())
        self._next += 1
        while len(self._items) > self.max_size:
            self._items.popitem(last=False)

    def clear(self) -> None:
        self._items.clear()
