"""
Guardrails — Classificador de intenção clínica pré-LLM
========================================================
Bloqueia perguntas de diagnóstico, prescrição e avaliação clínica.
Usa um classificador Scikit-Learn treinado e carregado via MLflow.
Caso falhe o carregamento, cai para o fallback de Regex.
"""
from __future__ import annotations

import logging
import re
import warnings

import mlflow
import mlflow.sklearn

from app.config import get_settings

logger = logging.getLogger("susana.guardrails")

# ---------------------------------------------------------------------------
# Fallback Regex (usado apenas se o MLflow falhar ou estiver desabilitado)
# ---------------------------------------------------------------------------
CLINICAL_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("diagnostico", re.compile(r"\b(diagnosticar|diagnóstico|o que (eu )?tenho|qual (minha )?doença)\b", re.I)),
    ("prescricao", re.compile(r"\b(que (remédio|medicamento) (devo |posso )?(tomar|usar)|me (receite|prescreva|indique)|posso tomar|devo tomar|preciso tomar)\b", re.I)),
    ("sintomas", re.compile(r"\b(estou (sentindo|com)|sinto (muita |uma )?(dor|febre|tontura|enjoo|mal)|meu filho (está|tá) (com|doente)|sintomas? de)\b", re.I)),
    ("tratamento", re.compile(r"\b(como (tratar|curar|combater|prevenir)|tratamento (para|de|do|da)|(é |está )?(grave|perigoso|contagioso))\b", re.I)),
    ("dosagem", re.compile(r"\b(quantos? (mg|ml|comprimidos?|gotas)|dose (de|do|da)|dosagem|posologia)\b", re.I)),
]

ADMINISTRATIVE_OVERRIDES = re.compile(
    r"\b(horário|endereço|localização|telefone|funciona(mento)?|agenda(mento|r)?|marcar (consulta|exame)|onde (fica|é|tem|posso)|lista de (espera|medicamentos)|retirar (medicamento|remédio)|farmácia (do sus|popular|básica)|cartão (do sus|nacional)|calendário (de vacinação|vacinal)|campanha de vacinação)\b", re.I
)


class GuardrailsClassifier:
    """Classificador híbrido (ML + Regex fallback)."""

    def __init__(self):
        self.settings = get_settings()
        self.ml_model = None
        self._load_ml_model()

    def _load_ml_model(self):
        if not self.settings.guardrail_enabled_ml:
            logger.info("Guardrail ML desabilitado por config. Usando Regex.")
            return

        # Ignorar warnings do MLflow/urllib3 para stdout mais limpo
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            mlflow.set_tracking_uri(self.settings.mlflow_tracking_uri)
            try:
                logger.info("Carregando modelo guardrail de %s", self.settings.guardrail_model_uri)
                self.ml_model = mlflow.sklearn.load_model(self.settings.guardrail_model_uri)
                logger.info("Modelo ML Guardrail carregado com sucesso via MLflow.")
            except Exception as e:
                # Fallback: tentar carregar diretamente de arquivo .pkl local
                import joblib
                pkl_fallback = self.settings.docs_dir.parent / "guardrail_model.pkl"
                if pkl_fallback.exists():
                    try:
                        self.ml_model = joblib.load(pkl_fallback)
                        logger.info("Modelo ML Guardrail carregado com sucesso do arquivo .pkl local: %s", pkl_fallback)
                        return
                    except Exception as pkl_err:
                        logger.warning("Falha ao carregar .pkl local: %s", pkl_err)
                logger.warning("Falha ao carregar modelo ML (caindo para Regex): %s", e)

    def is_clinical(self, message: str) -> bool:
        """
        Retorna True se for clínica, False se administrativa.
        """
        # Override administrativo tem prioridade absoluta em ambas abordagens
        if ADMINISTRATIVE_OVERRIDES.search(message):
            logger.debug("ALLOWED by admin override: %s", message[:80])
            return False

        # Se ML carregado, usar
        if self.ml_model is not None:
            try:
                # O pipeline prediz 1 (CLINICAL) ou 0 (ADMIN)
                # O proba no index 1 é a chance de ser CLINICAL
                probs = self.ml_model.predict_proba([message])[0]
                if probs[1] >= 0.50:
                    logger.info("BLOCKED by ML Classifier (p=%.2f): %s", probs[1], message[:80])
                    return True
            except Exception as e:
                logger.error("Erro na predição ML (usando regex): %s", e)

        # Camada 2 (Defesa em profundidade): Verificação Regex
        for rule_name, pattern in CLINICAL_PATTERNS:
            if pattern.search(message):
                logger.info("BLOCKED by Regex rule '%s': %s", rule_name, message[:80])
                return True

        return False
