"""Gerenciador de Sessões e Histórico de Chat no SQLite."""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from app.chat_sessions.schemas import (
    ChatMessageItem,
    ChatSessionSummary,
    CreateSessionRequest,
    SaveMessageRequest,
)
from app.citizen.storage import CitizenStorage, get_citizen_storage

logger = logging.getLogger("susana.chat_sessions.storage")


class ChatSessionStorage:
    def __init__(self, citizen_storage: Optional[CitizenStorage] = None):
        self.storage = citizen_storage or get_citizen_storage()

    def create_session(self, req: CreateSessionRequest) -> ChatSessionSummary:
        sid = str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).isoformat()
        title = req.title.strip() if req.title else "Nova conversa"
        with self.storage._lock, self.storage._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO chat_sessions (id, citizen_id, title, last_preview, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (sid, req.citizen_id, title, "", now_iso, now_iso),
            )
        return ChatSessionSummary(
            id=sid,
            citizen_id=req.citizen_id,
            title=title,
            last_preview="",
            created_at=now_iso,
            updated_at=now_iso,
            message_count=0,
        )

    def list_sessions(self, citizen_id: Optional[str] = None) -> List[ChatSessionSummary]:
        with self.storage._lock, self.storage._get_connection() as conn:
            cur = conn.cursor()
            if citizen_id:
                cur.execute(
                    """
                    SELECT s.*, COUNT(m.id) as msg_count 
                    FROM chat_sessions s
                    LEFT JOIN chat_messages m ON s.id = m.session_id
                    WHERE s.citizen_id = ? OR s.citizen_id IS NULL
                    GROUP BY s.id
                    ORDER BY s.updated_at DESC
                    LIMIT 50
                    """,
                    (citizen_id,),
                )
            else:
                cur.execute(
                    """
                    SELECT s.*, COUNT(m.id) as msg_count 
                    FROM chat_sessions s
                    LEFT JOIN chat_messages m ON s.id = m.session_id
                    GROUP BY s.id
                    ORDER BY s.updated_at DESC
                    LIMIT 50
                    """
                )
            rows = cur.fetchall()
            return [
                ChatSessionSummary(
                    id=r["id"],
                    citizen_id=r["citizen_id"],
                    title=r["title"],
                    last_preview=r["last_preview"],
                    created_at=r["created_at"],
                    updated_at=r["updated_at"],
                    message_count=r["msg_count"],
                )
                for r in rows
            ]

    def get_messages(self, session_id: str) -> List[ChatMessageItem]:
        with self.storage._lock, self.storage._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT * FROM chat_messages 
                WHERE session_id = ? 
                ORDER BY created_at ASC
                """,
                (session_id,),
            )
            rows = cur.fetchall()
            result = []
            for r in rows:
                citations = json.loads(r["citations_json"]) if r["citations_json"] else []
                options = json.loads(r["options_json"]) if r["options_json"] else []
                result.append(
                    ChatMessageItem(
                        id=r["id"],
                        session_id=r["session_id"],
                        role=r["role"],
                        content=r["content"],
                        source=r["source"],
                        citations=citations,
                        options=options,
                        created_at=r["created_at"],
                    )
                )
            return result

    def save_message(self, req: SaveMessageRequest) -> ChatMessageItem:
        mid = str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).isoformat()
        cit_json = json.dumps(req.citations) if req.citations else None
        opt_json = json.dumps(req.options) if req.options else None
        preview = req.content[:100].replace("\n", " ")

        with self.storage._lock, self.storage._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO chat_messages (id, session_id, role, content, source, citations_json, options_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (mid, req.session_id, req.role, req.content, req.source, cit_json, opt_json, now_iso),
            )
            # Atualiza o preview e updated_at da sessão
            # Se for a primeira mensagem do usuário e o título for "Nova conversa", atualiza o título
            cur = conn.cursor()
            cur.execute("SELECT COUNT(id) as cnt FROM chat_messages WHERE session_id = ?", (req.session_id,))
            cnt_row = cur.fetchone()
            msg_cnt = cnt_row["cnt"] if cnt_row else 1

            cur.execute("SELECT title FROM chat_sessions WHERE id = ?", (req.session_id,))
            sess_row = cur.fetchone()
            current_title = sess_row["title"] if sess_row else ""

            new_title = None
            if req.role == "user" and msg_cnt <= 2 and current_title in ("Nova conversa", ""):
                # Gera título resumido
                new_title = req.content[:35] + ("..." if len(req.content) > 35 else "")

            if new_title:
                conn.execute(
                    """
                    UPDATE chat_sessions 
                    SET title = ?, last_preview = ?, updated_at = ? 
                    WHERE id = ?
                    """,
                    (new_title, preview, now_iso, req.session_id),
                )
            else:
                conn.execute(
                    """
                    UPDATE chat_sessions 
                    SET last_preview = ?, updated_at = ? 
                    WHERE id = ?
                    """,
                    (preview, now_iso, req.session_id),
                )

        return ChatMessageItem(
            id=mid,
            session_id=req.session_id,
            role=req.role,
            content=req.content,
            source=req.source,
            citations=req.citations,
            options=req.options,
            created_at=now_iso,
        )

    def delete_session(self, session_id: str) -> bool:
        with self.storage._lock, self.storage._get_connection() as conn:
            conn.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
            res = conn.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
            return res.rowcount > 0
