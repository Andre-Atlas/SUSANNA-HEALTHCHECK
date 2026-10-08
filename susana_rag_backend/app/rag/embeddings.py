"""Embeddings locais (sentence-transformers) com prefixos por família de modelo."""
from __future__ import annotations

import logging
from typing import List, Sequence

import numpy as np

logger = logging.getLogger("susana.embeddings")

# Modelos da família E5 exigem prefixos "query: " / "passage: "
_PREFIXES = {
    "e5": ("query: ", "passage: "),
}


def _family(model_name: str) -> str:
    return "e5" if "e5" in model_name.lower() else "default"


def _resolve(model_name: str) -> str:
    # Aceita nome curto ("paraphrase-multilingual-MiniLM-L12-v2") ou completo ("org/model")
    if "/" in model_name:
        return model_name
    return f"sentence-transformers/{model_name}"


class Embedder:
    def __init__(self, model_name: str, max_seq_length: int = 512):
        from sentence_transformers import SentenceTransformer  # import tardio (pesado)

        self.model_name = _resolve(model_name)
        self._model = SentenceTransformer(self.model_name)
        model_max_positions = self._model[0].auto_model.config.max_position_embeddings
        self._model.max_seq_length = min(max_seq_length, model_max_positions)
        self._q_prefix, self._p_prefix = _PREFIXES.get(_family(self.model_name), ("", ""))
        self.dim = int(self._model.get_embedding_dimension() or 0)
        logger.info("Embedder carregado: %s (dim=%d)", self.model_name, self.dim)

    def _encode(self, texts: Sequence[str]) -> np.ndarray:
        return np.asarray(
            self._model.encode(list(texts), normalize_embeddings=True, show_progress_bar=False),
            dtype=np.float32,
        )

    def encode_queries(self, texts: Sequence[str]) -> np.ndarray:
        return self._encode([self._q_prefix + t for t in texts])

    def encode_passages(self, texts: Sequence[str]) -> np.ndarray:
        return self._encode([self._p_prefix + t for t in texts])

    @property
    def slug(self) -> str:
        name = self.model_name.split("/")[-1].lower().replace(".", "-")
        return f"{name}-seq{self._model.max_seq_length}"


def to_list(vecs: np.ndarray) -> List[List[float]]:
    return vecs.astype(float).tolist()
