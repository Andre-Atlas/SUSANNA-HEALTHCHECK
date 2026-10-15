"""Rotas da Agenda personalizada (exigem login)."""
from __future__ import annotations

from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.agenda.schemas import (
    AgendaEvent,
    AgendaEventCreate,
    AgendaEventUpdate,
    AgendaOverview,
    PendingVaccine,
    ProposalConfirmRequest,
    ScheduleVaccineRequest,
    VaccineRecord,
    VaccineRecordCreate,
)
from app.agenda.storage import AgendaStorage, ProposalError, get_agenda_storage
from app.citizen.auth import get_current_citizen
from app.citizen.schemas import CitizenProfileResponse
from app.vaccines.schedule import VALID_VACCINE_IDS, compute_pending

router = APIRouter(prefix="/api/agenda", tags=["agenda"])


def pending_for(citizen: CitizenProfileResponse, agenda: AgendaStorage) -> List[PendingVaccine]:
    return compute_pending(citizen.data_nascimento, citizen.condicoes, agenda.list_vaccine_records(citizen.id))


@router.get("", response_model=List[AgendaEvent])
def list_events(
    start: Optional[str] = Query(None, alias="from"),
    end: Optional[str] = Query(None, alias="to"),
    citizen: CitizenProfileResponse = Depends(get_current_citizen),
    agenda: AgendaStorage = Depends(get_agenda_storage),
):
    return agenda.list_events(citizen.id, start, end)


@router.get("/overview", response_model=AgendaOverview)
def overview(
    citizen: CitizenProfileResponse = Depends(get_current_citizen),
    agenda: AgendaStorage = Depends(get_agenda_storage),
):
    hoje = date.today()
    eventos = [
        e for e in agenda.list_events(citizen.id, hoje.isoformat(), (hoje + timedelta(days=30)).isoformat())
        if e.status == "agendado"
    ]
    vacinas = pending_for(citizen, agenda)
    urgentes = sum(1 for v in vacinas if v.status in ("atrasada", "agora"))
    proximos_7d = sum(1 for e in eventos if e.data_evento <= (hoje + timedelta(days=7)).isoformat())
    return AgendaOverview(
        eventos=eventos,
        vacinas_pendentes=vacinas,
        perfil_incompleto=citizen.data_nascimento is None,
        pendencias=urgentes + proximos_7d,
    )


@router.post("/events", response_model=AgendaEvent, status_code=201)
def create_event(
    req: AgendaEventCreate,
    citizen: CitizenProfileResponse = Depends(get_current_citizen),
    agenda: AgendaStorage = Depends(get_agenda_storage),
):
    return agenda.create_event(citizen.id, req)


@router.patch("/events/{event_id}", response_model=AgendaEvent)
def update_event(
    event_id: str,
    req: AgendaEventUpdate,
    citizen: CitizenProfileResponse = Depends(get_current_citizen),
    agenda: AgendaStorage = Depends(get_agenda_storage),
):
    ev = agenda.update_event(citizen.id, event_id, req)
    if not ev:
        raise HTTPException(status_code=404, detail="Evento não encontrado.")
    return ev


@router.delete("/events/{event_id}")
def delete_event(
    event_id: str,
    citizen: CitizenProfileResponse = Depends(get_current_citizen),
    agenda: AgendaStorage = Depends(get_agenda_storage),
):
    if not agenda.delete_event(citizen.id, event_id):
        raise HTTPException(status_code=404, detail="Evento não encontrado.")
    return {"status": "deleted", "id": event_id}


@router.get("/vaccines/pending", response_model=List[PendingVaccine])
def list_pending_vaccines(
    citizen: CitizenProfileResponse = Depends(get_current_citizen),
    agenda: AgendaStorage = Depends(get_agenda_storage),
):
    return pending_for(citizen, agenda)


@router.get("/vaccines/records", response_model=List[VaccineRecord])
def list_vaccine_records(
    citizen: CitizenProfileResponse = Depends(get_current_citizen),
    agenda: AgendaStorage = Depends(get_agenda_storage),
):
    return agenda.list_vaccine_records(citizen.id)


