"""Retriever vetorial (ChromaDB, espaço cosseno) + cache semântico em memória."""
from __future__ import annotations

import logging
import math
import re
import time
from collections import OrderedDict, defaultdict
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
    """Há evidência suficiente para chamar o LLM?

    - algum dos trechos está perto o bastante em significado (a busca intercalada pode pôr em 1º
      um trecho escolhido pelas palavras, com distância maior); ou
    - (develop_gui_sam) o 1º trecho é exatamente a unidade numerada pedida e contém todos os termos.
    """
    if not results:
        return False
    if min(r.distance for r in results) <= threshold:
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

    # ------------------------------------------------------------------
    # Estatísticas de termos para a parte textual da busca (calculadas sob demanda, em memória)
    # ------------------------------------------------------------------
    _RARE_DF_RATIO = 0.03   # termo em ≤3% dos blocos = "raro" (ex.: "dipirona", "192", "ceilandia")
    _MAX_POSTINGS = 60      # termos raros trazem até 60 blocos extras como candidatos

    def _term_stats(self) -> Tuple[int, dict]:
        if getattr(self, "_stats", None) is None:
            data = self._collection.get(include=["documents"])
            postings: dict[str, set] = defaultdict(set)
            for cid, doc in zip(data["ids"], data["documents"]):
                for term in _search_terms(doc):
                    postings[term].add(cid)
            self._stats = (len(data["ids"]), postings)
        return self._stats

    def _idf(self, term: str) -> float:
        n, postings = self._term_stats()
        return math.log((n + 1) / (len(postings.get(term, ())) + 1)) + 1.0

    def _rare_terms(self, terms: set) -> set:
        n, postings = self._term_stats()
        return {t for t in terms if 0 < len(postings.get(t, ())) <= max(1, self._RARE_DF_RATIO * n)}

    def count(self) -> int:
        return self._collection.count()

    def index(self, blocks: Sequence[CorpusBlock], batch_size: int = 256, prune: bool = True) -> int:
        """Sincroniza a coleção com `blocks`: adiciona os novos e, com `prune`, remove os que
        não existem mais no corpus (ids são hash do conteúdo; um bloco editado ganha id novo)."""
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
        stale_ids = list(stored_ids - current_ids) if prune else []
        if stale_ids:
            logger.info("Indexação: %d blocos removidos (não estão mais no corpus)", len(stale_ids))
        for i in range(0, len(stale_ids), 5000):
            self._collection.delete(ids=stale_ids[i : i + 5000])
        self._stats = None  # corpus mudou: recalcula IDF na próxima busca
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

        # Termos raros (poucos blocos os contêm): trazem como candidatos os blocos que os citam,
        # mesmo fora dos 300 mais próximos por vetor. Sem distinção de maiúsculas/acentos.
        rare = self._rare_terms(query_terms)
        if rare:
            _, postings = self._term_stats()
            extra = set()
            for term in sorted(rare, key=lambda t: len(postings[t])):
                extra |= postings[term]
            extra = [cid for cid in extra if cid not in candidates][: self._MAX_POSTINGS * max(1, len(rare))]
            if extra:
                got = self._collection.get(ids=extra, include=["documents", "metadatas", "embeddings"])
                for cid, doc, meta, embedding in zip(got["ids"], got["documents"], got["metadatas"], got["embeddings"]):
                    distance = 1.0 - float(np.dot(query_vec, np.asarray(embedding, dtype=np.float32)))
                    candidates[cid] = (doc, meta, distance)

        # Dois rankings sobre os mesmos candidatos:
        #  - por PALAVRAS (develop_gui_sam, com peso por raridade/IDF): entidade numerada exata,
        #    depois quem contém o termo mais raro da pergunta, depois cobertura ponderada, depois distância;
        #  - por SIGNIFICADO: distância do vetor, com a cobertura só como desempate.
        # Pergunta específica (unidade numerada ou termo raro): os k trechos INTERCALAM os dois rankings,
        # então o LLM sempre recebe o melhor de cada um. Pergunta geral: só o ranking por significado.
        _, postings = self._term_stats()
        weights = {t: self._idf(t) for t in query_terms}
        total = sum(weights.values()) or 1.0
        present = [t for t in query_terms if postings.get(t)]
        rarest = min(present, key=lambda t: len(postings[t])) if present else None
        specific = bool(numbered_entity) or bool(rare)

        chunks: dict[str, RetrievedChunk] = {}
        lexical_key: dict[str, tuple] = {}
        semantic_key: dict[str, tuple] = {}
        for cid, (doc, meta, dist) in candidates.items():
            source = meta.get("source", "Fonte desconhecida")
            if meta.get("url"):
                source = f"{source} — {meta['url']}"
            chunks[cid] = RetrievedChunk(id=cid, text=doc, source=source, distance=dist, url=meta.get("url") or None)
            doc_terms = _search_terms(doc)
            coverage = sum(weights[t] for t in query_terms & doc_terms) / total
            entity_match = int(numbered_entity is not None and _numbered_entity(doc) == numbered_entity)
            has_rarest = int(rarest is not None and rarest in doc_terms)
            lexical_key[cid] = (-entity_match, -has_rarest, -round(coverage, 1), dist)
            semantic_key[cid] = (-entity_match, dist - 0.1 * coverage)

        by_meaning = sorted(chunks, key=semantic_key.__getitem__)
        if not specific:
            return [chunks[cid] for cid in by_meaning[:k]]
        by_words = sorted(chunks, key=lexical_key.__getitem__)
        out: List[str] = []
        for pair in zip(by_words, by_meaning):
            for cid in pair:
                if cid not in out:
                    out.append(cid)
        return [chunks[cid] for cid in out[:k]]


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
