"""
Armazenamento Relacional SQLite (susana_app.db) para Cidadãos, Sessões e Agenda
================================================================================
Modo WAL (Write-Ahead Logging) ativo, thread-safe, sem bloquear o event loop.
"""
from __future__ import annotations

import logging
import sqlite3
import threading
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, List, Optional

from app.citizen.schemas import (
    CitizenProfileResponse,
    CitizenRegisterRequest,
    CitizenUpdateRequest,
)
from app.rag.nlu import RA_DICTIONARY

logger = logging.getLogger("susana.citizen.storage")


def _calc_idade(nasc_str: str) -> tuple[int, str]:
    """Calcula idade em anos e faixa etária para o PNI."""
    try:
        d = datetime.strptime(nasc_str, "%Y-%m-%d").date()
        hoje = date.today()
        idade = hoje.year - d.year - ((hoje.month, hoje.day) < (d.month, d.day))
        if idade < 1:
            faixa = "recem_nascido"
        elif idade < 11:
            faixa = "crianca"
        elif idade < 20:
            faixa = "adolescente"
        elif idade < 60:
            faixa = "adulto"
        else:
            faixa = "idoso"
        return max(0, idade), faixa
    except Exception:
        return 30, "adulto"


def _format_ra_display(ra_id: str) -> str:
    norm = ra_id.lower().replace(" ", "_")
    for rid, aliases in RA_DICTIONARY:
        if rid == norm or norm in [a.lower().replace(" ", "_") for a in aliases]:
            return aliases[0].title()
    return ra_id.title()


class CitizenStorage:
    """Gerencia a persistência de perfis de cidadãos e sessões no SQLite."""

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            backend_dir = Path(__file__).resolve().parent.parent.parent
            self.db_path = backend_dir / "data" / "susana_app.db"
        else:
            self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_db(self) -> None:
        with self._lock, self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS citizens (
                    id TEXT PRIMARY KEY,
                    cpf TEXT UNIQUE NOT NULL,
                    cns TEXT UNIQUE,
                    nome_completo TEXT NOT NULL,
                    data_nascimento TEXT NOT NULL,
                    sexo_biologico TEXT NOT NULL,
                    gestante INTEGER NOT NULL DEFAULT 0,
                    ra_residencia TEXT NOT NULL,
                    bairro_ou_setor TEXT,
                    telefone TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id TEXT PRIMARY KEY,
                    citizen_id TEXT,
                    title TEXT NOT NULL,
                    last_preview TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(citizen_id) REFERENCES citizens(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS chat_messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source TEXT,
                    citations_json TEXT,
                    options_json TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS user_appointments (
                    id TEXT PRIMARY KEY,
                    citizen_id TEXT NOT NULL,
                    titulo TEXT NOT NULL,
                    data_evento TEXT NOT NULL,
                    horario TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    unidade_saude TEXT,
                    status TEXT NOT NULL DEFAULT 'agendado',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(citizen_id) REFERENCES citizens(id) ON DELETE CASCADE
                );
            """)

    def register_citizen(self, req: CitizenRegisterRequest) -> CitizenProfileResponse:
        cid = str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._lock, self._get_connection() as conn:
            # Verifica duplicidade de CPF
            cur = conn.cursor()
            cur.execute("SELECT id FROM citizens WHERE cpf = ?", (req.cpf,))
            if cur.fetchone():
                raise ValueError("Cidadão já cadastrado com este CPF.")
            if req.cns:
                cur.execute("SELECT id FROM citizens WHERE cns = ?", (req.cns,))
                if cur.fetchone():
                    raise ValueError("Cidadão já cadastrado com este Cartão Nacional de Saúde (CNS).")

            conn.execute(
                """
                INSERT INTO citizens (
                    id, cpf, cns, nome_completo, data_nascimento, sexo_biologico,
                    gestante, ra_residencia, bairro_ou_setor, telefone, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    cid,
                    req.cpf,
                    req.cns,
                    req.nome_completo,
                    req.data_nascimento,
                    req.sexo_biologico,
                    1 if req.gestante else 0,
                    req.ra_residencia,
                    req.bairro_ou_setor,
                    req.telefone,
                    now_iso,
                ),
            )
        return self.get_citizen_by_id(cid)

    def login_citizen(self, cpf_or_cns: str, data_nasc: str) -> Optional[CitizenProfileResponse]:
        clean = "".join(filter(str.isdigit, cpf_or_cns))
        with self._lock, self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id FROM citizens 
                WHERE (cpf = ? OR cns = ?) AND data_nascimento = ?
                """,
                (clean, clean, data_nasc),
            )
            row = cur.fetchone()
            if row:
                return self.get_citizen_by_id(row["id"])
        return None

    def get_citizen_by_id(self, cid: str) -> Optional[CitizenProfileResponse]:
        with self._lock, self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM citizens WHERE id = ?", (cid,))
            row = cur.fetchone()
            if not row:
                return None
            
            cpf = row["cpf"]
            cns = row["cns"]
            cpf_mask = f"***.{cpf[3:6]}.{cpf[6:9]}-**" if len(cpf) == 11 else cpf
            cns_mask = f"*** **** **** {cns[-4:]}" if cns and len(cns) == 15 else cns
            idade, faixa = _calc_idade(row["data_nascimento"])
            primeiro_nome = row["nome_completo"].split()[0].title()

            return CitizenProfileResponse(
                id=row["id"],
                nome_completo=row["nome_completo"].title(),
                primeiro_nome=primeiro_nome,
                cpf_mascarado=cpf_mask,
                cns_mascarado=cns_mask,
                data_nascimento=row["data_nascimento"],
                idade_anos=idade,
                faixa_etaria=faixa,
                sexo_biologico=row["sexo_biologico"],
                gestante=bool(row["gestante"]),
                ra_residencia=row["ra_residencia"],
                ra_display=_format_ra_display(row["ra_residencia"]),
                bairro_ou_setor=row["bairro_ou_setor"],
                telefone=row["telefone"],
                created_at=row["created_at"],
            )

    def update_citizen(self, cid: str, req: CitizenUpdateRequest) -> Optional[CitizenProfileResponse]:
        fields = []
        vals = []
        if req.ra_residencia is not None:
            fields.append("ra_residencia = ?")
            vals.append(req.ra_residencia)
        if req.gestante is not None:
            fields.append("gestante = ?")
            vals.append(1 if req.gestante else 0)
        if req.bairro_ou_setor is not None:
            fields.append("bairro_ou_setor = ?")
            vals.append(req.bairro_ou_setor)
        if req.telefone is not None:
            fields.append("telefone = ?")
            vals.append(req.telefone)

        if not fields:
            return self.get_citizen_by_id(cid)

        vals.append(cid)
        with self._lock, self._get_connection() as conn:
            conn.execute(f"UPDATE citizens SET {', '.join(fields)} WHERE id = ?", vals)
        return self.get_citizen_by_id(cid)

    def get_first_or_demo_citizen(self) -> Optional[CitizenProfileResponse]:
        with self._lock, self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM citizens ORDER BY created_at ASC LIMIT 1")
            row = cur.fetchone()
            if row:
                return self.get_citizen_by_id(row["id"])
        return None


_citizen_storage_singleton: Optional[CitizenStorage] = None


def get_citizen_storage() -> CitizenStorage:
    global _citizen_storage_singleton
    if _citizen_storage_singleton is None:
        _citizen_storage_singleton = CitizenStorage()
    return _citizen_storage_singleton

