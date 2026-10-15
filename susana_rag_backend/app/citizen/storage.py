"""
Armazenamento Relacional SQLite (susana_app.db) para Cidadãos, Sessões e Agenda
================================================================================
Modo WAL (Write-Ahead Logging) ativo, thread-safe, sem bloquear o event loop.

Versões do schema (tabela ``schema_meta``):
- v1: cadastro sem senha (login por CPF + data de nascimento) e ``user_appointments``.
- v2: cadastro opcional com senha, campos de perfil anuláveis, condições de saúde,
      sessões de autenticação, agenda, registros de vacina e propostas do chat.
      A migração v1 -> v2 descarta os cadastros v1 (não possuem senha e eram dados
      de demonstração) e recria ``citizens`` sem as restrições NOT NULL do perfil.
"""
from __future__ import annotations

import json
import logging
import sqlite3
import threading
import unicodedata
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

from app.citizen.schemas import (
    DEFAULT_RA,
    CitizenProfileResponse,
    CitizenRegisterRequest,
    CitizenUpdateRequest,
)
from app.citizen.security import hash_password, verify_password
from app.rag.nlu import RA_DICTIONARY

logger = logging.getLogger("susana.citizen.storage")

SCHEMA_VERSION = 2


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _calc_idade(nasc_str: Optional[str]) -> Tuple[Optional[int], Optional[str]]:
    """Calcula idade em anos e faixa etária para o PNI (None se sem data)."""
    if not nasc_str:
        return None, None
    try:
        d = datetime.strptime(nasc_str, "%Y-%m-%d").date()
    except ValueError:
        return None, None
    hoje = date.today()
    idade = max(0, hoje.year - d.year - ((hoje.month, hoje.day) < (d.month, d.day)))
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
    return idade, faixa


