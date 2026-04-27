from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import database
from app.main import app, db


@pytest.fixture()
def client():
    with tempfile.TemporaryDirectory() as tmp:
        test_db = Path(tmp) / "papertrail-test.db"
        database.init_db(reset=True, db_path=test_db)

        def override_db():
            conn = database.connect(test_db)
            try:
                yield conn
            finally:
                conn.close()

        app.dependency_overrides[db] = override_db
        os.environ["PAPERTRAIL_TESTING"] = "1"
        with TestClient(app) as test_client:
            yield test_client
        app.dependency_overrides.clear()

