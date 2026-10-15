"""
Primitivas de segurança do cadastro (somente stdlib)
====================================================
- Hash de senha PBKDF2-HMAC-SHA256 com salt aleatório (o Python do projeto é
  compilado com LibreSSL, sem ``hashlib.scrypt``).
- Tokens opacos de sessão: o cliente recebe o token, o banco guarda só o SHA-256.
- Limitador de tentativas de login em memória (processo único).
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import re
import secrets
import threading
import time
from typing import Dict, List

PBKDF2_ITERATIONS = 600_000
_SCHEME = "pbkdf2_sha256"


def _b64(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def hash_password(password: str, iterations: int = PBKDF2_ITERATIONS) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"{_SCHEME}${iterations}${_b64(salt)}${_b64(digest)}"


def verify_password(password: str, stored: str | None) -> bool:
    if not stored:
        return False
    try:
        scheme, iters, salt_b64, hash_b64 = stored.split("$")
        if scheme != _SCHEME:
            return False
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(hash_b64)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iters))
        return hmac.compare_digest(digest, expected)
    except (ValueError, TypeError):
        return False


def check_password_policy(password: str) -> str:
    """Valida a política mínima (8+ caracteres, com letra e número)."""
    if len(password) < 8 or len(password) > 128:
        raise ValueError("A senha deve ter entre 8 e 128 caracteres.")
    if not re.search(r"[A-Za-zÀ-ÿ]", password) or not re.search(r"\d", password):
        raise ValueError("A senha deve conter pelo menos uma letra e um número.")
    return password


def new_token() -> str:
    return secrets.token_urlsafe(32)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class LoginRateLimiter:
    """Bloqueia uma chave (CPF ou IP) após ``max_failures`` falhas na janela."""

    def __init__(self, max_failures: int = 5, window_s: int = 600):
        self.max_failures = max_failures
        self.window_s = window_s
        self._failures: Dict[str, List[float]] = {}
        self._lock = threading.Lock()

    def _recent(self, key: str, now: float) -> List[float]:
        return [t for t in self._failures.get(key, []) if now - t < self.window_s]

    def is_blocked(self, *keys: str) -> bool:
        now = time.monotonic()
        with self._lock:
            return any(len(self._recent(k, now)) >= self.max_failures for k in keys if k)

    def register_failure(self, *keys: str) -> None:
        now = time.monotonic()
        with self._lock:
            for k in keys:
                if k:
                    self._failures[k] = self._recent(k, now) + [now]

    def reset(self, *keys: str) -> None:
        with self._lock:
            for k in keys:
                self._failures.pop(k, None)


login_rate_limiter = LoginRateLimiter()
