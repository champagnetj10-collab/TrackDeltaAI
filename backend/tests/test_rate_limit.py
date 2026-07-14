"""Unit tests for the rate limiter: fails open when Redis is unavailable,
enforces the configured limit when it isn't, using a fake in-memory Redis
stand-in rather than a real connection (consistent with this codebase's
fake-client pattern for other external services).
"""
from __future__ import annotations

import uuid

import pytest
import redis
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.middleware import rate_limit as rate_limit_module
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import rate_limit
from app.models.user import User


class _FakeRedis:
    """Minimal INCR/EXPIRE stand-in — enough for the fixed-window counter."""

    def __init__(self):
        self.counts: dict[str, int] = {}

    def incr(self, key: str) -> int:
        self.counts[key] = self.counts.get(key, 0) + 1
        return self.counts[key]

    def expire(self, key: str, seconds: int) -> None:
        pass


class _BrokenRedis:
    def incr(self, key: str) -> int:
        raise redis.ConnectionError("Redis is down")


@pytest.fixture
def fake_user() -> User:
    return User(id=uuid.uuid4(), email="driver@example.com", subscription_tier="free")


@pytest.fixture
def tiny_app(fake_user):
    """A throwaway app with one route limited to 2 requests per 60s window."""
    app = FastAPI()

    @app.get("/limited", dependencies=[rate_limit(2, 60, "test-scope")])
    def limited(current_user: User = Depends(get_current_user)):
        return {"ok": True}

    app.dependency_overrides[get_current_user] = lambda: fake_user
    yield app
    app.dependency_overrides.pop(get_current_user, None)


def test_allows_requests_under_the_limit(tiny_app, monkeypatch):
    monkeypatch.setattr(rate_limit_module, "_redis_client", _FakeRedis())
    client = TestClient(tiny_app)

    assert client.get("/limited").status_code == 200
    assert client.get("/limited").status_code == 200


def test_returns_429_once_limit_is_exceeded(tiny_app, monkeypatch):
    monkeypatch.setattr(rate_limit_module, "_redis_client", _FakeRedis())
    client = TestClient(tiny_app)

    client.get("/limited")
    client.get("/limited")
    response = client.get("/limited")

    assert response.status_code == 429
    assert "Too many requests" in response.json()["detail"]


def test_different_users_have_independent_limits(tiny_app, monkeypatch):
    monkeypatch.setattr(rate_limit_module, "_redis_client", _FakeRedis())

    other_user = User(id=uuid.uuid4(), email="other@example.com", subscription_tier="free")
    client = TestClient(tiny_app)

    client.get("/limited")
    client.get("/limited")
    assert client.get("/limited").status_code == 429

    tiny_app.dependency_overrides[get_current_user] = lambda: other_user
    assert client.get("/limited").status_code == 200


def test_fails_open_when_redis_is_unavailable(tiny_app, monkeypatch):
    monkeypatch.setattr(rate_limit_module, "_redis_client", _BrokenRedis())
    client = TestClient(tiny_app)

    # Well past the configured limit of 2 — every request should still succeed.
    for _ in range(5):
        assert client.get("/limited").status_code == 200
