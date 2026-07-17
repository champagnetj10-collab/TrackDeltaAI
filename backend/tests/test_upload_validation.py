"""Unit tests for session upload validation (extension check, S3 existence/size
checks before enqueueing processing). Uses an in-memory SQLite `sessions` table
(FK enforcement is off by default in SQLite, so the referenced users/debriefs
tables don't need to exist) and mocks StorageService/Celery so no real S3 or
broker is touched.
"""
from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.middleware.auth import get_current_user
from app.models.session import Session as SessionModel
from app.models.user import User
from app.routers import sessions as sessions_module


@pytest.fixture
def db_session():
    # FastAPI runs sync endpoints in a worker thread, so a plain in-memory
    # SQLite connection (thread-local by default) won't be usable from the
    # request handler. StaticPool keeps one shared connection alive instead.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionModel.__table__.create(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


@pytest.fixture
def fake_user() -> User:
    return User(
        id=uuid.uuid4(),
        email="driver@example.com",
        subscription_tier="free",
        monthly_uploads_used=0,
    )


@pytest.fixture
def client(fake_user, db_session):
    app.dependency_overrides[get_current_user] = lambda: fake_user
    app.dependency_overrides[get_db] = lambda: db_session
    yield TestClient(app)
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(get_db, None)


def test_upload_url_rejects_non_ibt_filename(client):
    response = client.post("/v1/sessions/upload-url", json={"filename": "malware.exe"})
    assert response.status_code == 400
    assert "iRacing telemetry file" in response.json()["error"]["message"]


def test_upload_url_accepts_ibt_filename(client, monkeypatch):
    monkeypatch.setattr(
        sessions_module.StorageService,
        "generate_upload_url",
        lambda self, bucket, key, expiry_seconds=900: f"https://storage.example/{bucket}/{key}",
    )
    response = client.post("/v1/sessions/upload-url", json={"filename": "practice.ibt"})
    assert response.status_code == 200
    body = response.json()
    assert "presigned_url" in body
    assert body["presigned_url"].startswith("http")


def test_upload_url_extension_check_is_case_insensitive(client, monkeypatch):
    monkeypatch.setattr(
        sessions_module.StorageService,
        "generate_upload_url",
        lambda self, bucket, key, expiry_seconds=900: f"https://storage.example/{bucket}/{key}",
    )
    response = client.post("/v1/sessions/upload-url", json={"filename": "PRACTICE.IBT"})
    assert response.status_code == 200


def test_upload_url_enforces_free_tier_limit(client, fake_user):
    fake_user.monthly_uploads_used = 3
    response = client.post("/v1/sessions/upload-url", json={"filename": "practice.ibt"})
    assert response.status_code == 402


def test_upload_url_ignores_path_traversal_in_filename(client, monkeypatch):
    captured_key = {}

    def fake_generate(self, bucket, key, expiry_seconds=900):
        captured_key["key"] = key
        return f"https://storage.example/{bucket}/{key}"

    monkeypatch.setattr(sessions_module.StorageService, "generate_upload_url", fake_generate)
    response = client.post("/v1/sessions/upload-url", json={"filename": "../../etc/passwd.ibt"})
    assert response.status_code == 200
    assert ".." not in captured_key["key"]
    assert "passwd" not in captured_key["key"]


def test_upload_url_handles_unicode_filename_without_empty_key(client, monkeypatch):
    captured_key = {}

    def fake_generate(self, bucket, key, expiry_seconds=900):
        captured_key["key"] = key
        return f"https://storage.example/{bucket}/{key}"

    monkeypatch.setattr(sessions_module.StorageService, "generate_upload_url", fake_generate)
    response = client.post("/v1/sessions/upload-url", json={"filename": "🏎️ race day 🔥.ibt"})
    assert response.status_code == 200
    assert not captured_key["key"].endswith("/")


def _create_session(db_session, user_id: uuid.UUID) -> SessionModel:
    session = SessionModel(id=uuid.uuid4(), user_id=user_id, raw_file_s3_key="users/x/sessions/y/z.ibt")
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


def test_upload_complete_rejects_missing_file(client, db_session, fake_user, monkeypatch):
    session = _create_session(db_session, fake_user.id)
    monkeypatch.setattr(
        sessions_module.StorageService, "get_object_size", lambda self, bucket, key: None
    )

    response = client.post(f"/v1/sessions/{session.id}/upload-complete", json={})
    assert response.status_code == 400
    assert "couldn't find" in response.json()["error"]["message"]


def test_upload_complete_rejects_empty_file(client, db_session, fake_user, monkeypatch):
    session = _create_session(db_session, fake_user.id)
    monkeypatch.setattr(
        sessions_module.StorageService, "get_object_size", lambda self, bucket, key: 0
    )

    response = client.post(f"/v1/sessions/{session.id}/upload-complete", json={})
    assert response.status_code == 400
    assert "empty" in response.json()["error"]["message"]


def test_upload_complete_rejects_oversized_file(client, db_session, fake_user, monkeypatch):
    session = _create_session(db_session, fake_user.id)
    oversized = (sessions_module.settings.max_upload_size_mb + 1) * 1024 * 1024
    monkeypatch.setattr(
        sessions_module.StorageService, "get_object_size", lambda self, bucket, key: oversized
    )

    response = client.post(f"/v1/sessions/{session.id}/upload-complete", json={})
    assert response.status_code == 400
    assert "larger than" in response.json()["error"]["message"]


def test_upload_complete_succeeds_and_enqueues(client, db_session, fake_user, monkeypatch):
    session = _create_session(db_session, fake_user.id)
    monkeypatch.setattr(
        sessions_module.StorageService, "get_object_size", lambda self, bucket, key: 5_000_000
    )
    mock_task = MagicMock()
    monkeypatch.setattr("pipeline.tasks.process_session.process_session_task", mock_task)

    response = client.post(f"/v1/sessions/{session.id}/upload-complete", json={"driver_note": "test"})

    assert response.status_code == 200
    assert response.json()["status"] == "processing"
    mock_task.delay.assert_called_once_with(str(session.id))

    db_session.refresh(session)
    assert session.processing_status == "parsing"
    assert session.driver_note == "test"
    assert fake_user.monthly_uploads_used == 1


def test_upload_complete_404_for_other_users_session(client, db_session):
    other_user_id = uuid.uuid4()
    session = _create_session(db_session, other_user_id)

    response = client.post(f"/v1/sessions/{session.id}/upload-complete", json={})
    assert response.status_code == 404