def _strip(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn").lower()


def _format_ra_display(ra_id: Optional[str]) -> str:
    if not ra_id or ra_id == DEFAULT_RA:
        return "Distrito Federal"
    norm = ra_id.lower().replace(" ", "_")
    for rid, aliases in RA_DICTIONARY:
        if rid == norm or norm in [a.lower().replace(" ", "_") for a in aliases]:
            # Prefere a grafia acentuada ("Ceilândia") quando o dicionário a possui
            base = _strip(aliases[0])
            accented = next((x for x in aliases if not x.isascii() and _strip(x) == base), aliases[0])
            return accented.title()
    return ra_id.title()


_CITIZENS_DDL = """
    CREATE TABLE IF NOT EXISTS citizens (
        id TEXT PRIMARY KEY,
        cpf TEXT UNIQUE NOT NULL,
        cns TEXT UNIQUE,
        nome_completo TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        data_nascimento TEXT,
        sexo_biologico TEXT,
        gestante INTEGER NOT NULL DEFAULT 0,
        condicoes_json TEXT NOT NULL DEFAULT '[]',
        ra_residencia TEXT NOT NULL DEFAULT 'geral_df',
        bairro_ou_setor TEXT,
        telefone TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT
    );
"""

_TABLES_DDL = """
    CREATE TABLE IF NOT EXISTS schema_meta (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
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

    CREATE TABLE IF NOT EXISTS auth_sessions (
        token_hash TEXT PRIMARY KEY,
        citizen_id TEXT NOT NULL,
        remember INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        last_seen_at TEXT,
        user_agent TEXT,
        FOREIGN KEY(citizen_id) REFERENCES citizens(id) ON DELETE CASCADE
    );
    CREATE INDEX IF NOT EXISTS ix_auth_citizen ON auth_sessions(citizen_id);

    CREATE TABLE IF NOT EXISTS agenda_events (
        id TEXT PRIMARY KEY,
        citizen_id TEXT NOT NULL,
        tipo TEXT NOT NULL,
        titulo TEXT NOT NULL,
        data_evento TEXT NOT NULL,
        horario TEXT,
        unidade_saude TEXT,
        unidade_id TEXT,
        notas TEXT,
        lembrete_min_antes INTEGER NOT NULL DEFAULT 60,
        recorrencia TEXT,
        status TEXT NOT NULL DEFAULT 'agendado',
        origem TEXT NOT NULL DEFAULT 'manual',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY(citizen_id) REFERENCES citizens(id) ON DELETE CASCADE
    );
    CREATE INDEX IF NOT EXISTS ix_agenda_cit_date ON agenda_events(citizen_id, data_evento);

    CREATE TABLE IF NOT EXISTS vaccine_records (
        id TEXT PRIMARY KEY,
        citizen_id TEXT NOT NULL,
        vaccine_id TEXT NOT NULL,
        dose_num INTEGER NOT NULL DEFAULT 1,
        data_aplicacao TEXT,
        created_at TEXT NOT NULL,
        UNIQUE(citizen_id, vaccine_id, dose_num),
        FOREIGN KEY(citizen_id) REFERENCES citizens(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS agenda_proposals (
        id TEXT PRIMARY KEY,
        citizen_id TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        consumed INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY(citizen_id) REFERENCES citizens(id) ON DELETE CASCADE
    );
"""


class CitizenStorage:
    """Gerencia a persistência de perfis de cidadãos e sessões no SQLite."""

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            backend_dir = Path(__file__).resolve().parent.parent.parent
            self.db_path = backend_dir / "data" / "susana_app.db"
        else:
            self.db_path = Path(db_path)
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

    # ------------------------------------------------------------------
    # Schema & migração
    # ------------------------------------------------------------------
    @staticmethod
    def _columns(conn: sqlite3.Connection, table: str) -> List[str]:
        return [r["name"] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]

    def _init_db(self) -> None:
        with self._lock, self._get_connection() as conn:
            existing = self._columns(conn, "citizens")
            if existing and "password_hash" not in existing:
                self._migrate_v1_to_v2(conn)
            conn.executescript(_CITIZENS_DDL + _TABLES_DDL)
            conn.execute("DROP TABLE IF EXISTS user_appointments")
            conn.execute(
                "INSERT OR REPLACE INTO schema_meta (key, value) VALUES ('schema_version', ?)",
                (str(SCHEMA_VERSION),),
            )

    def _migrate_v1_to_v2(self, conn: sqlite3.Connection) -> None:
        """Descarta cadastros v1 (sem senha) e o histórico vinculado a eles."""
        removed = conn.execute("SELECT COUNT(*) FROM citizens").fetchone()[0]
        conn.execute(
            "DELETE FROM chat_messages WHERE session_id IN "
            "(SELECT id FROM chat_sessions WHERE citizen_id IS NOT NULL)"
        )
        conn.execute("DELETE FROM chat_sessions WHERE citizen_id IS NOT NULL")
        conn.execute("DROP TABLE IF EXISTS user_appointments")
        conn.execute("DROP TABLE citizens")
        logger.warning(
            "Migração do cadastro v1 -> v2: %d cadastro(s) sem senha removido(s).", removed
        )

    # ------------------------------------------------------------------
    # Cidadãos
    # ------------------------------------------------------------------
    def register_citizen(self, req: CitizenRegisterRequest) -> CitizenProfileResponse:
        cid = str(uuid.uuid4())
        now_iso = _now().isoformat()
        condicoes = list(req.condicoes or [])
        if req.sexo_biologico == "M" and "gestante" in condicoes:
            condicoes.remove("gestante")
        with self._lock, self._get_connection() as conn:
            if conn.execute("SELECT 1 FROM citizens WHERE cpf = ?", (req.cpf,)).fetchone():
                raise ValueError("Já existe uma conta com este CPF.")
            if req.cns and conn.execute("SELECT 1 FROM citizens WHERE cns = ?", (req.cns,)).fetchone():
                raise ValueError("Já existe uma conta com este Cartão Nacional de Saúde (CNS).")
            conn.execute(
                """
                INSERT INTO citizens (
                    id, cpf, cns, nome_completo, password_hash, data_nascimento, sexo_biologico,
                    gestante, condicoes_json, ra_residencia, bairro_ou_setor, telefone,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    cid,
                    req.cpf,
                    req.cns,
                    req.nome_completo,
                    hash_password(req.senha),
                    req.data_nascimento,
                    req.sexo_biologico,
                    1 if "gestante" in condicoes else 0,
                    json.dumps(condicoes),
                    req.ra_residencia or DEFAULT_RA,
                    req.bairro_ou_setor,
                    req.telefone,
                    now_iso,
                    now_iso,
                ),
            )
        return self.get_citizen_by_id(cid)

    def authenticate(self, cpf: str, senha: str) -> Optional[CitizenProfileResponse]:
        with self._lock, self._get_connection() as conn:
            row = conn.execute(
                "SELECT id, password_hash FROM citizens WHERE cpf = ?", (cpf,)
            ).fetchone()
        if not row or not verify_password(senha, row["password_hash"]):
            return None
        return self.get_citizen_by_id(row["id"])

    def verify_citizen_password(self, cid: str, senha: str) -> bool:
        with self._lock, self._get_connection() as conn:
            row = conn.execute("SELECT password_hash FROM citizens WHERE id = ?", (cid,)).fetchone()
        return bool(row) and verify_password(senha, row["password_hash"])

    def set_password(self, cid: str, nova_senha: str) -> None:
        with self._lock, self._get_connection() as conn:
            conn.execute(
                "UPDATE citizens SET password_hash = ?, updated_at = ? WHERE id = ?",
                (hash_password(nova_senha), _now().isoformat(), cid),
            )

    def get_citizen_by_id(self, cid: str) -> Optional[CitizenProfileResponse]:
        with self._lock, self._get_connection() as conn:
            row = conn.execute("SELECT * FROM citizens WHERE id = ?", (cid,)).fetchone()
        if not row:
            return None
        cpf = row["cpf"]
        cns = row["cns"]
        cpf_mask = f"***.{cpf[3:6]}.{cpf[6:9]}-**" if len(cpf) == 11 else "***"
        cns_mask = f"*** **** **** {cns[-4:]}" if cns and len(cns) == 15 else None
        idade, faixa = _calc_idade(row["data_nascimento"])
        condicoes = json.loads(row["condicoes_json"] or "[]")
        ra = row["ra_residencia"] or DEFAULT_RA
        completo = bool(row["data_nascimento"] and row["sexo_biologico"] and ra != DEFAULT_RA)
        return CitizenProfileResponse(
            id=row["id"],
            nome_completo=row["nome_completo"].title(),
            primeiro_nome=row["nome_completo"].split()[0].title(),
            cpf_mascarado=cpf_mask,
            cns_mascarado=cns_mask,
            data_nascimento=row["data_nascimento"],
            idade_anos=idade,
            faixa_etaria=faixa,
            sexo_biologico=row["sexo_biologico"],
            gestante=bool(row["gestante"]),
            condicoes=condicoes,
            ra_residencia=ra,
            ra_display=_format_ra_display(ra),
            bairro_ou_setor=row["bairro_ou_setor"],
            telefone=row["telefone"],
            perfil_completo=completo,
            created_at=row["created_at"],
        )

    def update_citizen(self, cid: str, req: CitizenUpdateRequest) -> Optional[CitizenProfileResponse]:
        current = self.get_citizen_by_id(cid)
        if current is None:
            return None
        data = req.model_dump(exclude_unset=True)
        fields: List[str] = []
        vals: List[object] = []

        for col in ("nome_completo", "data_nascimento", "sexo_biologico", "bairro_ou_setor", "telefone"):
            if col in data:
                fields.append(f"{col} = ?")
                vals.append(data[col])
        if "ra_residencia" in data:
            fields.append("ra_residencia = ?")
            vals.append(data["ra_residencia"] or DEFAULT_RA)

        # Condições e flag de gestante são mantidas em sincronia
        condicoes = list(data["condicoes"]) if data.get("condicoes") is not None else list(current.condicoes)
        if data.get("gestante") is True and "gestante" not in condicoes:
            condicoes.append("gestante")
        if data.get("gestante") is False and "gestante" in condicoes:
            condicoes.remove("gestante")
        sexo = data.get("sexo_biologico", current.sexo_biologico)
        if sexo == "M" and "gestante" in condicoes:
            condicoes.remove("gestante")
        fields += ["condicoes_json = ?", "gestante = ?", "updated_at = ?"]
        vals += [json.dumps(condicoes), 1 if "gestante" in condicoes else 0, _now().isoformat()]

        vals.append(cid)
        with self._lock, self._get_connection() as conn:
            conn.execute(f"UPDATE citizens SET {', '.join(fields)} WHERE id = ?", vals)
        return self.get_citizen_by_id(cid)

    def delete_citizen(self, cid: str) -> bool:
        with self._lock, self._get_connection() as conn:
            conn.execute(
                "DELETE FROM chat_messages WHERE session_id IN (SELECT id FROM chat_sessions WHERE citizen_id = ?)",
                (cid,),
            )
            res = conn.execute("DELETE FROM citizens WHERE id = ?", (cid,))
            return res.rowcount > 0


_citizen_storage_singleton: Optional[CitizenStorage] = None


def get_citizen_storage() -> CitizenStorage:
    global _citizen_storage_singleton
    if _citizen_storage_singleton is None:
        _citizen_storage_singleton = CitizenStorage()
    return _citizen_storage_singleton
