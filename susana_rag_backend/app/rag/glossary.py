"""Expansão de siglas do SUS-DF antes da busca vetorial.

O modelo de embeddings não conhece siglas locais ("UBS" fica longe de "Unidade Básica de Saúde"
no espaço vetorial). Acrescentar o significado à pergunta aproxima a consulta dos textos oficiais,
que costumam usar o nome por extenso. Só afeta a BUSCA; o LLM recebe a pergunta original.
"""
from __future__ import annotations

import re

GLOSSARY = {
    "UBS": "Unidade Básica de Saúde, posto de saúde",
    "UPA": "Unidade de Pronto Atendimento",
    "SAMU": "SAMU 192, Serviço de Atendimento Móvel de Urgência",
    "CEAF": "Componente Especializado da Assistência Farmacêutica, Farmácia de Alto Custo",
    "SES": "Secretaria de Estado de Saúde",
    "SES-DF": "Secretaria de Estado de Saúde do Distrito Federal",
    "CNS": "Cartão Nacional de Saúde, cartão do SUS",
    "SISREG": "Sistema de Regulação, marcação de consultas e exames",
    "HRAN": "Hospital Regional da Asa Norte",
    "HRT": "Hospital Regional de Taguatinga",
    "HRC": "Hospital Regional de Ceilândia",
    "HRG": "Hospital Regional do Gama",
    "HRL": "Hospital da Região Leste, Paranoá",
    "HRS": "Hospital Regional de Sobradinho",
    "HRSM": "Hospital Regional de Santa Maria",
    "EMAD": "Equipe Multiprofissional de Atenção Domiciliar",
    "NRAD": "Núcleo Regional de Atenção Domiciliar",
}

_PATTERN = re.compile(r"\b(" + "|".join(sorted(map(re.escape, GLOSSARY), key=len, reverse=True)) + r")\b", re.I)


def expand_acronyms(text: str) -> str:
    """'Onde fica a UBS?' → 'Onde fica a UBS? (UBS: Unidade Básica de Saúde, posto de saúde)'."""
    found = []
    for m in _PATTERN.finditer(text):
        key = m.group(1).upper()
        if key not in found:
            found.append(key)
    if not found:
        return text
    return text + " (" + "; ".join(f"{k}: {GLOSSARY[k]}" for k in found) + ")"