@router.post("/vaccines/records", response_model=VaccineRecord, status_code=201)
def add_vaccine_record(
    req: VaccineRecordCreate,
    citizen: CitizenProfileResponse = Depends(get_current_citizen),
    agenda: AgendaStorage = Depends(get_agenda_storage),
):
    if req.vaccine_id not in VALID_VACCINE_IDS:
        raise HTTPException(status_code=422, detail="Vacina desconhecida.")
    return agenda.add_vaccine_record(citizen.id, req)


@router.delete("/vaccines/records/{record_id}")
def delete_vaccine_record(
    record_id: str,
    citizen: CitizenProfileResponse = Depends(get_current_citizen),
    agenda: AgendaStorage = Depends(get_agenda_storage),
):
    if not agenda.delete_vaccine_record(citizen.id, record_id):
        raise HTTPException(status_code=404, detail="Registro não encontrado.")
    return {"status": "deleted", "id": record_id}


@router.post("/vaccines/{vaccine_id}/schedule", response_model=AgendaEvent, status_code=201)
def schedule_vaccine(
    vaccine_id: str,
    req: ScheduleVaccineRequest,
    citizen: CitizenProfileResponse = Depends(get_current_citizen),
    agenda: AgendaStorage = Depends(get_agenda_storage),
):
    item = next((v for v in pending_for(citizen, agenda) if v.vaccine_id == vaccine_id), None)
    if vaccine_id not in VALID_VACCINE_IDS:
        raise HTTPException(status_code=422, detail="Vacina desconhecida.")
    titulo = f"Vacina – {item.nome}" if item else "Vacina"
    return agenda.create_event(
        citizen.id,
        AgendaEventCreate(
            tipo="vacina",
            titulo=titulo[:120],
            data_evento=req.data_evento,
            horario=req.horario,
            unidade_saude=req.unidade_saude,
            notas=f"{item.dose_label}. Leve a caderneta de vacinação." if item else None,
            lembrete_min_antes=24 * 60,
        ),
    )


@router.post("/proposals/{proposal_id}/confirm", response_model=AgendaEvent, status_code=201)
def confirm_proposal(
    proposal_id: str,
    req: ProposalConfirmRequest,
    citizen: CitizenProfileResponse = Depends(get_current_citizen),
    agenda: AgendaStorage = Depends(get_agenda_storage),
):
    try:
        proposal = agenda.get_proposal(citizen.id, proposal_id)
    except ProposalError as e:
        if e.code == "not_found":
            raise HTTPException(status_code=404, detail="Proposta não encontrada.")
        if e.code == "consumed":
            raise HTTPException(status_code=409, detail="Este lembrete já foi adicionado.")
        raise HTTPException(status_code=410, detail="A proposta expirou. Peça novamente no chat.")
    overrides = req.model_dump(exclude_unset=True, exclude_none=True)
    merged = {**proposal.model_dump(), **overrides}
    if not merged.get("data_evento"):
        raise HTTPException(status_code=422, detail="Informe a data do evento.")
    event = agenda.create_event(
        citizen.id,
        AgendaEventCreate(
            tipo=merged["tipo"],
            titulo=merged["titulo"],
            data_evento=merged["data_evento"],
            horario=merged.get("horario"),
            unidade_saude=merged.get("unidade_saude"),
            recorrencia=merged.get("recorrencia"),
            lembrete_min_antes=merged.get("lembrete_min_antes") or (15 if merged["tipo"] == "medicamento" else 60),
        ),
        origem="chat",
    )
    agenda.consume_proposal(citizen.id, proposal_id)
    return event


@router.post("/proposals/{proposal_id}/dismiss")
def dismiss_proposal(
    proposal_id: str,
    citizen: CitizenProfileResponse = Depends(get_current_citizen),
    agenda: AgendaStorage = Depends(get_agenda_storage),
):
    agenda.consume_proposal(citizen.id, proposal_id)
    return {"status": "dismissed"}
