"""
Guardrails — Classificador de intenção clínica pré-LLM
========================================================
Bloqueia perguntas de diagnóstico, prescrição e avaliação clínica.

Decisão híbrida (regras + ML somam proteção, nunca se substituem):
  1. Regra clínica FORTE (prescrição, dose, diagnóstico)   → bloqueia
  2. Termo administrativo (horário, endereço, agendar...)  → libera
  3. Regra clínica FRACA (relato de sintoma, tratamento)   → bloqueia
  4. Classificador ML (TF-IDF + LogReg via MLflow) p ≥ thr → bloqueia
  5. Caso contrário                                        → libera

A mesma função `decide` é usada em produção e na avaliação de `ml/guardrails/train.py`,
de modo que o gate de promoção mede exatamente o comportamento que vai ao ar.
"""
from __future__ import annotations

import logging
import re
import warnings
from dataclasses import dataclass
from typing import Optional

import mlflow
import mlflow.sklearn

from app.config import get_settings

logger = logging.getLogger("susana.guardrails")

# ---------------------------------------------------------------------------
# Regras
# ---------------------------------------------------------------------------
# Fortes: pedem conduta clínica explícita. Bloqueiam mesmo com termo administrativo.
STRONG_CLINICAL_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("diagnostico", re.compile(r"\b(diagnosticar|diagnóstico|o que (eu )?tenho(?! que| de)|qual (é )?(a )?minha doença|que doença (eu )?tenho)\b", re.I)),
    ("prescricao", re.compile(
        r"\b(que (remédio|medicamento|antibiótico) (eu )?(devo |posso |preciso )?(tomar|usar|dar|comprar)"
        r"|me (receite|receita|prescreva)|me (indique|recomende) (um |uma |algum |alguma )?(remédio|medicamento|antibiótico|tratamento)"
        r"|(posso|devo|preciso) (tomar|usar|dar)(?! (a |as |o |os )?(vacina|dose))"
        r"|(remédio|medicamento|antibiótico)s? (que |para )?(cura|curar|trata|tratar)"
        r"|sem receita)\b", re.I)),
    ("dosagem", re.compile(r"\b(quantos? (mg|ml|miligramas|comprimidos?|gotas)|dose (de|do|da) (?!vacina|reforço)|dosagem|posologia)\b", re.I)),
]

# Fracas: relatos de sintoma/tratamento. Cedem a um termo administrativo explícito.
WEAK_CLINICAL_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("sintomas", re.compile(r"\b(estou (sentindo|com)|sinto (muita |uma )?(dor|febre|tontura|enjoo|mal)|meu filho (está|tá) (com|doente)|sintomas? de)\b", re.I)),
    ("tratamento", re.compile(r"\b(como (tratar|curar|combater)|tratamento (para|de|do|da)|(é |está )?(grave|perigoso))\b", re.I)),
]

# Mantido por compatibilidade com código/testes que importam o nome antigo.
CLINICAL_PATTERNS = STRONG_CLINICAL_PATTERNS + WEAK_CLINICAL_PATTERNS

ADMINISTRATIVE_OVERRIDES = re.compile(
    r"\b(horário|endereço|localização|telefone|funciona(mento)?|agenda(mento|r)?|marcar (um |uma )?(consulta|exame)|onde (fica|é|tem|posso)|lista de (espera|medicamentos)|retirar (medicamento|remédio)|farmácia (do sus|popular|básica)|cartão (do sus|nacional)|calendário (de vacinação|vacinal)|campanha de vacinação)\b", re.I
)


@dataclass(frozen=True)
class GuardrailDecision:
    blocked: bool
    reason: str  # ex.: "regex:prescricao", "admin_override", "ml:p=0.71", "allow"


def _first_match(patterns: list[tuple[str, re.Pattern]], text: str) -> Optional[str]:
    for name, pattern in patterns:
        if pattern.search(text):
            return name
    return None


def decide(text: str, p_clinical: Optional[float], threshold: float) -> GuardrailDecision:
    """Decisão pura (sem I/O). `p_clinical=None` = sem modelo ML disponível."""
    rule = _first_match(STRONG_CLINICAL_PATTERNS, text)
    if rule:
        return GuardrailDecision(True, f"regex:{rule}")
    if ADMINISTRATIVE_OVERRIDES.search(text):
        return GuardrailDecision(False, "admin_override")
    rule = _first_match(WEAK_CLINICAL_PATTERNS, text)
    if rule:
        return GuardrailDecision(True, f"regex:{rule}")
    if p_clinical is not None and p_clinical >= threshold:
        return GuardrailDecision(True, f"ml:p={p_clinical:.2f}")
    return GuardrailDecision(False, "allow")


class GuardrailsClassifier:
    """Classificador híbrido (regras + ML)."""

    def __init__(self):
        self.settings = get_settings()
        self.threshold = self.settings.guardrail_threshold
        self.ml_model = None
        self._load_ml_model()

    def _load_ml_model(self):
        if not self.settings.guardrail_enabled_ml:
            logger.info("Guardrail ML desabilitado por config. Usando só regras.")
            return

        # Ignorar warnings do MLflow/urllib3 para stdout mais limpo
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            mlflow.set_tracking_uri(self.settings.mlflow_tracking_uri)
            try:
                logger.info("Carregando modelo guardrail de %s", self.settings.guardrail_model_uri)
                self.ml_model = mlflow.sklearn.load_model(self.settings.guardrail_model_uri)
                logger.info("Modelo ML Guardrail carregado (limiar=%.2f).", self.threshold)
            except Exception as e:
                logger.warning("Falha ao carregar modelo ML (usando só regras): %s", e)

    def _p_clinical(self, message: str) -> Optional[float]:
        if self.ml_model is None:
            return None
        try:
            return float(self.ml_model.predict_proba([message])[0][1])
        except Exception as e:
            logger.error("Erro na predição ML (usando só regras): %s", e)
            return None

    def check(self, message: str) -> GuardrailDecision:
        decision = decide(message, self._p_clinical(message), self.threshold)
        if decision.blocked:
            logger.info("BLOCKED (%s): %s", decision.reason, message[:80])
        return decision

    def is_clinical(self, message: str) -> bool:
        return self.check(message).blocked
