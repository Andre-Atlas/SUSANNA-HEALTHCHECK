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
    r"\b(horário|endereço|localização|telefone|funciona(mento)?|agenda(mento|r)?|"
    r"marcar (consulta|exame)|onde (fica|é|tem|posso)|lista de (espera|medicamentos)|"
    r"retirar (medicamento|remédio)|farmácia (do sus|popular|básica)|cartão (do sus|nacional)|"
    r"calendário (de vacinação|vacinal)|campanha de vacinação|vacina(s|ção)?|vacinar|"
    r"imunização|samu|192|postinho(s)?|posto(s)?|ubs|upa|verifique|mostre|exiba|listar|"
    r"opç(ão|ões)|primeir[oa]|segund[oa]|terceir[oa]|"
    r"como (chegar|marcar|agendar|retirar|funciona|fazer)|"
    r"quais (documentos|ubs|postos|horários|vacinas|serviços))\b|^[0-9]{1,2}$",
    re.I,
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
        clean = message.strip()
        if not clean:
            return False

        # 1. Mensagens ultra-curtas de navegação ("1", "2", "sim", "não", "ok") nunca são clínicas
        if clean.isdigit() or clean.lower() in {"sim", "nao", "não", "ok", "certo", "concordo", "mostre", "verifique", "ajuda"}:
            return False

        # 2. Perguntas sobre vacinas do calendário público e imunização são administrativas do SUS
        is_vaccine_query = bool(re.search(r"\b(vacina|vacinas|vacina[cç][aã]o|vacinar|gotinha|imuniza[cç][aã]o)\b", clean, re.I))

        # 3. Checagem estrita de padrões clínicos explícitos (sintomas, prescrição médica, diagnóstico)
        for name, pattern in CLINICAL_PATTERNS:
            if name == "prescricao" and is_vaccine_query:
                # Perguntas sobre tomar vacinas do calendário público não configuram prescrição de remédios
                continue
            if pattern.search(clean):
                logger.info("BLOCKED by clinical regex pattern (%s): %s", name, clean[:80])
                return True

        # 3. Override administrativo específico (endereços, horários, agendamento de consulta administrativa)
        if ADMINISTRATIVE_OVERRIDES.search(clean):
            logger.debug("ALLOWED by admin override: %s", clean[:80])
            return False

        # 3. Se ML carregado, usar com limiar calibrado (0.60 para evitar falsos positivos de OOV que pontuam ~0.507)
        if self.ml_model is not None:
            try:
                # O pipeline prediz 1 (CLINICAL) ou 0 (ADMIN)
                # O proba no index 1 é a chance de ser CLINICAL
                probs = self.ml_model.predict_proba([clean])[0]
                if probs[1] >= 0.60:
                    logger.info("BLOCKED by ML Classifier (p=%.2f): %s", probs[1], clean[:80])
                    return True
            except Exception as e:
                logger.error("Erro na predição ML (usando regex): %s", e)

        # 4. Camada 2 (Defesa em profundidade): Verificação Regex
        for rule_name, pattern in CLINICAL_PATTERNS:
            if pattern.search(clean):
                logger.info("BLOCKED by Regex rule '%s': %s", rule_name, clean[:80])
                return True

        return False
