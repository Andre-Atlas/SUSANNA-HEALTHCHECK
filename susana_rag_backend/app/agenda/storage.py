"""Persistência da Agenda (eventos, registros de vacina e propostas do chat)."""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from app.agenda.schemas import (
    AgendaEvent,
    AgendaEventCreate,
    AgendaEventUpdate,
    AgendaProposal,
    VaccineRecord,
    VaccineRecordCreate,
)
from app.citizen.storage import CitizenStorage, _now, get_citizen_storage

PROPOSAL_TTL = timedelta(minutes=30)


class ProposalError(Exception):
    """Proposta inexistente, expirada ou já utilizada."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code  # not_found | consumed | expired


def _event(row: sqlite3.Row) -> AgendaEvent:
    return AgendaEvent(**{k: row[k] for k in row.keys() if k != "citizen_id"})


class AgendaStorage:
    def __init__(self, citizen_storage: Optional[CitizenStorage] = None):
        self.storage = citizen_storage or get_citizen_storage()

    # ------------------------------------------------------------------ eventos
    def list_events(self, citizen_id: str, start: Optional[str] = None, end: Optional[str] = None,
                    include_cancelled: bool = False) -> List[AgendaEvent]:
        sql = "SELECT * FROM agenda_events WHERE citizen_id = ?"
        args: list = [citizen_id]
        if start:
            sql += " AND (data_evento >= ? OR recorrencia IS NOT NULL)"
            args.append(start)
        if end:
            sql += " AND data_evento <= ?"
            args.append(end)
        if not include_cancelled:
            sql += " AND status != 'cancelado'"
        sql += " ORDER BY data_evento ASC, COALESCE(horario, '99:99') ASC"
        with self.storage._lock, self.storage._get_connection() as conn:
            return [_event(r) for r in conn.execute(sql, args).fetchall()]

    def get_event(self, citizen_id: str, event_id: str) -> Optional[AgendaEvent]:
        with self.storage._lock, self.storage._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM agenda_events WHERE id = ? AND citizen_id = ?", (event_id, citizen_id)
            ).fetchone()
        return _event(row) if row else None

    def create_event(self, citizen_id: str, req: AgendaEventCreate, origem: str = "manual") -> AgendaEvent:
        eid = str(uuid.uuid4())
        now = _now().isoformat()
        with self.storage._lock, self.storage._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO agenda_events (id, citizen_id, tipo, titulo, data_evento, horario, unidade_saude,
                    unidade_id, notas, lembrete_min_antes, recorrencia, status, origem, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'agendado', ?, ?, ?)
                """,
                (eid, citizen_id, req.tipo, req.titulo, req.data_evento, req.horario, req.unidade_saude,
                 req.unidade_id, req.notas, req.lembrete_min_antes, req.recorrencia, origem, now, now),
            )
        return self.get_event(citizen_id, eid)

    def update_event(self, citizen_id: str, event_id: str, req: AgendaEventUpdate) -> Optional[AgendaEvent]:
        data = req.model_dump(exclude_unset=True)
        if not self.get_event(citizen_id, event_id):
            return None
        if data:
            cols = ", ".join(f"{k} = ?" for k in data) + ", updated_at = ?"
            with self.storage._lock, self.storage._get_connection() as conn:
                conn.execute(
                    f"UPDATE agenda_events SET {cols} WHERE id = ? AND citizen_id = ?",
                    [*data.values(), _now().isoformat(), event_id, citizen_id],
                )
        return self.get_event(citizen_id, event_id)

    def delete_event(self, citizen_id: str, event_id: str) -> bool:
        with self.storage._lock, self.storage._get_connection() as conn:
            res = conn.execute("DELETE FROM agenda_events WHERE id = ? AND citizen_id = ?", (event_id, citizen_id))
            return res.rowcount > 0

    # ------------------------------------------------------- registros vacinais
    def list_vaccine_records(self, citizen_id: str) -> List[VaccineRecord]:
        with self.storage._lock, self.storage._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM vaccine_records WHERE citizen_id = ? ORDER BY created_at DESC", (citizen_id,)
            ).fetchall()
        return [VaccineRecord(id=r["id"], vaccine_id=r["vaccine_id"], dose_num=r["dose_num"],
                              data_aplicacao=r["data_aplicacao"], created_at=r["created_at"]) for r in rows]

    def add_vaccine_record(self, citizen_id: str, req: VaccineRecordCreate) -> VaccineRecord:
        rid = str(uuid.uuid4())
        now = _now().isoformat()
        aplic = req.data_aplicacao or now[:10]
        with self.storage._lock, self.storage._get_connection() as conn:
            # Doses periódicas (dT, Influenza) substituem o registro anterior
            conn.execute(
                "DELETE FROM vaccine_records WHERE citizen_id = ? AND vaccine_id = ? AND dose_num = ?",
                (citizen_id, req.vaccine_id, req.dose_num),
            )
            conn.execute(
                "INSERT INTO vaccine_records (id, citizen_id, vaccine_id, dose_num, data_aplicacao, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (rid, citizen_id, req.vaccine_id, req.dose_num, aplic, now),
            )
        return VaccineRecord(id=rid, vaccine_id=req.vaccine_id, dose_num=req.dose_num, data_aplicacao=aplic, created_at=now)

    def delete_vaccine_record(self, citizen_id: str, record_id: str) -> bool:
        with self.storage._lock, self.storage._get_connection() as conn:
            res = conn.execute("DELETE FROM vaccine_records WHERE id = ? AND citizen_id = ?", (record_id, citizen_id))
            return res.rowcount > 0

    # ---------------------------------------------------------------- propostas
    def save_proposal(self, citizen_id: str, proposal: AgendaProposal) -> AgendaProposal:
        now = _now()
        pid = proposal.proposal_id or str(uuid.uuid4())
        proposal = proposal.model_copy(update={"proposal_id": pid})
        with self.storage._lock, self.storage._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO agenda_proposals (id, citizen_id, payload_json, created_at, expires_at, consumed)
                VALUES (?, ?, ?, ?, ?, 0)
                """,
                (pid, citizen_id, proposal.model_dump_json(), now.isoformat(), (now + PROPOSAL_TTL).isoformat()),
            )
        return proposal

    def get_proposal(self, citizen_id: str, proposal_id: str) -> AgendaProposal:
        with self.storage._lock, self.storage._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM agenda_proposals WHERE id = ? AND citizen_id = ?", (proposal_id, citizen_id)
            ).fetchone()
        if not row:
            raise ProposalError("not_found")
        if row["consumed"]:
            raise ProposalError("consumed")
        if datetime.fromisoformat(row["expires_at"]) <= _now():
            raise ProposalError("expired")
        return AgendaProposal(**json.loads(row["payload_json"]))

    def consume_proposal(self, citizen_id: str, proposal_id: str) -> None:
        with self.storage._lock, self.storage._get_connection() as conn:
            conn.execute(
                "UPDATE agenda_proposals SET consumed = 1 WHERE id = ? AND citizen_id = ?", (proposal_id, citizen_id)
            )


_agenda_storage: Optional[AgendaStorage] = None


def get_agenda_storage() -> AgendaStorage:
    global _agenda_storage
    if _agenda_storage is None:
        _agenda_storage = AgendaStorage()
    return _agenda_storage
