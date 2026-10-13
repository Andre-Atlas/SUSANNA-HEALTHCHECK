"""Retriever vetorial (ChromaDB, espaço cosseno) + cache semântico em memória."""
from __future__ import annotations

import logging
import re
import threading
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
    "segunda", "terca", "quarta", "quinta", "sexta", "domingo", "feira", "feiras",
    "meu", "minha", "meus", "minhas", "seu", "sua", "seus", "suas", "me", "te", "se",
    "dia", "dias", "mes", "meses", "ano", "anos", "prazo", "prazos", "via", "vias", "semana", "semanas",
}

_GENERIC_GEO_TERMS = {
    "brasilia", "df", "distrito", "federal", "taguatinga", "ceilandia", "samambaia",
    "plano", "piloto", "gama", "guara", "sobradinho", "planaltina", "paranoa",
    "brazlandia", "cruzeiro", "candangolandia", "riacho", "fundo", "santa", "maria",
    "sao", "sebastiao", "recanto", "emas", "lago", "sul", "norte", "aguas", "claras",
    "vicente", "pires", "estrutural", "fercal", "itapoa", "varjao", "park", "way",
    "scia", "sia", "sol", "nascente", "arniqueira", "jardim", "botanico", "centro",
    "setor", "quadra", "lote", "bloco", "avenida", "rua", "praca", "asa", "cidade",
}

_HEALTH_TERMS = {
    "saude", "sus", "ubs", "upa", "hospital", "hospitais", "policlinica", "policlinicas",
    "caps", "samu", "posto", "postinho", "farmacia", "farmacias", "medicamento", "medicamentos",
    "remedio", "remedios", "vacina", "vacinas", "vacinacao", "consulta", "consultas",
    "exame", "exames", "medico", "medica", "medicos", "enfermagem", "curativo", "curativos",
    "sutura", "suturas", "leite", "materno", "prenatal", "parto", "psiquiatria", "psicologia",
    "acolhimento", "cirurgia", "cirurgias", "regulacao", "ouvidoria", "lme", "cns", "cartao",
    "hiv", "sifilis", "dengue", "gripe", "febre", "amarela", "escorpiao", "cobra", "fitoterapico",
    "fitoterapicos", "acupuntura", "odontologia", "odonto", "clinica", "cnes", "ambulancia",
    "hemoderivados", "hemodialise", "paciente", "sangue", "maternidade", "alcool", "drogas",
    "residencia", "comprovante", "declaracao", "especialidades", "especializada", "ambulatorio",
    "vivas", "consultorio",
}


def _search_terms(text: str) -> set[str]:
    text = re.sub(r"\bregistros?:\s*\d+\b", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\(registro\s*\d+\)", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\bregistro\s+\d+\b", " ", text, flags=re.IGNORECASE)
    normalized = "".join(
        char
        for char in unicodedata.normalize("NFKD", text).casefold()
        if not unicodedata.combining(char)
    )
    terms = set()
    for term in re.findall(r"[a-z0-9]+", normalized):
        if term.isdigit():
            terms.add(str(int(term)))
        elif len(term) > 1:
            terms.add(term)
    return {term for term in terms if term not in _STOPWORDS}


def _expand_plurals(terms: set[str]) -> set[str]:
    """Expande termos para incluir formas singulares e plurais equivalentes."""
    expanded = set(terms)
    for t in terms:
        if t.endswith("ais") and len(t) > 4:
            expanded.add(t[:-3] + "al")
        elif t.endswith("al") and len(t) > 3:
            expanded.add(t[:-2] + "ais")
        elif t.endswith("s") and len(t) > 3:
            expanded.add(t[:-1])
        else:
            expanded.add(t + "s")
    return expanded


def _numbered_entity(text: str) -> Optional[Tuple[str, str]]:
    normalized = "".join(
        char
        for char in unicodedata.normalize("NFKD", text).casefold()
        if not unicodedata.combining(char)
    )
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    match = re.search(r"\b(ubs|hospital|upa|policlinica)\s+(\d{1,3})\b", normalized)
    return (match.group(1), str(int(match.group(2)))) if match else None


