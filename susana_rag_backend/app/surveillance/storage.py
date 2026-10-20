"""
Armazenamento Relacional SQLite (susana_app.db) para Vigilância Epidemiológica
================================================================================
Thread-safe (RLock), modo WAL, sem bloqueio de event loop.
"""
from __future__ import annotations

import json
import logging
import sqlite3
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.surveillance.official_data import CATEGORIES_DATA, CONDITIONS_DATA
from app.surveillance.schemas import (
    GuidelineItem,
    RegionCaseDistribution,
    SurveillanceCategory,
    SurveillanceCondition,
    TimeSeriesPoint,
    UnidadeReferenciaItem,
)

logger = logging.getLogger("susana.surveillance.storage")


class SurveillanceStorage:
    """Gerencia a persistência das tabelas de monitoramento epidemiológico."""

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            from app.config import get_settings

            self.db_path = Path(get_settings().app_db_path)
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

    def _init_db(self) -> None:
        with self._lock, self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS surveillance_categories (
                    id TEXT PRIMARY KEY,
                    nome TEXT NOT NULL,
                    slug TEXT UNIQUE NOT NULL,
                    icone TEXT NOT NULL,
                    descricao TEXT NOT NULL,
                    cor_badge TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS surveillance_conditions (
                    id TEXT PRIMARY KEY,
                    category_id TEXT NOT NULL,
                    nome TEXT NOT NULL,
                    codigo_cid10 TEXT NOT NULL,
                    tipo_agravo TEXT NOT NULL,
                    descricao TEXT NOT NULL,
                    nivel_alerta TEXT NOT NULL,
                    sazonalidade TEXT NOT NULL,
                    vetor_ou_transmissao TEXT NOT NULL,
                    taxa_incidencia_100k REAL NOT NULL,
                    total_casos_ano INTEGER NOT NULL,
                    variacao_semanal_pct REAL NOT NULL,
                    faixa_etaria_predominante TEXT NOT NULL,
                    obitos_confirmados INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY(category_id) REFERENCES surveillance_categories(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS surveillance_time_series (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    condition_id TEXT NOT NULL,
                    semana_epidemio TEXT NOT NULL,
                    numero_semana INTEGER NOT NULL,
                    rotulo TEXT NOT NULL,
                    casos INTEGER NOT NULL,
                    taxa_movel REAL NOT NULL,
                    status TEXT NOT NULL,
                    FOREIGN KEY(condition_id) REFERENCES surveillance_conditions(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS surveillance_regions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    condition_id TEXT NOT NULL,
                    ra_id TEXT NOT NULL,
                    ra_nome TEXT NOT NULL,
                    casos INTEGER NOT NULL,
                    taxa_incidencia_100k REAL NOT NULL,
                    percentual REAL NOT NULL,
                    risco TEXT NOT NULL,
                    FOREIGN KEY(condition_id) REFERENCES surveillance_conditions(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS surveillance_guidelines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    condition_id TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    titulo TEXT NOT NULL,
                    descricao TEXT NOT NULL,
                    severidade TEXT NOT NULL,
                    FOREIGN KEY(condition_id) REFERENCES surveillance_conditions(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS surveillance_referrals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    condition_id TEXT NOT NULL,
                    tipo_servico TEXT NOT NULL,
                    nome_exemplo TEXT NOT NULL,
                    papel_clinico TEXT NOT NULL,
                    endereco_resumo TEXT NOT NULL,
                    FOREIGN KEY(condition_id) REFERENCES surveillance_conditions(id) ON DELETE CASCADE
                );

                -- Índices de alta performance
                CREATE INDEX IF NOT EXISTS idx_cond_cat ON surveillance_conditions(category_id);
                CREATE INDEX IF NOT EXISTS idx_ts_cond ON surveillance_time_series(condition_id, numero_semana);
                CREATE INDEX IF NOT EXISTS idx_reg_cond ON surveillance_regions(condition_id);
                CREATE INDEX IF NOT EXISTS idx_guide_cond ON surveillance_guidelines(condition_id);
                CREATE INDEX IF NOT EXISTS idx_ref_cond ON surveillance_referrals(condition_id);
            """)

            # Carga inicial idempotente
            self._seed_data(conn)

    def _seed_data(self, conn: sqlite3.Connection) -> None:
        """Popula tabelas com dados oficiais caso ainda não existam."""
        cur = conn.cursor()

        for cat in CATEGORIES_DATA:
            cur.execute(
                """
                INSERT INTO surveillance_categories (id, nome, slug, icone, descricao, cor_badge)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    nome=excluded.nome,
                    descricao=excluded.descricao,
                    cor_badge=excluded.cor_badge
                """,
                (cat["id"], cat["nome"], cat["slug"], cat["icone"], cat["descricao"], cat["cor_badge"]),
            )

        for cond in CONDITIONS_DATA:
            cur.execute(
                """
                INSERT INTO surveillance_conditions (
                    id, category_id, nome, codigo_cid10, tipo_agravo, descricao,
                    nivel_alerta, sazonalidade, vetor_ou_transmissao, taxa_incidencia_100k,
                    total_casos_ano, variacao_semanal_pct, faixa_etaria_predominante, obitos_confirmados
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    nome=excluded.nome,
                    codigo_cid10=excluded.codigo_cid10,
                    tipo_agravo=excluded.tipo_agravo,
                    descricao=excluded.descricao,
                    nivel_alerta=excluded.nivel_alerta,
                    taxa_incidencia_100k=excluded.taxa_incidencia_100k,
                    total_casos_ano=excluded.total_casos_ano,
                    variacao_semanal_pct=excluded.variacao_semanal_pct,
                    obitos_confirmados=excluded.obitos_confirmados
                """,
                (
                    cond["id"],
                    cond["category_id"],
                    cond["nome"],
                    cond["codigo_cid10"],
                    cond["tipo_agravo"],
                    cond["descricao"],
                    cond["nivel_alerta"],
                    cond["sazonalidade"],
                    cond["vetor_ou_transmissao"],
                    cond["taxa_incidencia_100k"],
                    cond["total_casos_ano"],
                    cond["variacao_semanal_pct"],
                    cond["faixa_etaria_predominante"],
                    cond.get("obitos_confirmados", 0),
                ),
            )

            # Séries temporais (limpa e recria para garantir consistência)
            cur.execute("DELETE FROM surveillance_time_series WHERE condition_id = ?", (cond["id"],))
            for ts in cond.get("time_series", []):
                cur.execute(
                    """
                    INSERT INTO surveillance_time_series (condition_id, semana_epidemio, numero_semana, rotulo, casos, taxa_movel, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (cond["id"], ts["semana"], ts["num"], ts["rotulo"], ts["casos"], ts["taxa_movel"], ts["status"]),
                )

            # Regiões
            cur.execute("DELETE FROM surveillance_regions WHERE condition_id = ?", (cond["id"],))
            for reg in cond.get("regions", []):
                cur.execute(
                    """
                    INSERT INTO surveillance_regions (condition_id, ra_id, ra_nome, casos, taxa_incidencia_100k, percentual, risco)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (cond["id"], reg["ra_id"], reg["ra_nome"], reg["casos"], reg["taxa_incidencia_100k"], reg["percentual"], reg["risco"]),
                )

            # Guidelines
            cur.execute("DELETE FROM surveillance_guidelines WHERE condition_id = ?", (cond["id"],))
            for g in cond.get("guidelines", []):
                cur.execute(
                    """
                    INSERT INTO surveillance_guidelines (condition_id, tipo, titulo, descricao, severidade)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (cond["id"], g["tipo"], g["titulo"], g["descricao"], g.get("severidade", "moderada")),
                )

            # Unidades de referência
            cur.execute("DELETE FROM surveillance_referrals WHERE condition_id = ?", (cond["id"],))
            for ref in cond.get("unidades_referencia", []):
                cur.execute(
                    """
                    INSERT INTO surveillance_referrals (condition_id, tipo_servico, nome_exemplo, papel_clinico, endereco_resumo)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (cond["id"], ref["tipo_servico"], ref["nome_exemplo"], ref["papel_clinico"], ref["endereco_resumo"]),
                )

        conn.commit()
        logger.info("Base de Vigilância Epidemiológica do DF inicializada com sucesso.")

    def list_categories(self) -> List[SurveillanceCategory]:
        with self._lock, self._get_connection() as conn:
            rows = conn.execute("""
                SELECT c.id, c.nome, c.slug, c.icone, c.descricao, c.cor_badge,
                       COUNT(cd.id) as total_agravos
                FROM surveillance_categories c
                LEFT JOIN surveillance_conditions cd ON cd.category_id = c.id
                GROUP BY c.id
                ORDER BY c.rowid ASC
            """).fetchall()

            return [
                SurveillanceCategory(
                    id=r["id"],
                    nome=r["nome"],
                    slug=r["slug"],
                    icone=r["icone"],
                    descricao=r["descricao"],
                    cor_badge=r["cor_badge"],
                    total_agravos=r["total_agravos"],
                )
                for r in rows
            ]

    def list_conditions(self, category_id: Optional[str] = None) -> List[SurveillanceCondition]:
        with self._lock, self._get_connection() as conn:
            if category_id:
                rows = conn.execute(
                    "SELECT * FROM surveillance_conditions WHERE category_id = ? ORDER BY total_casos_ano DESC",
                    (category_id,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM surveillance_conditions ORDER BY total_casos_ano DESC"
                ).fetchall()

            return [
                SurveillanceCondition(
                    id=r["id"],
                    category_id=r["category_id"],
                    nome=r["nome"],
                    codigo_cid10=r["codigo_cid10"],
                    tipo_agravo=r["tipo_agravo"],
                    descricao=r["descricao"],
                    nivel_alerta=r["nivel_alerta"],
                    sazonalidade=r["sazonalidade"],
                    vetor_ou_transmissao=r["vetor_ou_transmissao"],
                    taxa_incidencia_100k=r["taxa_incidencia_100k"],
                    total_casos_ano=r["total_casos_ano"],
                    variacao_semanal_pct=r["variacao_semanal_pct"],
                    faixa_etaria_predominante=r["faixa_etaria_predominante"],
                )
                for r in rows
            ]

    def get_condition(self, condition_id: str) -> Optional[Dict[str, Any]]:
        with self._lock, self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM surveillance_conditions WHERE id = ?",
                (condition_id,),
            ).fetchone()
            if not row:
                return None

            cond_dict = dict(row)

            # Série temporal
            ts_rows = conn.execute(
                "SELECT * FROM surveillance_time_series WHERE condition_id = ? ORDER BY numero_semana ASC",
                (condition_id,),
            ).fetchall()
            cond_dict["time_series"] = [
                TimeSeriesPoint(
                    semana_epidemio=t["semana_epidemio"],
                    numero_semana=t["numero_semana"],
                    rotulo=t["rotulo"],
                    casos=t["casos"],
                    taxa_movel=t["taxa_movel"],
                    status=t["status"],
                )
                for t in ts_rows
            ]

            # Regiões
            reg_rows = conn.execute(
                "SELECT * FROM surveillance_regions WHERE condition_id = ? ORDER BY casos DESC",
                (condition_id,),
            ).fetchall()
            cond_dict["regions"] = [
                RegionCaseDistribution(
                    ra_id=rg["ra_id"],
                    ra_nome=rg["ra_nome"],
                    casos=rg["casos"],
                    taxa_incidencia_100k=rg["taxa_incidencia_100k"],
                    percentual_distrital=rg["percentual"],
                    nivel_risco=rg["risco"],
                )
                for rg in reg_rows
            ]

            # Guidelines
            guide_rows = conn.execute(
                "SELECT * FROM surveillance_guidelines WHERE condition_id = ?",
                (condition_id,),
            ).fetchall()
            cond_dict["guidelines"] = [
                GuidelineItem(
                    tipo=g["tipo"],
                    titulo=g["titulo"],
                    descricao=g["descricao"],
                    severidade=g["severidade"],
                )
                for g in guide_rows
            ]

            # Referências
            ref_rows = conn.execute(
                "SELECT * FROM surveillance_referrals WHERE condition_id = ?",
                (condition_id,),
            ).fetchall()
            cond_dict["unidades_referencia"] = [
                UnidadeReferenciaItem(
                    tipo_servico=rf["tipo_servico"],
                    nome_exemplo=rf["nome_exemplo"],
                    papel_clinico=rf["papel_clinico"],
                    endereco_resumo=rf["endereco_resumo"],
                )
                for rf in ref_rows
            ]

            return cond_dict
