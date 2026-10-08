"""Detecção de possível emergência (requisito RNF06 — docs/projeto/requisitos-susana.md).

"O sistema deve reconhecer sinais de possível urgência/emergência e, nesses casos, nunca substituir
orientação de emergência — direcionando sempre a canais oficiais apropriados."

Regra conservadora: exige um SINAL GRAVE ("dor no peito", "não consigo respirar", "desmaiou"...) E um
indício de que está acontecendo com alguém agora ("estou", "meu pai", "agora", "forte"...). Assim,
"O SAMU atende caso de dor no peito?" (pergunta administrativa) NÃO é tratada como emergência.
Roda antes do guardrail: a mensagem de emergência substitui a recusa clínica genérica.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Optional

SUICIDE = re.compile(
    r"\b(me matar|quero morrer|tirar (a )?minha (propria )?vida|suicid\w*|acabar com (a )?minha vida|"
    r"nao quero mais viver|me (cortar|machucar))\b")
SEVERE = re.compile(
    r"\b(dor (forte |muito forte )?no peito|aperto no peito|infart\w*|parada cardiaca|"
    r"falta de ar|nao (consigo|consegue) respirar|sem respirar|engasg\w*|sufoc\w*|"
    r"desmai\w*|inconsciente|nao acorda|desacordad\w*|convuls\w*|"
    r"avc|derrame|boca torta|perda de forca|"
    r"sangramento (forte|intenso|que nao para)|sangrando muito|hemorragia|"
    r"overdose|envenen\w*|intoxica\w*|tomou (muitos|varios) (remedios|comprimidos)|"
    r"picad\w* de (cobra|escorpiao)|mordid\w* de cobra|queimadura grave|"
    r"acidente grave|atropel\w*|baleado|esfaquead\w*)\b")
NOW_OR_PERSONAL = re.compile(
    r"\b(estou|to|tou|tô|sinto|sentindo|meu|minha|meus|minhas|ele|ela|alguem|uma pessoa|crianca|bebe|"
    r"agora|urgente|socorro|rapido|ajuda|de repente|forte|muito|nao para)\b")

EMERGENCY_MESSAGE = (
    "⚠️ Isso pode ser uma emergência. Ligue AGORA para o SAMU 192 (gratuito, 24 horas) "
    "ou vá à UPA ou ao pronto-socorro mais próximo. Em caso de risco imediato, não espere por esta conversa. "
    "A Susana fornece apenas informações administrativas e não substitui atendimento de saúde."
)
SUICIDE_MESSAGE = (
    "Sinto muito que você esteja passando por isso. Você não está sozinho(a). "
    "Ligue para o CVV no 188 (gratuito, 24 horas) ou acesse cvv.org.br. "
    "Se houver risco imediato, ligue para o SAMU 192 ou vá ao pronto-socorro mais próximo. "
    "Os CAPS (Centros de Atenção Psicossocial) da rede pública também acolhem sem agendamento."
)


def _norm(text: str) -> str:
    text = "".join(c for c in unicodedata.normalize("NFD", text.lower()) if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", text)


def emergency_message(text: str) -> Optional[str]:
    """Mensagem de emergência a mostrar, ou None se não há sinal de emergência."""
    t = _norm(text)
    if SUICIDE.search(t):
        return SUICIDE_MESSAGE
    if SEVERE.search(t) and NOW_OR_PERSONAL.search(t):
        return EMERGENCY_MESSAGE
    return None
