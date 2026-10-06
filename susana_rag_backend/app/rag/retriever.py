"""Retriever vetorial (ChromaDB, espaço cosseno) + cache semântico em memória."""
from __future__ import annotations

import logging
import time
from collections import OrderedDict
from pathlib import Path
from typing import Any, List, Optional, Sequence, Tuple

import numpy as np

from app.ports import RetrievedChunk
from app.rag.corpus import CorpusBlock
from app.rag.embeddings import Embedder, to_list

logger = logging.getLogger("susana.retriever")


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

    def index(self, blocks: Sequence[CorpusBlock], batch_size: int = 64) -> int:
        if not blocks:
            return 0
        existing = set(self._collection.get(ids=[b.id for b in blocks])["ids"])
        new = [b for b in blocks if b.id not in existing]
        for i in range(0, len(new), batch_size):
            batch = new[i : i + batch_size]
            self._collection.add(
                ids=[b.id for b in batch],
                documents=[b.text for b in batch],
                embeddings=to_list(self.embedder.encode_passages([b.text for b in batch])),
                metadatas=[{"source": b.header, "tag": b.tag, "url": b.url or ""} for b in batch],
            )
        logger.info("Indexação: %d novos / %d total", len(new), self.count())
        return len(new)

    def search(self, query_vec: np.ndarray, k: int = 3) -> List[RetrievedChunk]:
        if self.count() == 0:
            return []
        res = self._collection.query(query_embeddings=to_list(query_vec.reshape(1, -1)), n_results=k)
        out: List[RetrievedChunk] = []
        for cid, doc, meta, dist in zip(
            res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0]
        ):
            source = meta.get("source", "Fonte desconhecida")
            if meta.get("url"):
                source = f"{source} — {meta['url']}"
            out.append(RetrievedChunk(id=cid, text=doc, source=source, distance=float(dist)))
        return out


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
