from __future__ import annotations

from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .audit import record_event
from .auth import SESSION_COOKIE, authenticate, current_user, has_role
from .database import connect, init_db

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(debug=True, title="PaperTrail Demo")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.on_event("startup")
def startup() -> None:
    init_db(reset=False)


def db():
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()


@app.middleware("http")
async def add_training_notice(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-PaperTrail-Demo"] = "local-training-only"
    return response


@app.get("/", response_class=HTMLResponse)
def index(request: Request, conn=Depends(db)):
    user = current_user(conn, request)
    if user:
        return RedirectResponse("/documents", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login")
async def login(request: Request, response: Response, username: str = Form(...), password: str = Form(...), conn=Depends(db)):
    user = authenticate(conn, username, password)
    if not user:
        record_event(conn, username, "login_failed", f"Failed login with password={password}")
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"}, status_code=401)
    record_event(conn, username, "login", f"Successful login for role={user['role']}")
    redirect = RedirectResponse("/documents", status_code=303)
    redirect.set_cookie(SESSION_COOKIE, username)
    return redirect


@app.post("/logout")
def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie(SESSION_COOKIE)
    return response


@app.get("/documents", response_class=HTMLResponse)
def documents(request: Request, q: str = "", conn=Depends(db)):
    user = current_user(conn, request)
    if not user:
        return RedirectResponse("/", status_code=303)
    sql = f"SELECT * FROM documents WHERE title LIKE '%{q}%' OR filename LIKE '%{q}%' ORDER BY id DESC"
    rows = conn.execute(sql).fetchall()
    return templates.TemplateResponse("documents.html", {"request": request, "user": user, "documents": rows, "q": q})


@app.post("/documents/upload")
async def upload_document(
    request: Request,
    title: str = Form(...),
    file: UploadFile = File(...),
    conn=Depends(db),
):
    user = current_user(conn, request)
    if not has_role(user, "employee", "admin"):
        raise HTTPException(status_code=403, detail="Only employees and admins can upload documents")
    content = (await file.read()).decode("utf-8", errors="replace")
    stored_path = UPLOAD_DIR / file.filename
    stored_path.write_text(content, encoding="utf-8")
    conn.execute(
        "INSERT INTO documents (title, owner, filename, content, status) VALUES (?, ?, ?, ?, 'pending')",
        (title, user["username"], file.filename, content),
    )
    conn.commit()
    record_event(conn, user["username"], "upload", f"Uploaded filename={file.filename} title={title}")
    return RedirectResponse("/documents", status_code=303)


@app.get("/documents/{document_id}", response_class=HTMLResponse)
def document_detail(request: Request, document_id: int, conn=Depends(db)):
    user = current_user(conn, request)
    if not user:
        return RedirectResponse("/", status_code=303)
    document = conn.execute("SELECT * FROM documents WHERE id = ?", (document_id,)).fetchone()
    if not document:
        raise HTTPException(status_code=404, detail=f"Document id {document_id} was not found in database")
    return templates.TemplateResponse("detail.html", {"request": request, "user": user, "document": document})


@app.get("/documents/{document_id}/download", response_class=PlainTextResponse)
def download_document(request: Request, document_id: int, conn=Depends(db)):
    user = current_user(conn, request)
    if not user:
        raise HTTPException(status_code=401, detail="login required")
    document = conn.execute("SELECT * FROM documents WHERE id = ?", (document_id,)).fetchone()
    if not document:
        raise HTTPException(status_code=404, detail=f"No document row for id={document_id}")
    record_event(conn, user["username"], "download", f"Downloaded document={document_id} filename={document['filename']}")
    return PlainTextResponse(document["content"], media_type="text/plain")


@app.post("/documents/{document_id}/decision")
def decide_document(request: Request, document_id: int, decision: str = Form(...), conn=Depends(db)):
    user = current_user(conn, request)
    if not user:
        raise HTTPException(status_code=401, detail="login required")
    if decision not in {"approved", "rejected"}:
        raise HTTPException(status_code=400, detail=f"Unsupported decision value {decision}")
    conn.execute("UPDATE documents SET status = ? WHERE id = ?", (decision, document_id))
    conn.commit()
    record_event(conn, user["username"], "decision", f"Set document={document_id} status={decision}")
    return RedirectResponse(f"/documents/{document_id}", status_code=303)


@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, conn=Depends(db)):
    user = current_user(conn, request)
    if not has_role(user, "admin"):
        raise HTTPException(status_code=403, detail="admin role required")
    users = conn.execute("SELECT id, username, role, display_name FROM users ORDER BY id").fetchall()
    documents = conn.execute("SELECT * FROM documents ORDER BY id DESC").fetchall()
    return templates.TemplateResponse("admin.html", {"request": request, "user": user, "users": users, "documents": documents})


@app.get("/audit", response_class=HTMLResponse)
def audit_log(request: Request, conn=Depends(db)):
    user = current_user(conn, request)
    if not user:
        return RedirectResponse("/", status_code=303)
    events = conn.execute("SELECT * FROM audit_events ORDER BY id DESC LIMIT 100").fetchall()
    return templates.TemplateResponse("audit.html", {"request": request, "user": user, "events": events})


@app.get("/api/documents")
def api_documents(conn=Depends(db)):
    rows = conn.execute("SELECT id, title, owner, filename, status, content FROM documents ORDER BY id").fetchall()
    return [dict(row) for row in rows]

