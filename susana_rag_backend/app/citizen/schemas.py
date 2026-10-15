"""Schemas Pydantic para Cadastro (opcional), Login e Perfil do Cidadão no SUS-DF."""
from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.citizen.security import check_password_policy
from app.citizen.validators import validate_cns, validate_cpf

# Checklist opcional de condições de saúde (id -> rótulo exibido na interface)
CONDITION_LABELS: dict = {
    "gestante": "Gestante",
    "diabetes": "Diabetes",
    "hipertensao": "Hipertensão",
    "asma": "Asma",
    "dpoc": "DPOC / doença pulmonar crônica",
    "cardiopatia": "Doença cardíaca",
    "doenca_renal_cronica": "Doença renal crônica",
    "imunossupressao": "Imunossupressão",
    "hiv": "HIV",
    "cancer": "Câncer (em tratamento)",
    "obesidade": "Obesidade",
    "deficiencia": "Pessoa com deficiência",
    "tabagismo": "Tabagismo",
}

DEFAULT_RA = "geral_df"


def _clean_digits(v: Optional[str]) -> str:
    return "".join(filter(str.isdigit, str(v or "")))


def _validate_birth_date(v: Optional[str]) -> Optional[str]:
    if not v:
        return None
    try:
        d = datetime.strptime(v, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Data de nascimento deve estar no formato AAAA-MM-DD.")
    hoje = date.today()
    if d > hoje:
        raise ValueError("Data de nascimento não pode estar no futuro.")
    if hoje.year - d.year > 120:
        raise ValueError("Data de nascimento inválida.")
    return v


def _validate_phone(v: Optional[str]) -> Optional[str]:
    if v is None or v == "":
        return None
    clean = _clean_digits(v)
    if len(clean) not in (10, 11):
        raise ValueError("Telefone deve ter DDD + número (10 ou 11 dígitos).")
    return clean


def _validate_ra(v: Optional[str]) -> Optional[str]:
    if v is None or v == "":
        return None
    from app.rag.nlu import RA_DICTIONARY

    norm = v.strip().lower().replace(" ", "_")
    valid = {rid for rid, _ in RA_DICTIONARY} | {DEFAULT_RA}
    if norm not in valid:
        raise ValueError("Região Administrativa desconhecida.")
    return norm


def _validate_conditions(v: Optional[List[str]]) -> Optional[List[str]]:
    if v is None:
        return None
    out: List[str] = []
    for c in v:
        key = str(c).strip().lower()
        if key not in CONDITION_LABELS:
            raise ValueError(f"Condição de saúde desconhecida: {c}")
        if key not in out:
            out.append(key)
    return out


class CitizenRegisterRequest(BaseModel):
    # Passo 1 (obrigatório): acesso
    nome_completo: str = Field(..., min_length=3, max_length=150)
    cpf: str = Field(..., description="CPF válido com 11 dígitos")
    senha: str = Field(..., description="Senha de acesso")
    lembrar: bool = Field(False, description="Manter conectado por 30 dias")
    # Passos 2 e 3 (opcionais): perfil e saúde
    cns: Optional[str] = None
    data_nascimento: Optional[str] = None
    sexo_biologico: Optional[str] = Field(None, pattern="^(M|F)$")
    ra_residencia: Optional[str] = None
    bairro_ou_setor: Optional[str] = Field(None, max_length=100)
    telefone: Optional[str] = None
    condicoes: List[str] = Field(default_factory=list)

    @field_validator("nome_completo")
    @classmethod
    def check_nome(cls, v: str) -> str:
        v = " ".join(v.split())
        if len(v) < 3:
            raise ValueError("Informe seu nome.")
        return v

    @field_validator("cpf")
    @classmethod
    def check_cpf(cls, v: str) -> str:
        clean = _clean_digits(v)
        if not validate_cpf(clean):
            raise ValueError("CPF inválido.")
        return clean

    @field_validator("senha")
    @classmethod
    def check_senha(cls, v: str) -> str:
        return check_password_policy(v)

    @field_validator("cns")
    @classmethod
    def check_cns(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        clean = _clean_digits(v)
        if not validate_cns(clean):
            raise ValueError("Cartão Nacional de Saúde (CNS) inválido.")
        return clean

    @field_validator("data_nascimento")
    @classmethod
    def check_nascimento(cls, v: Optional[str]) -> Optional[str]:
        return _validate_birth_date(v)

    @field_validator("telefone")
    @classmethod
    def check_telefone(cls, v: Optional[str]) -> Optional[str]:
        return _validate_phone(v)

    @field_validator("ra_residencia")
    @classmethod
    def check_ra(cls, v: Optional[str]) -> Optional[str]:
        return _validate_ra(v)

    @field_validator("condicoes")
    @classmethod
    def check_condicoes(cls, v):
        return _validate_conditions(v) or []


class CitizenLoginRequest(BaseModel):
    cpf: str
    senha: str
    lembrar: bool = False

    @field_validator("cpf")
    @classmethod
    def clean_cpf(cls, v: str) -> str:
        return _clean_digits(v)


class CitizenProfileResponse(BaseModel):
    id: str
    nome_completo: str
    primeiro_nome: str
    cpf_mascarado: str
    cns_mascarado: Optional[str] = None
    data_nascimento: Optional[str] = None
    idade_anos: Optional[int] = None
    faixa_etaria: Optional[str] = None  # recem_nascido, crianca, adolescente, adulto, idoso
    sexo_biologico: Optional[str] = None
    gestante: bool = False
    condicoes: List[str] = Field(default_factory=list)
    ra_residencia: str = DEFAULT_RA
    ra_display: str = "Distrito Federal"
    bairro_ou_setor: Optional[str] = None
    telefone: Optional[str] = None
    perfil_completo: bool = False
    created_at: str


class AuthResponse(BaseModel):
    token: str
    expires_at: str
    remember: bool
    citizen: CitizenProfileResponse


class CitizenUpdateRequest(BaseModel):
    nome_completo: Optional[str] = Field(None, min_length=3, max_length=150)
    data_nascimento: Optional[str] = None
    sexo_biologico: Optional[str] = Field(None, pattern="^(M|F)$")
    ra_residencia: Optional[str] = None
    bairro_ou_setor: Optional[str] = Field(None, max_length=100)
    telefone: Optional[str] = None
    condicoes: Optional[List[str]] = None
    # Mantido por compatibilidade: equivale a incluir/remover "gestante" de condicoes
    gestante: Optional[bool] = None

    @field_validator("data_nascimento")
    @classmethod
    def check_nascimento(cls, v: Optional[str]) -> Optional[str]:
        return _validate_birth_date(v)

    @field_validator("telefone")
    @classmethod
    def check_telefone(cls, v: Optional[str]) -> Optional[str]:
        return _validate_phone(v)

    @field_validator("ra_residencia")
    @classmethod
    def check_ra(cls, v: Optional[str]) -> Optional[str]:
        return _validate_ra(v)

    @field_validator("condicoes")
    @classmethod
    def check_condicoes(cls, v):
        return _validate_conditions(v)


class ChangePasswordRequest(BaseModel):
    senha_atual: str
    nova_senha: str

    @field_validator("nova_senha")
    @classmethod
    def check_nova(cls, v: str) -> str:
        return check_password_policy(v)


class DeleteAccountRequest(BaseModel):
    senha: str


class ConditionOption(BaseModel):
    id: str
    label: str
