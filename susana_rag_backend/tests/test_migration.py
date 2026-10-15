"""Migração do schema v1 (sem senha) para v2."""
from __future__ import annotations

import sqlite3

from app.citizen.storage import CitizenStorage

V1_SCHEMA = """
CREATE TABLE citizens (
    id TEXT PRIMARY KEY, cpf TEXT UNIQUE NOT NULL, cns TEXT UNIQUE, nome_completo TEXT NOT NULL,
    data_nascimento TEXT NOT NULL, sexo_biologico TEXT NOT NULL, gestante INTEGER NOT NULL DEFAULT 0,
    ra_residencia TEXT NOT NULL, bairro_ou_setor TEXT, telefone TEXT, created_at TEXT NOT NULL);
CREATE TABLE chat_sessions (id TEXT PRIMARY KEY, citizen_id TEXT, title TEXT NOT NULL, last_preview TEXT,
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE chat_messages (id TEXT PRIMARY KEY, session_id TEXT NOT NULL, role TEXT NOT NULL, content TEXT NOT NULL,
    source TEXT, citations_json TEXT, options_json TEXT, created_at TEXT NOT NULL);
CREATE TABLE user_appointments (id TEXT PRIMARY KEY, citizen_id TEXT NOT NULL, titulo TEXT NOT NULL,
    data_evento TEXT NOT NULL, horario TEXT NOT NULL, tipo TEXT NOT NULL, unidade_saude TEXT,
    status TEXT NOT NULL DEFAULT 'agendado', created_at TEXT NOT NULL);
INSERT INTO citizens VALUES ('c1', '05481729199', NULL, 'Juliana', '1994-05-18', 'F', 0, 'ceilandia', NULL, NULL, 'x');
INSERT INTO chat_sessions VALUES ('s1', 'c1', 'Do cadastro', '', 'x', 'x');
INSERT INTO chat_sessions VALUES ('s2', NULL, 'Anônima', '', 'x', 'x');
INSERT INTO chat_messages VALUES ('m1', 's1', 'user', 'oi', NULL, NULL, NULL, 'x');
"""


def _tables(conn):
    return {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def test_v1_database_is_migrated_and_idempotent(tmp_path):
    db = tmp_path / "v1.db"
    with sqlite3.connect(db) as conn:
        conn.executescript(V1_SCHEMA)

    CitizenStorage(db_path=db)
    CitizenStorage(db_path=db)  # segunda abertura não deve falhar nem apagar nada novo

    with sqlite3.connect(db) as conn:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(citizens)")}
        assert {"password_hash", "condicoes_json", "updated_at"} <= cols
        tables = _tables(conn)
        assert {"auth_sessions", "agenda_events", "vaccine_records", "agenda_proposals", "schema_meta"} <= tables
        assert "user_appointments" not in tables
        assert conn.execute("SELECT COUNT(*) FROM citizens").fetchone()[0] == 0
        sessions = [r[0] for r in conn.execute("SELECT id FROM chat_sessions")]
        assert sessions == ["s2"]
        assert conn.execute("SELECT value FROM schema_meta WHERE key='schema_version'").fetchone()[0] == "2"
