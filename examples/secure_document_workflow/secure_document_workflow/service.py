from __future__ import annotations

import re
import secrets
from dataclasses import dataclass, field
from datetime import UTC, datetime


class AuthorizationError(Exception):
    pass


class ValidationError(Exception):
    pass


@dataclass(frozen=True)
class User:
    username: str
    role: str


@dataclass
class Document:
    id: int
    owner: str
    filename: str
    content: bytes
    approved: bool = False


@dataclass
class AuditEvent:
    event: str
    actor: str
    detail: str
    created_at: str = field(default_factory=lambda: datetime.now(UTC).replace(microsecond=0).isoformat())


class DocumentWorkflow:
    SAFE_FILENAME = re.compile(r"^[A-Za-z0-9._-]{1,120}$")

    def __init__(self, users: dict[str, tuple[str, str]]) -> None:
        self._users = users
        self._sessions: dict[str, User] = {}
        self._documents: dict[int, Document] = {}
        self._audit: list[AuditEvent] = []
        self._next_id = 1

    @classmethod
    def demo(cls) -> "DocumentWorkflow":
        return cls(
            {
                "author": ("correct horse battery staple", "author"),
                "approver": ("correct horse battery staple", "approver"),
                "admin": ("correct horse battery staple", "admin"),
                "reader": ("correct horse battery staple", "reader"),
            }
        )

    def login(self, username: str, password: str) -> str:
        expected = self._users.get(username)
        if expected is None or not secrets.compare_digest(expected[0], password):
            self._record("login_failed", username, "invalid credentials")
            raise AuthorizationError("invalid credentials")
        token = secrets.token_urlsafe(24)
        self._sessions[token] = User(username, expected[1])
        self._record("login", username, "success")
        return token

    def upload(self, token: str, filename: str, content: bytes) -> int:
        user = self._require(token, {"author", "admin"})
        self._validate_filename(filename)
        if not content:
            raise ValidationError("document content is required")
        doc_id = self._next_id
        self._next_id += 1
        self._documents[doc_id] = Document(doc_id, user.username, filename, content)
        self._record("upload", user.username, f"document:{doc_id}")
        return doc_id

    def approve(self, token: str, document_id: int) -> None:
        user = self._require(token, {"approver", "admin"})
        document = self._documents[document_id]
        document.approved = True
        self._record("approve", user.username, f"document:{document_id}")

    def download(self, token: str, document_id: int) -> bytes:
        user = self._require(token, {"author", "approver", "admin", "reader"})
        document = self._documents[document_id]
        allowed = user.role in {"admin", "approver"} or user.username == document.owner or document.approved
        if not allowed:
            self._record("unauthorized_download", user.username, f"document:{document_id}")
            raise AuthorizationError("not authorized for document")
        self._record("download", user.username, f"document:{document_id}")
        return document.content

    def list_documents(self, token_or_username: str) -> list[dict[str, object]]:
        user = self._user_from_token_or_name(token_or_username)
        visible = []
        for document in self._documents.values():
            if user.role in {"admin", "approver"} or user.username == document.owner or document.approved:
                visible.append({"id": document.id, "filename": document.filename, "approved": document.approved})
        return visible

    def audit_log(self, token: str) -> list[AuditEvent]:
        self._require(token, {"admin"})
        return list(self._audit)

    def _require(self, token: str, roles: set[str]) -> User:
        user = self._sessions.get(token)
        if user is None:
            self._record("auth_failed", "anonymous", "missing or invalid session")
            raise AuthorizationError("authentication required")
        if user.role not in roles:
            self._record("authz_failed", user.username, f"role:{user.role}")
            raise AuthorizationError("insufficient role")
        return user

    def _user_from_token_or_name(self, token_or_username: str) -> User:
        if token_or_username in self._sessions:
            return self._sessions[token_or_username]
        if token_or_username in self._users:
            return User(token_or_username, self._users[token_or_username][1])
        raise AuthorizationError("unknown user")

    def _validate_filename(self, filename: str) -> None:
        if not self.SAFE_FILENAME.fullmatch(filename) or ".." in filename:
            raise ValidationError("unsafe filename")

    def _record(self, event: str, actor: str, detail: str) -> None:
        redacted = re.sub(r"(?i)(password|token|secret)=[^ ]+", r"\1=<redacted>", detail)
        self._audit.append(AuditEvent(event, actor, redacted))

