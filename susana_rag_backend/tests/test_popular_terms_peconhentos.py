"""Vocabulário popular de acidentes com animais peçonhentos (cobra, escorpião, aranha)."""
from __future__ import annotations

import pytest

from app.rag.conversation import ConversationalContextManager, expand_popular_terms


@pytest.mark.parametrize(
    "pergunta, esperado",
    [
        ("uma cobra me mordeu oq eu faço?", ["animal peçonhento", "soro antiofídico", "HRAN"]),
        ("fui picado por uma serpente", ["animal peçonhento", "soro antiofídico"]),
        ("um escorpião me picou", ["animal peçonhento", "soro antiescorpiônico"]),
        ("escorpiões na minha casa", ["animal peçonhento"]),
        ("fui picado por uma aranha", ["animal peçonhento", "HRAN"]),
    ],
)
def test_termos_populares_ganham_vocabulario_oficial(pergunta, esperado):
    expandida = expand_popular_terms(pergunta)
    for termo in esperado:
        assert termo in expandida, f"'{termo}' ausente em: {expandida}"


def test_pergunta_original_e_preservada():
    # A palavra original continua na consulta (ajuda tanto a busca vetorial quanto a lexical)
    assert "cobra" in expand_popular_terms("uma cobra me mordeu").lower()


def test_contextualizacao_inclui_a_ponte_de_vocabulario():
    ctx = ConversationalContextManager.contextualize("fui picado por uma cobra, o que houve?", [])
    assert "peçonhento" in ctx


def test_termos_sem_relacao_nao_sao_alterados():
    assert expand_popular_terms("onde tomar vacina da gripe?") == "onde tomar vacina da gripe?"
