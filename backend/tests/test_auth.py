"""Unit tests for the Supabase JWT auth middleware, especially the
auto-create-user-on-first-login behavior.

Uses an in-memory SQLite engine for just the `users` table (not the full
Base metadata, since other models use Postgres-only JSONB columns) so
these tests don't require a real Postgres connection.
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from fastapi import HTTPException
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.middleware import auth as auth_module
from app.models.user import User

TEST_SECRET = "test-secret-for-unit-tests"


class FakeCredentials:
    def __init__(self, token: str) -> None:
        self.credentials = token


def make_token(
    user_id: uuid.UUID,
    email: str | None = None,
    display_name: str | None = None,
    secret: str = TEST_SECRET,
) -> str:
    payload: dict = {"sub": str(user_id), "exp": datetime.now(UTC) + timedelta(hours=1)}
    if email:
        payload["email"] = email
    if display_name:
        payload["user_metadata"] = {"display_name": display_name}
    return jwt.encode(payload, secret, algorithm="HS256")


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    User.__table__.create(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


@pytest.fixture(autouse=True)
def _jwt_secret(monkeypatch):
    monkeypatch.setattr(auth_module.settings, "supabase_jwt_secret", TEST_SECRET)


def test_creates_user_row_on_first_call(db_session) -> None:
    user_id = uuid.uuid4()
    creds = FakeCredentials(make_token(user_id, email="driver@example.com", display_name="Test Driver"))

    user = auth_module.get_current_user(credentials=creds, db=db_session)

    assert user.id == user_id
    assert user.email == "driver@example.com"
    assert user.display_name == "Test Driver"
    assert db_session.query(User).filter(User.id == user_id).first() is not None


def test_reuses_existing_row_without_overwriting(db_session) -> None:
    user_id = uuid.uuid4()
    db_session.add(User(id=user_id, email="original@example.com", display_name="Original Name"))
    db_session.commit()

    creds = FakeCredentials(make_token(user_id, email="ignored@example.com", display_name="Ignored Name"))
    user = auth_module.get_current_user(credentials=creds, db=db_session)

    assert user.email == "original@example.com"
    assert user.display_name == "Original Name"


def test_get_current_user_id_returns_uuid_without_db() -> None:
    user_id = uuid.uuid4()
    creds = FakeCredentials(make_token(user_id, email="driver@example.com"))

    assert auth_module.get_current_user_id(credentials=creds) == user_id


def test_missing_email_claim_rejected(db_session) -> None:
    user_id = uuid.uuid4()
    creds = FakeCredentials(make_token(user_id))  # no email claim

    with pytest.raises(HTTPException) as exc_info:
        auth_module.get_current_user(credentials=creds, db=db_session)
    assert exc_info.value.status_code == 401


def test_invalid_token_rejected(db_session) -> None:
    creds = FakeCredentials("not-a-valid-jwt")

    with pytest.raises(HTTPException) as exc_info:
        auth_module.get_current_user(credentials=creds, db=db_session)
    assert exc_info.value.status_code == 401


def test_wrong_signing_secret_rejected(db_session) -> None:
    user_id = uuid.uuid4()
    creds = FakeCredentials(make_token(user_id, email="driver@example.com", secret="a-different-secret"))

    with pytest.raises(HTTPException) as exc_info:
        auth_module.get_current_user(credentials=creds, db=db_session)
    assert exc_info.value.status_code == 401
