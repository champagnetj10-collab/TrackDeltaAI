"""Unit tests for JWKS-based (ES256) token verification — the path used by
Supabase projects created with the new asymmetric signing keys, which have
no static JWT secret. httpx.get is mocked so no real network call is made;
tokens are signed with a locally-generated EC key pair.
"""
from __future__ import annotations

import base64
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi import HTTPException
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.middleware import auth as auth_module
from app.models.user import User

KID = "test-signing-key"


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


@pytest.fixture
def ec_keypair():
    private_key = ec.generate_private_key(ec.SECP256R1())
    return private_key, private_key.public_key()


@pytest.fixture
def jwks_response(ec_keypair):
    _, public_key = ec_keypair
    numbers = public_key.public_numbers()
    return {
        "keys": [{
            "kty": "EC", "crv": "P-256", "alg": "ES256", "use": "sig", "kid": KID,
            "x": _b64url(numbers.x.to_bytes(32, "big")),
            "y": _b64url(numbers.y.to_bytes(32, "big")),
        }]
    }


@pytest.fixture(autouse=True)
def _use_jwks_path(monkeypatch):
    """Force the JWKS branch (empty secret) and reset the module-level cache
    between tests so mocked responses don't leak across tests."""
    monkeypatch.setattr(auth_module.settings, "supabase_jwt_secret", "")
    monkeypatch.setattr(auth_module.settings, "supabase_url", "https://project.supabase.co")
    auth_module._jwks_cache["keys"] = []
    auth_module._jwks_cache["fetched_at"] = 0.0


@pytest.fixture
def mock_jwks_endpoint(monkeypatch, jwks_response):
    calls = {"count": 0}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return jwks_response

    def fake_get(url, timeout=5.0):
        calls["count"] += 1
        assert "jwks.json" in url
        return FakeResponse()

    monkeypatch.setattr(auth_module.httpx, "get", fake_get)
    return calls


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    User.__table__.create(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


class FakeCredentials:
    def __init__(self, token: str) -> None:
        self.credentials = token


def make_es256_token(ec_keypair, user_id, email=None, kid=KID, alg="ES256") -> str:
    private_key, _ = ec_keypair
    priv_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    payload = {"sub": str(user_id), "exp": datetime.now(timezone.utc) + timedelta(hours=1)}
    if email:
        payload["email"] = email
    return jwt.encode(payload, priv_pem, algorithm=alg, headers={"kid": kid})


def test_verifies_es256_token_via_jwks(ec_keypair, mock_jwks_endpoint, db_session):
    user_id = uuid.uuid4()
    token = make_es256_token(ec_keypair, user_id, email="driver@example.com")

    user = auth_module.get_current_user(credentials=FakeCredentials(token), db=db_session)

    assert user.id == user_id
    assert user.email == "driver@example.com"
    assert mock_jwks_endpoint["count"] == 1  # fetched once, then cached


def test_jwks_response_is_cached_across_calls(ec_keypair, mock_jwks_endpoint, db_session):
    token1 = make_es256_token(ec_keypair, uuid.uuid4(), email="a@example.com")
    token2 = make_es256_token(ec_keypair, uuid.uuid4(), email="b@example.com")

    auth_module.get_current_user(credentials=FakeCredentials(token1), db=db_session)
    auth_module.get_current_user(credentials=FakeCredentials(token2), db=db_session)

    assert mock_jwks_endpoint["count"] == 1


def test_unknown_kid_triggers_one_refetch_then_fails(ec_keypair, mock_jwks_endpoint, db_session):
    token = make_es256_token(ec_keypair, uuid.uuid4(), email="a@example.com", kid="rotated-out-key")

    with pytest.raises(HTTPException) as exc_info:
        auth_module.get_current_user(credentials=FakeCredentials(token), db=db_session)

    assert exc_info.value.status_code == 401
    # Initial fetch + one forced refresh attempt to check for key rotation.
    assert mock_jwks_endpoint["count"] == 2


def test_token_signed_by_different_key_rejected(mock_jwks_endpoint, db_session):
    other_keypair = (ec.generate_private_key(ec.SECP256R1()),)
    other_keypair = (other_keypair[0], other_keypair[0].public_key())
    # Signed with a *different* private key but claims the *known* kid.
    token = make_es256_token(other_keypair, uuid.uuid4(), email="a@example.com", kid=KID)

    with pytest.raises(HTTPException) as exc_info:
        auth_module.get_current_user(credentials=FakeCredentials(token), db=db_session)
    assert exc_info.value.status_code == 401


def test_legacy_hs256_path_used_when_secret_configured(monkeypatch, db_session, mock_jwks_endpoint):
    monkeypatch.setattr(auth_module.settings, "supabase_jwt_secret", "legacy-secret")
    user_id = uuid.uuid4()
    token = jwt.encode(
        {"sub": str(user_id), "email": "legacy@example.com"}, "legacy-secret", algorithm="HS256"
    )

    user = auth_module.get_current_user(credentials=FakeCredentials(token), db=db_session)

    assert user.email == "legacy@example.com"
    assert mock_jwks_endpoint["count"] == 0  # JWKS never touched when a secret is configured
