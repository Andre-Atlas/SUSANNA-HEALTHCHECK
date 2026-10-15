"""
Sessões de autenticação (token opaco Bearer) e dependências FastAPI
===================================================================
- "Lembrar de mim": sessão de 30 dias, renovada a cada uso (janela deslizante).
- Sem "lembrar": sessão de 24 horas.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, Tuple

from fastapi import Depends, Header, HTTPException

from app.citizen.schemas import CitizenProfileResponse
from app.citizen.security import new_token, token_hash
from app.citizen.storage import CitizenStorage, _now, get_citizen_storage
from app.config import get_settings


class AuthStorage:
    def __init__(self, citizen_storage: Optional[CitizenStorage] = None):
        self.storage = citizen_storage or get_citizen_storage()
        self.purge_expired()

    def _ttl(self, remember: bool) -> timedelta:
        s = get_settings()
        if remember:
            return timedelta(days=s.auth_session_days_remember)
        return timedelta(hours=s.auth_session_hours_default)

    def create_session(self, citizen_id: str, remember: bool, user_agent: Optional[str] = None) -> Tuple[str, str]:
        token = new_token()
        now = _now()
        expires = (now + self._ttl(remember)).isoformat()
        with self.storage._lock, self.storage._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO auth_sessions (token_hash, citizen_id, remember, created_at, expires_at, last_seen_at, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (token_hash(token), citizen_id, 1 if remember else 0, now.isoformat(), expires, now.isoformat(), (user_agent or "")[:200]),
            )
        return token, expires

    def resolve(self, token: str) -> Optional[str]:
        th = token_hash(token)
        now = _now()
        with self.storage._lock, self.storage._get_connection() as conn:
            row = conn.execute(
                "SELECT citizen_id, remember, expires_at FROM auth_sessions WHERE token_hash = ?", (th,)
            ).fetchone()
            if not row:
                return None
            if datetime.fromisoformat(row["expires_at"]) <= now:
                conn.execute("DELETE FROM auth_sessions WHERE token_hash = ?", (th,))
                return None
            if row["remember"]:
                new_exp = (now + self._ttl(True)).isoformat()
                conn.execute(
                    "UPDATE auth_sessions SET last_seen_at = ?, expires_at = ? WHERE token_hash = ?",
                    (now.isoformat(), new_exp, th),
                )
            else:
                conn.execute("UPDATE auth_sessions SET last_seen_at = ? WHERE token_hash = ?", (now.isoformat(), th))
            return row["citizen_id"]

    def revoke(self, token: str) -> None:
        with self.storage._lock, self.storage._get_connection() as conn:
            conn.execute("DELETE FROM auth_sessions WHERE token_hash = ?", (token_hash(token),))

    def revoke_all(self, citizen_id: str, except_token: Optional[str] = None) -> None:
        with self.storage._lock, self.storage._get_connection() as conn:
            if except_token:
                conn.execute(
                    "DELETE FROM auth_sessions WHERE citizen_id = ? AND token_hash != ?",
                    (citizen_id, token_hash(except_token)),
                )
            else:
                conn.execute("DELETE FROM auth_sessions WHERE citizen_id = ?", (citizen_id,))

    def purge_expired(self) -> None:
        with self.storage._lock, self.storage._get_connection() as conn:
            conn.execute("DELETE FROM auth_sessions WHERE expires_at <= ?", (_now().isoformat(),))


_auth_storage: Optional[AuthStorage] = None


def get_auth_storage() -> AuthStorage:
    global _auth_storage
    if _auth_storage is None:
        _auth_storage = AuthStorage()
    return _auth_storage


def get_bearer_token(authorization: Optional[str] = Header(None)) -> Optional[str]:
    if not authorization:
        return None
    scheme, _, value = authorization.partition(" ")
    if scheme.lower() != "bearer" or not value.strip():
        return None
    return value.strip()


def get_current_citizen_optional(
    token: Optional[str] = Depends(get_bearer_token),
    auth: AuthStorage = Depends(get_auth_storage),
    storage: CitizenStorage = Depends(get_citizen_storage),
) -> Optional[CitizenProfileResponse]:
    if not token:
        return None
    cid = auth.resolve(token)
    if not cid:
        return None
    return storage.get_citizen_by_id(cid)


def get_current_citizen(
    citizen: Optional[CitizenProfileResponse] = Depends(get_current_citizen_optional),
) -> CitizenProfileResponse:
    if citizen is None:
        raise HTTPException(
            status_code=401,
            detail="Sessão expirada ou ausente. Entre novamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return citizen
