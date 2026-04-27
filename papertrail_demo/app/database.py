from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "papertrail.db"
SEED_PATH = Path(__file__).resolve().parent.parent / "sample_data" / "seed.json"


def connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(reset: bool = False, db_path: Path = DB_PATH) -> None:
    if reset and db_path.exists():
        db_path.unlink()
    conn = connect(db_path)
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                display_name TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                owner TEXT NOT NULL,
                filename TEXT NOT NULL,
                content TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
            );

            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor TEXT NOT NULL,
                action TEXT NOT NULL,
                detail TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        if not conn.execute("SELECT 1 FROM users LIMIT 1").fetchone():
            seed(conn)
        conn.commit()
    finally:
        conn.close()


def seed(conn: sqlite3.Connection) -> None:
    data = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    for user in data["users"]:
        conn.execute(
            "INSERT INTO users (username, password, role, display_name) VALUES (?, ?, ?, ?)",
            (user["username"], user["password"], user["role"], user["display_name"]),
        )
    for document in data["documents"]:
        conn.execute(
            "INSERT INTO documents (title, owner, filename, content, status) VALUES (?, ?, ?, ?, ?)",
            (document["title"], document["owner"], document["filename"], document["content"], document["status"]),
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    init_db(reset=args.reset)
    print(f"initialized {DB_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
