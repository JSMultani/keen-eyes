from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: int
    username: str
    password: str
    role: str
    display_name: str


@dataclass(frozen=True)
class Document:
    id: int
    title: str
    owner: str
    filename: str
    content: str
    status: str


@dataclass(frozen=True)
class AuditEvent:
    id: int
    actor: str
    action: str
    detail: str
    created_at: str

