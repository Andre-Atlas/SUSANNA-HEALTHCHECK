"""Schemas Pydantic para Cadastro e Gestão de Cidadãos no SUS-DF."""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from app.citizen.validators import validate_cpf, validate_cns


class CitizenRegisterRequest(BaseModel):
    nome_completo: str = Field(..., min_length=3, max_length=150, description="Nome completo do cidadão")
    cpf: str = Field(..., description="CPF válido com 11 dígitos")
    cns: Optional[str] = Field(None, description="Cartão Nacional de Saúde (15 dígitos)")
    data_nascimento: str = Field(..., description="Data de nascimento no formato YYYY-MM-DD")
    sexo_biologico: str = Field("F", pattern="^(M|F|N)$", description="Sexo biológico (M, F ou N para não informado)")
    gestante: bool = Field(False, description="Indicador se a cidadã está gestante")
    ra_residencia: str = Field(..., min_length=2, max_length=60, description="Região Administrativa do DF")
    bairro_ou_setor: Optional[str] = Field(None, max_length=100)
    telefone: Optional[str] = Field(None, max_length=20)

    @field_validator("cpf")
    @classmethod
    def check_cpf(cls, v: str) -> str:
        clean = "".join(filter(str.isdigit, str(v)))
        if not validate_cpf(clean):
            raise ValueError("CPF informado é inválido pelo algoritmo do Módulo 11 da Receita Federal.")
        return clean

    @field_validator("cns")
    @classmethod
    def check_cns(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        clean = "".join(filter(str.isdigit, str(v)))
        if not validate_cns(clean):
            raise ValueError("Cartão Nacional de Saúde (CNS) informado é inválido pelo algoritmo do DATASUS.")
        return clean


class CitizenLoginRequest(BaseModel):
    cpf_or_cns: str = Field(..., description="CPF ou Cartão SUS cadastrado")
    data_nascimento: str = Field(..., description="Data de nascimento YYYY-MM-DD para autenticação simples")


class CitizenProfileResponse(BaseModel):
    id: str
    nome_completo: str
    primeiro_nome: str
    cpf_mascarado: str
    cns_mascarado: Optional[str]
    data_nascimento: str
    idade_anos: int
    faixa_etaria: str  # recem_nascido, crianca, adolescente, adulto, idoso
    sexo_biologico: str
    gestante: bool
    ra_residencia: str
    ra_display: str
    bairro_ou_setor: Optional[str]
    telefone: Optional[str]
    created_at: str


class CitizenUpdateRequest(BaseModel):
    ra_residencia: Optional[str] = None
    gestante: Optional[bool] = None
    bairro_ou_setor: Optional[str] = None
    telefone: Optional[str] = None
