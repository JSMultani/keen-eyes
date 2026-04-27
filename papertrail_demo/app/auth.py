from __future__ import annotations

import sqlite3
from typing import Any

from fastapi import Request


SESSION_COOKIE = "papertrail_session"


def authenticate(conn: sqlite3.Connection, username: str, password: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password),
    ).fetchone()


def current_user(conn: sqlite3.Connection, request: Request) -> sqlite3.Row | None:
    username = request.cookies.get(SESSION_COOKIE)
    if not username:
        return None
    return conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()


def has_role(user: Any, *roles: str) -> bool:
    return bool(user and user["role"] in roles)

