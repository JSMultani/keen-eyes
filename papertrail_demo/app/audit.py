from __future__ import annotations

import sqlite3


def record_event(conn: sqlite3.Connection, actor: str, action: str, detail: str) -> None:
    conn.execute(
        "INSERT INTO audit_events (actor, action, detail) VALUES (?, ?, ?)",
        (actor or "anonymous", action, detail),
    )
    conn.commit()

