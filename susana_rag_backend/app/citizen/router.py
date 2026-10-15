"""Rotas FastAPI para Cadastro opcional, Login (CPF + senha) e Perfil do Cidadão SUS-DF."""
from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request

from app.citizen.auth import (
    AuthStorage,
    get_auth_storage,
    get_bearer_token,
    get_current_citizen,
)
from app.citizen.schemas import (
    CONDITION_LABELS,
    AuthResponse,
    ChangePasswordRequest,
    CitizenLoginRequest,
    CitizenProfileResponse,
    CitizenRegisterRequest,
    CitizenUpdateRequest,
    ConditionOption,
    DeleteAccountRequest,
)
from app.citizen.security import login_rate_limiter
from app.citizen.storage import CitizenStorage, get_citizen_storage

logger = logging.getLogger("susana.citizen.router")
router = APIRouter(prefix="/api/citizen", tags=["citizen"])

INVALID_CREDENTIALS = "CPF ou senha incorretos."


def _auth_response(auth: AuthStorage, profile: CitizenProfileResponse, remember: bool, request: Request) -> AuthResponse:
    token, expires = auth.create_session(profile.id, remember, request.headers.get("user-agent"))
    return AuthResponse(token=token, expires_at=expires, remember=remember, citizen=profile)


@router.get("/conditions", response_model=List[ConditionOption])
def list_conditions():
    return [ConditionOption(id=k, label=v) for k, v in CONDITION_LABELS.items()]


@router.post("/register", response_model=AuthResponse, status_code=201)
def register_citizen(
    req: CitizenRegisterRequest,
    request: Request,
    storage: CitizenStorage = Depends(get_citizen_storage),
    auth: AuthStorage = Depends(get_auth_storage),
):
    try:
        profile = storage.register_citizen(req)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    logger.info("Nova conta criada (RA: %s)", profile.ra_residencia)
    return _auth_response(auth, profile, req.lembrar, request)


@router.post("/login", response_model=AuthResponse)
def login_citizen(
    req: CitizenLoginRequest,
    request: Request,
    storage: CitizenStorage = Depends(get_citizen_storage),
    auth: AuthStorage = Depends(get_auth_storage),
):
    ip = request.client.host if request.client else ""
    keys = (f"cpf:{req.cpf}", f"ip:{ip}")
    if login_rate_limiter.is_blocked(*keys):
        raise HTTPException(status_code=429, detail="Muitas tentativas. Aguarde alguns minutos e tente novamente.")
    profile = storage.authenticate(req.cpf, req.senha)
    if not profile:
        login_rate_limiter.register_failure(*keys)
        raise HTTPException(status_code=401, detail=INVALID_CREDENTIALS)
    login_rate_limiter.reset(f"cpf:{req.cpf}")
    return _auth_response(auth, profile, req.lembrar, request)


@router.post("/logout")
def logout(
    token: Optional[str] = Depends(get_bearer_token),
    auth: AuthStorage = Depends(get_auth_storage),
):
    if token:
        auth.revoke(token)
    return {"status": "ok"}


@router.post("/logout-all")
def logout_all(
    citizen: CitizenProfileResponse = Depends(get_current_citizen),
    auth: AuthStorage = Depends(get_auth_storage),
):
    auth.revoke_all(citizen.id)
    return {"status": "ok"}


@router.get("/me", response_model=CitizenProfileResponse)
def get_me(citizen: CitizenProfileResponse = Depends(get_current_citizen)):
    return citizen


@router.put("/me", response_model=CitizenProfileResponse)
@router.patch("/me", response_model=CitizenProfileResponse)
def update_me(
    req: CitizenUpdateRequest,
    citizen: CitizenProfileResponse = Depends(get_current_citizen),
    storage: CitizenStorage = Depends(get_citizen_storage),
):
    updated = storage.update_citizen(citizen.id, req)
    if not updated:
        raise HTTPException(status_code=404, detail="Conta não encontrada.")
    return updated


@router.post("/me/password")
def change_password(
    req: ChangePasswordRequest,
    citizen: CitizenProfileResponse = Depends(get_current_citizen),
    token: Optional[str] = Depends(get_bearer_token),
    storage: CitizenStorage = Depends(get_citizen_storage),
    auth: AuthStorage = Depends(get_auth_storage),
):
    if not storage.verify_citizen_password(citizen.id, req.senha_atual):
        raise HTTPException(status_code=403, detail="Senha atual incorreta.")
    storage.set_password(citizen.id, req.nova_senha)
    auth.revoke_all(citizen.id, except_token=token)
    return {"status": "ok"}


@router.delete("/me")
def delete_me(
    req: DeleteAccountRequest,
    citizen: CitizenProfileResponse = Depends(get_current_citizen),
    storage: CitizenStorage = Depends(get_citizen_storage),
):
    if not storage.verify_citizen_password(citizen.id, req.senha):
        raise HTTPException(status_code=403, detail="Senha incorreta.")
    storage.delete_citizen(citizen.id)
    logger.info("Conta excluída a pedido do titular.")
    return {"status": "deleted"}
