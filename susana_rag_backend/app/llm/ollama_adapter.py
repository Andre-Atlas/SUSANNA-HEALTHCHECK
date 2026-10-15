"""Adapter Ollama (LLM local) — implementa LLMPort."""
from __future__ import annotations

import json
import logging
import time
from typing import Iterator, Optional, Sequence

import httpx

from app.llm.prompts import build_messages
from app.ports import LLMAnswer, LLMUnavailable, RetrievedChunk

logger = logging.getLogger("susana.llm")


class OllamaAdapter:
    def __init__(
        self,
        base_url: str,
        model: str,
        timeout_s: float = 12.0,
        keep_alive: str = "30m",
        num_predict: int = 350,
        client: Optional[httpx.Client] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.model_name = model
        self.timeout_s = timeout_s
        self.keep_alive = keep_alive
        self.num_predict = num_predict
        self._client = client or httpx.Client(timeout=httpx.Timeout(timeout_s, connect=2.0))

    # ------------------------------------------------------------------
    def _payload(self, question: str, contexts: Sequence[RetrievedChunk], stream: bool) -> dict:
        return {
            "model": self.model_name,
            "messages": build_messages(question, contexts),
            "stream": stream,
            "keep_alive": self.keep_alive,
            "options": {"temperature": 0.1, "num_ctx": 4096, "num_predict": self.num_predict, "seed": 42},
        }

    def generate(self, question: str, contexts: Sequence[RetrievedChunk]) -> LLMAnswer:
        t0 = time.perf_counter()
        try:
            r = self._client.post(f"{self.base_url}/api/chat", json=self._payload(question, contexts, False))
            r.raise_for_status()
            text = r.json()["message"]["content"].strip()
        except (httpx.HTTPError, KeyError, ValueError, TypeError) as exc:
            logger.warning("Ollama indisponível (%s)", type(exc).__name__)
            raise LLMUnavailable(str(exc)) from exc
        if not text:
            raise LLMUnavailable("resposta vazia")
        return LLMAnswer(text=text, model=self.model_name, latency_ms=int((time.perf_counter() - t0) * 1000))

    def stream(self, question: str, contexts: Sequence[RetrievedChunk]) -> Iterator[str]:
        try:
            with self._client.stream(
                "POST", f"{self.base_url}/api/chat", json=self._payload(question, contexts, True)
            ) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if not line:
                        continue
                    data = json.loads(line)
                    piece = data.get("message", {}).get("content", "")
                    if piece:
                        yield piece
                    if data.get("done"):
                        break
        except (httpx.HTTPError, ValueError) as exc:
            raise LLMUnavailable(str(exc)) from exc

    def is_ready(self) -> bool:
        try:
            r = self._client.get(f"{self.base_url}/api/tags", timeout=2.0)
            r.raise_for_status()
            names = {m.get("name", "") for m in r.json().get("models", [])}
            return any(n == self.model_name or n.startswith(self.model_name + ":") for n in names)
        except (httpx.HTTPError, ValueError):
            return False

    def warm_up(self) -> bool:
        """Carrega o modelo na memória (evita cold start na 1ª pergunta)."""
        try:
            r = self._client.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model_name, "prompt": "", "keep_alive": self.keep_alive},
                timeout=60.0,
            )
            r.raise_for_status()
            logger.info("Ollama warm-up ok (%s)", self.model_name)
            return True
        except httpx.HTTPError as exc:
            logger.warning("Ollama warm-up falhou: %s", exc)
            return False