def is_relevant(
    results: Sequence[RetrievedChunk],
    query_text: str,
    threshold: float,
    confident_threshold: float = 0.35,
) -> bool:
    if not results:
        return False

    # 1. Distância ultra-confiante (mocks sintéticos em testes ou matches praticamente exatos)
    if results[0].distance <= confident_threshold:
        return True

    query_terms = _search_terms(query_text)
    doc_terms = _search_terms(results[0].text)
    overlap = query_terms & doc_terms
    substantive_query = query_terms - _GENERIC_GEO_TERMS
    substantive_overlap = overlap - _GENERIC_GEO_TERMS
    dist = results[0].distance

    # Se a pergunta tem termos substantivos, mas não há absolutamente nenhum overlap substantivo
    if substantive_query and not substantive_overlap:
        return False

    query_entity = _numbered_entity(query_text)
    doc_entity = _numbered_entity(results[0].text)
    if query_entity is not None and doc_entity is not None and query_entity == doc_entity:
        return True

    # Dentro do threshold de distância especificado
    if dist <= threshold:
        if substantive_overlap:
            if overlap & _HEALTH_TERMS:
                return True
            if len(substantive_overlap) >= 2:
                return True
            if len(substantive_query) <= 2:
                return True
        return False

    # Para distâncias ligeiramente maiores (0.65 a 0.82) em queries ricas do domínio da saúde
    if dist <= 0.82:
        if (overlap & _HEALTH_TERMS) and len(overlap) >= 3:
            return True

    return False


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

    @staticmethod
    def _serialize_metadata(b: CorpusBlock) -> dict[str, Any]:
        raw_meta = b.metadata or {}
        return {
            "source": b.header,
            "tag": b.tag,
            "url": b.url or "",
            "cluster": raw_meta.get("cluster", "geral"),
            "ra": raw_meta.get("ra", "geral_df"),
            "tipo_unidade": raw_meta.get("tipo_unidade", "unidade"),
            "servicos": raw_meta.get("servicos", ""),
        }

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
                metadatas=[self._serialize_metadata(b) for b in batch],
            )
        stale_ids = list(stored_ids - current_ids)
        for i in range(0, len(stale_ids), 5000):
            self._collection.delete(ids=stale_ids[i : i + 5000])
        logger.info("Indexação completa (bootstrap): %d novos / %d total", len(new), self.count())
        return len(new)

    def upsert(self, blocks: Sequence[CorpusBlock], batch_size: int = 256) -> int:
        """Adiciona ou atualiza blocos no ChromaDB sem remover os blocos pré-existentes do índice."""
        if not blocks:
            return 0
        new_or_updated = list(blocks)
        for i in range(0, len(new_or_updated), batch_size):
            batch = new_or_updated[i : i + batch_size]
            self._collection.upsert(
                ids=[b.id for b in batch],
                documents=[b.text for b in batch],
                embeddings=to_list(self.embedder.encode_passages([b.text for b in batch])),
                metadatas=[self._serialize_metadata(b) for b in batch],
            )
        logger.info("Upsert incremental: %d blocos adicionados/atualizados. Total no índice: %d", len(new_or_updated), self.count())
        return len(new_or_updated)

    def delete_by_url(self, url: str) -> int:
        """Remove blocos associados a uma URL específica (usado para substituir páginas atualizadas)."""
        if not url:
            return 0
        res = self._collection.get(where={"url": url}, include=[])
        ids_to_delete = res.get("ids", [])
        if ids_to_delete:
            self._collection.delete(ids=ids_to_delete)
            logger.info("Removidos %d blocos antigos para URL %s", len(ids_to_delete), url)
        return len(ids_to_delete)

    def search(
        self,
        query_vec: np.ndarray,
        k: int = 3,
        query_text: str = "",
        where_filter: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievedChunk]:
        collection_count = self.count()
        if collection_count == 0:
            return []

        candidates: dict[str, Tuple[str, dict[str, Any], float]] = {}

        # 1. Busca Filtrada por Metadados (ex: RA ou Cluster específico)
        if where_filter:
            try:
                filtered_limit = min(max(k * 10, 40), collection_count)
                f_res = self._collection.query(
                    query_embeddings=to_list(query_vec.reshape(1, -1)),
                    n_results=filtered_limit,
                    where=where_filter,
                )
                if f_res["ids"] and f_res["ids"][0]:
                    for cid, doc, meta, dist in zip(
                        f_res["ids"][0], f_res["documents"][0], f_res["metadatas"][0], f_res["distances"][0]
                    ):
                        candidates[cid] = (doc, meta, float(dist))
            except Exception as exc:
                logger.debug("Busca filtrada ignorada ou falhou (%s): %s", where_filter, exc)

        # 2. Busca Global (se não houver filtro ou se os resultados filtrados forem insuficientes)
        if not candidates or (len(candidates) < k and min((c[2] for c in candidates.values()), default=1.0) > 0.65):
            candidate_count = min(max(k * 100, 300), collection_count)
            res = self._collection.query(
                query_embeddings=to_list(query_vec.reshape(1, -1)), n_results=candidate_count
            )
            for cid, doc, meta, dist in zip(
                res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0]
            ):
                if cid not in candidates:
                    candidates[cid] = (doc, meta, float(dist))

        query_terms = _expand_plurals(_search_terms(query_text))

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
                if len(normalized_term) >= 5 and normalized_term not in _HEALTH_TERMS and normalized_term not in _GENERIC_GEO_TERMS:
                    rare_terms.setdefault(normalized_term, raw_term)
        for normalized_term, raw_term in sorted(rare_terms.items())[:3]:
            variants = {raw_term.upper(), normalized_term.upper()}
            for variant in variants:
                add_document_matches(variant)

        target_ra: Optional[str] = None
        if where_filter:
            if "ra" in where_filter and isinstance(where_filter["ra"], str) and where_filter["ra"] != "geral_df":
                target_ra = where_filter["ra"]
            elif "$or" in where_filter:
                for cond in where_filter["$or"]:
                    if isinstance(cond, dict) and "ra" in cond and cond["ra"] != "geral_df":
                        target_ra = cond["ra"]
                        break

        ranked: List[Tuple[int, int, int, int, RetrievedChunk]] = []
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
            doc_terms = _expand_plurals(_search_terms(doc))
            overlap = len(query_terms & doc_terms)
            entity_match = int(numbered_entity is not None and _numbered_entity(doc) == numbered_entity)
            header_terms = _expand_plurals(_search_terms(source))
            header_health_match = int(bool(query_terms & header_terms & (_HEALTH_TERMS | {"samu", "upa"})))
            ra_match = int(bool(target_ra and meta.get("ra") == target_ra))
            ranked.append((ra_match, entity_match, header_health_match, overlap, chunk))
        ranked.sort(key=lambda item: (-item[0], -item[1], -item[2], -item[3], item[4].distance))
        return [chunk for _, _, _, _, chunk in ranked[:k]]


class SemanticCache:
    """Cache por similaridade de pergunta (cosseno). Thread-safe."""

    def __init__(self, max_distance: float = 0.06, max_size: int = 512, ttl_s: float = 3600.0):
        self.max_distance = max_distance
        self.max_size = max_size
        self.ttl_s = ttl_s
        self._items: "OrderedDict[int, Tuple[np.ndarray, Any, float]]" = OrderedDict()
        self._next = 0
        self._lock = threading.RLock()

    def get(self, vec: np.ndarray) -> Optional[Any]:
        with self._lock:
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
        with self._lock:
            self._items[self._next] = (vec, value, time.time())
            self._next += 1
            while len(self._items) > self.max_size:
                self._items.popitem(last=False)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()

    def invalidate_negatives(self) -> int:
        """Invalida exclusivamente respostas negativas ('Não encontrei'), preservando consultas legítimas."""
        with self._lock:
            from app.rag.pipeline import NO_RESULT_MESSAGE
            to_del = []
            for k, (_, v, _) in self._items.items():
                if isinstance(v, dict) and v.get("response") == NO_RESULT_MESSAGE:
                    to_del.append(k)
            for k in to_del:
                del self._items[k]
            return len(to_del)

