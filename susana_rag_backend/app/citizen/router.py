"""Rotas FastAPI para Cadastro, Login e Perfil do Cidadão SUS-DF."""
from __future__ import annotations

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends

from app.citizen.schemas import (
    CitizenLoginRequest,
    CitizenProfileResponse,
    CitizenRegisterRequest,
    CitizenUpdateRequest,
)
from app.citizen.storage import CitizenStorage, get_citizen_storage

logger = logging.getLogger("susana.citizen.router")
router = APIRouter(prefix="/api/citizen", tags=["citizen"])


@router.post("/register", response_model=CitizenProfileResponse)
def register_citizen(
    req: CitizenRegisterRequest,
    storage: CitizenStorage = Depends(get_citizen_storage),
):
    try:
        profile = storage.register_citizen(req)
        logger.info("Cidadão cadastrado com sucesso: %s (RA: %s)", profile.nome_completo, profile.ra_residencia)
        return profile
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Erro interno ao registrar cidadão: %s", e)
        raise HTTPException(status_code=500, detail="Erro interno ao registrar cidadão.")


@router.post("/login", response_model=CitizenProfileResponse)
def login_citizen(
    req: CitizenLoginRequest,
    storage: CitizenStorage = Depends(get_citizen_storage),
):
    profile = storage.login_citizen(req.cpf_or_cns, req.data_nascimento)
    if not profile:
        raise HTTPException(status_code=404, detail="Cidadão não encontrado com estes dados ou data de nascimento divergente.")
    return profile


@router.get("/me", response_model=CitizenProfileResponse)
def get_current_or_demo_profile(
    citizen_id: Optional[str] = None,
    storage: CitizenStorage = Depends(get_citizen_storage),
):
    if citizen_id:
        p = storage.get_citizen_by_id(citizen_id)
        if p:
            return p
    # Fallback para o primeiro cidadão cadastrado ou demo padrão real do DF
    first = storage.get_first_or_demo_citizen()
    if first:
        return first

    # Se a base estiver virgem, cria um cidadão real do DF (ex: Maria Clara de Brasília/Ceilândia com dados válidos)
    from app.citizen.validators import validate_cpf
    # Cria perfil padrão inicial legítimo
    demo_req = CitizenRegisterRequest(
        nome_completo="Juliana Mendes de Alencar",
        cpf="05481729199",  # CPF matematicamente válido (módulo 11)
        cns="154823192010000",  # CNS válido (algoritmo DATASUS base PIS)
        data_nascimento="1994-05-18",
        sexo_biologico="F",
        gestante=False,
        ra_residencia="ceilandia",
        bairro_ou_setor="Ceilândia Sul",
        telefone="(61) 98765-4321",
    )
    return storage.register_citizen(demo_req)


@router.put("/me", response_model=CitizenProfileResponse)
@router.patch("/me", response_model=CitizenProfileResponse)
def update_profile(
    citizen_id: str,
    req: CitizenUpdateRequest,
    storage: CitizenStorage = Depends(get_citizen_storage),
):
    updated = storage.update_citizen(citizen_id, req)
    if not updated:
        raise HTTPException(status_code=404, detail="Cidadão não encontrado.")
    return updated
