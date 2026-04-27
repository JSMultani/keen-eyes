from __future__ import annotations


def login(client, username: str, password: str):
    return client.post("/login", data={"username": username, "password": password}, follow_redirects=False)


def test_employee_can_sign_in_and_list_documents(client):
    response = login(client, "employee", "employee123")
    assert response.status_code == 303
    response = client.get("/documents")
    assert response.status_code == 200
    assert "Travel Policy Draft" in response.text


def test_employee_can_upload_document(client):
    login(client, "employee", "employee123")
    response = client.post(
        "/documents/upload",
        data={"title": "Quarterly Notes"},
        files={"file": ("quarterly.txt", b"Synthetic quarterly notes.", "text/plain")},
        follow_redirects=False,
    )
    assert response.status_code == 303
    listing = client.get("/documents")
    assert "Quarterly Notes" in listing.text


def test_reviewer_can_approve_document(client):
    login(client, "reviewer", "reviewer123")
    response = client.post("/documents/1/decision", data={"decision": "approved"}, follow_redirects=False)
    assert response.status_code == 303
    detail = client.get("/documents/1")
    assert "approved" in detail.text


def test_admin_can_view_dashboard_and_audit(client):
    login(client, "admin", "admin123")
    dashboard = client.get("/admin")
    assert dashboard.status_code == 200
    assert "Admin Dashboard" in dashboard.text
    audit = client.get("/audit")
    assert audit.status_code == 200
    assert "Audit Log" in audit.text

