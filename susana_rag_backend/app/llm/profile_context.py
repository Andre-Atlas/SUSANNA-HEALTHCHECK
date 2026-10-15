"""
Bloco de perfil do cidadão para personalizar o prompt (minimização de dados)
===========================================================================
Somente dados não identificáveis entram no prompt: faixa etária, idade, sexo
biológico, condições declaradas, RA e vacinas pendentes. Nunca CPF, CNS,
telefone, nome completo, data exata de nascimento ou coordenadas.
"""
from __future__ import annotations

from typing import Optional, Sequence

from app.citizen.schemas import CONDITION_LABELS, DEFAULT_RA, CitizenProfileResponse

_FAIXA = {
    "recem_nascido": "recém-nascido",
    "crianca": "criança",
    "adolescente": "adolescente",
    "adulto": "adulto",
    "idoso": "idoso (60+)",
}


def build_profile_block(profile: Optional[CitizenProfileResponse], pending_vaccines: Sequence[str] = ()) -> Optional[str]:
    if profile is None:
        return None
    parts = []
    if profile.faixa_etaria:
        parts.append(f"faixa etária {_FAIXA.get(profile.faixa_etaria, profile.faixa_etaria)} ({profile.idade_anos} anos)")
    if profile.sexo_biologico:
        parts.append(f"sexo biológico {'feminino' if profile.sexo_biologico == 'F' else 'masculino'}")
    conds = [CONDITION_LABELS.get(c, c).lower() for c in profile.condicoes]
    if conds:
        parts.append("condições declaradas: " + ", ".join(conds))
    if profile.ra_residencia and profile.ra_residencia != DEFAULT_RA:
        parts.append(f"mora em {profile.ra_display}")
    if pending_vaccines:
        parts.append("vacinas possivelmente pendentes: " + ", ".join(list(pending_vaccines)[:3]))
    if not parts:
        return None
    return (
        "PERFIL DO CIDADÃO (use apenas para personalizar orientações administrativas; não faça diagnóstico): "
        + "; ".join(parts)
        + "."
    )
