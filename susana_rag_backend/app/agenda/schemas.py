"""Schemas da Agenda personalizada."""
from __future__ import annotations

import re
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.vaccines.schedule import PendingVaccine, VaccineRecord

EVENT_TYPES = ("consulta", "exame", "vacina", "medicamento", "outro")
EVENT_STATUS = ("agendado", "concluido", "cancelado")
TYPE_PATTERN = "^(" + "|".join(EVENT_TYPES) + ")$"


def _check_date(v: Optional[str]) -> Optional[str]:
    if v is None:
        return None
    try:
        datetime.strptime(v, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Data deve estar no formato AAAA-MM-DD.")
    return v


def _check_time(v: Optional[str]) -> Optional[str]:
    if v is None or v == "":
        return None
    if not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", v):
        raise ValueError("Horário deve estar no formato HH:MM.")
    return v


class AgendaEventBase(BaseModel):
    @field_validator("data_evento", check_fields=False)
    @classmethod
    def v_date(cls, v):
        return _check_date(v)

    @field_validator("horario", check_fields=False)
    @classmethod
    def v_time(cls, v):
        return _check_time(v)


class AgendaEventCreate(AgendaEventBase):
    tipo: str = Field(..., pattern=TYPE_PATTERN)
    titulo: str = Field(..., min_length=2, max_length=120)
    data_evento: str
    horario: Optional[str] = None
    unidade_saude: Optional[str] = Field(None, max_length=160)
    unidade_id: Optional[str] = None
    notas: Optional[str] = Field(None, max_length=500)
    lembrete_min_antes: int = Field(60, ge=0, le=7 * 24 * 60)
    recorrencia: Optional[str] = Field(None, pattern="^(diaria|semanal)$")


class AgendaEventUpdate(AgendaEventBase):
    tipo: Optional[str] = Field(None, pattern=TYPE_PATTERN)
    titulo: Optional[str] = Field(None, min_length=2, max_length=120)
    data_evento: Optional[str] = None
    horario: Optional[str] = None
    unidade_saude: Optional[str] = Field(None, max_length=160)
    unidade_id: Optional[str] = None
    notas: Optional[str] = Field(None, max_length=500)
    lembrete_min_antes: Optional[int] = Field(None, ge=0, le=7 * 24 * 60)
    recorrencia: Optional[str] = Field(None, pattern="^(diaria|semanal)$")
    status: Optional[str] = Field(None, pattern="^(" + "|".join(EVENT_STATUS) + ")$")


class AgendaEvent(BaseModel):
    id: str
    tipo: str
    titulo: str
    data_evento: str
    horario: Optional[str] = None
    unidade_saude: Optional[str] = None
    unidade_id: Optional[str] = None
    notas: Optional[str] = None
    lembrete_min_antes: int = 60
    recorrencia: Optional[str] = None
    status: str = "agendado"
    origem: str = "manual"
    created_at: str
    updated_at: str


class AgendaOverview(BaseModel):
    eventos: List[AgendaEvent]
    vacinas_pendentes: List[PendingVaccine]
    perfil_incompleto: bool = False
    pendencias: int = 0


class VaccineRecordCreate(BaseModel):
    vaccine_id: str
    dose_num: int = Field(1, ge=1, le=10)
    data_aplicacao: Optional[str] = None

    @field_validator("data_aplicacao")
    @classmethod
    def v_date(cls, v):
        return _check_date(v)


class ScheduleVaccineRequest(BaseModel):
    dose_num: int = Field(1, ge=1, le=10)
    data_evento: str
    horario: Optional[str] = None
    unidade_saude: Optional[str] = None

    @field_validator("data_evento")
    @classmethod
    def v_date(cls, v):
        return _check_date(v)

    @field_validator("horario")
    @classmethod
    def v_time(cls, v):
        return _check_time(v)


class AgendaProposal(BaseModel):
    """Evento sugerido pelo chat; só vira evento após confirmação do cidadão."""
    proposal_id: str = ""
    tipo: str = "consulta"
    titulo: str = "Consulta"
    data_evento: Optional[str] = None
    horario: Optional[str] = None
    unidade_saude: Optional[str] = None
    recorrencia: Optional[str] = None
    faltando: List[str] = Field(default_factory=list)
    texto_confirmacao: str = ""


class ProposalConfirmRequest(AgendaEventBase):
    tipo: Optional[str] = Field(None, pattern=TYPE_PATTERN)
    titulo: Optional[str] = Field(None, min_length=2, max_length=120)
    data_evento: Optional[str] = None
    horario: Optional[str] = None
    unidade_saude: Optional[str] = Field(None, max_length=160)
    lembrete_min_antes: Optional[int] = Field(None, ge=0, le=7 * 24 * 60)


__all__ = [
    "AgendaEvent", "AgendaEventCreate", "AgendaEventUpdate", "AgendaOverview", "AgendaProposal",
    "PendingVaccine", "ProposalConfirmRequest", "ScheduleVaccineRequest", "VaccineRecord",
    "VaccineRecordCreate", "EVENT_TYPES",
]
