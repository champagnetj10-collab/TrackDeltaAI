"""Unit tests for the subscriptions router.

These test routing, auth enforcement, and graceful "not configured" /
signature-validation behavior only — nothing here exercises a real Stripe
account. Full checkout/portal/webhook processing needs real Stripe test
keys to verify (see module docstring in app/routers/subscriptions.py).
"""
from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.middleware.auth import get_current_user
from app.models.user import User
from app.routers import subscriptions as subscriptions_module


@pytest.fixture
def fake_user() -> User:
    return User(
        id=uuid.uuid4(),
        email="driver@example.com",
        subscription_tier="free",
        subscription_status=None,
        monthly_uploads_used=1,
        stripe_customer_id=None,
    )


@pytest.fixture
def authed_client(fake_user):
    app.dependency_overrides[get_current_user] = lambda: fake_user
    yield TestClient(app)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def client():
    return TestClient(app)


def test_checkout_requires_auth(client):
    response = client.post("/v1/subscriptions/checkout", json={})
    assert response.status_code == 401


def test_portal_requires_auth(client):
    response = client.post("/v1/subscriptions/portal")
    assert response.status_code == 401


def test_current_requires_auth(client):
    response = client.get("/v1/subscriptions/current")
    assert response.status_code == 401


def test_current_returns_status_for_authed_user(authed_client, fake_user):
    response = authed_client.get("/v1/subscriptions/current")
    assert response.status_code == 200
    body = response.json()
    assert body["subscription_tier"] == "free"
    assert body["monthly_uploads_used"] == 1
    assert body["monthly_upload_limit"] is not None


def test_checkout_returns_503_when_stripe_not_configured(authed_client, monkeypatch):
    monkeypatch.setattr(subscriptions_module.settings, "stripe_secret_key", "")
    response = authed_client.post("/v1/subscriptions/checkout", json={})
    assert response.status_code == 503


def test_portal_returns_503_when_stripe_not_configured(authed_client, monkeypatch):
    monkeypatch.setattr(subscriptions_module.settings, "stripe_secret_key", "")
    response = authed_client.post("/v1/subscriptions/portal")
    assert response.status_code == 503


def test_portal_returns_400_when_no_stripe_customer(authed_client, monkeypatch):
    monkeypatch.setattr(subscriptions_module.settings, "stripe_secret_key", "sk_test_fake")
    response = authed_client.post("/v1/subscriptions/portal")
    assert response.status_code == 400


def test_webhook_returns_503_when_not_configured(client, monkeypatch):
    monkeypatch.setattr(subscriptions_module.settings, "stripe_secret_key", "")
    response = client.post("/webhooks/stripe", content=b"{}")
    assert response.status_code == 503


def test_webhook_rejects_invalid_signature(client, monkeypatch):
    monkeypatch.setattr(subscriptions_module.settings, "stripe_secret_key", "sk_test_fake")
    monkeypatch.setattr(subscriptions_module.settings, "stripe_webhook_secret", "whsec_fake")
    response = client.post(
        "/webhooks/stripe", content=b"{}", headers={"stripe-signature": "bad-signature"}
    )
    assert response.status_code == 400
