"""Ports (interfaces) do domínio Susana — ver openspec/changes/susana-local-llm-ml/contracts.md."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, List, Sequence

try:  # Python 3.9: Protocol existe em typing
    from typing import Protocol
except ImportError:  # pragma: no cover
    from typing_extensions import Protocol  # type: ignore


@dataclass(frozen=True)
class RetrievedChunk:
    id: str
    text: str
    source: str
    distance: float


@dataclass(frozen=True)
class LLMAnswer:
    text: str
    model: str
    latency_ms: int


class LLMUnavailable(RuntimeError):
    """LLM indisponível: conexão recusada, timeout ou resposta inválida."""


class LLMPort(Protocol):
    model_name: str

    def generate(self, question: str, contexts: Sequence[RetrievedChunk]) -> LLMAnswer:
        ...

    def stream(self, question: str, contexts: Sequence[RetrievedChunk]) -> Iterator[str]:
        ...

    def is_ready(self) -> bool:
        ...


class IntentClassifierPort(Protocol):
    version: str

    def predict_clinical_proba(self, texts: Sequence[str]) -> List[float]:
        ...
