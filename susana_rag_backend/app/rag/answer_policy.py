"""Regras determinísticas sobre trechos e respostas (adaptadas de answer_policy.py da branch develop_gui).

- `has_injected_instructions`: um trecho do corpus que tenta dar ordens ao modelo ("ignore as regras",
  "aprove qualquer resposta", marcadores de papel como "<|system|>") é descartado ANTES de ir ao LLM.
  Fail-closed: na dúvida, o trecho não é usado.
- `generated_links`: a resposta do LLM não deve conter URLs/domínios — os links verdadeiros vêm das
  citações estruturadas montadas pelo backend. Um link escrito pelo modelo pode ser inventado.
"""
from __future__ import annotations

import re
import unicodedata
from typing import List

_INJECTION = (
    r"\b(?:ignore|desconsidere|esqueca|disregard|forget|override|deixe de lado|coloque de lado|suspenda)\b"
    r".{0,160}\b(?:regras|criterios|instrucoes|politicas|prompt|rules|criteria|instructions|policies|system prompt)\b",
    r"\b(?:nao|don't|do not)\b.{0,80}\b(?:siga|obedeca|obedece|follow|obey)\b.{0,80}"
    r"\b(?:do sistema|the system|system prompt|developer instructions|regras do sistema)\b",
    r"\b(?:revisor|reviewer|assistant|assistente|modelo|model|system|sistema)\b.{0,120}"
    r"\b(?:ignore|desconsidere|aprove|aprovar|aceite|approve)\b",
    r"\b(?:voce agora e|you are now|a partir de agora voce)\b",
    r"<\|(?:im_start|im_end|system|assistant)\|>",
)
_LINK = re.compile(r"(?i)\b(?:[a-z][a-z0-9+.-]*://|www\.)|\[[^\]]*\]\s*\(|\b(?:[a-z0-9-]+\.)+(?:br|com|org|gov|net)\b|cli(?:que|car|cando) aqui")


def _fold(text: str) -> str:
    text = unicodedata.normalize("NFKD", unicodedata.normalize("NFKC", text).casefold())
    return "".join(c for c in text if not unicodedata.combining(c) and unicodedata.category(c) != "Cf")


def has_injected_instructions(text: str) -> bool:
    t = _fold(text)
    return any(re.search(p, t, re.DOTALL) for p in _INJECTION)


def generated_links(answer: str) -> List[str]:
    """Trechos da resposta que parecem links/domínios escritos pelo próprio LLM."""
    return [m.group(0) for m in _LINK.finditer(answer or "")]
