"""Verifies the app boots and serves traffic without ANTHROPIC_API_KEY or
STRIPE_SECRET_KEY/STRIPE_WEBHOOK_SECRET configured.

These previously had no default in Settings, so pydantic-settings raised a
ValidationError the instant app/config.py was imported — before uvicorn
could even start — any time those env vars weren't set. That's a much
bigger blast radius than "the debrief/billing features don't work"; it
means the whole API, including GET /health, never comes up at all. See
app/config.py's module docstring for the full required-to-boot vs
required-for-feature-X breakdown this test exists to protect.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app


def test_settings_construct_without_anthropic_or_stripe(monkeypatch):
    """The exact failure mode reported: Settings() must not require these.

    _env_file=None and clearing any real OS env vars isolates this from
    whatever happens to be in a developer's local backend/.env (e.g. this
    repo's own local .env has a placeholder ANTHROPIC_API_KEY) — the point
    is to prove the field *default* works when the platform genuinely has
    nothing set, which is exactly Railway's situation before this fix.
    """
    for var in ("ANTHROPIC_API_KEY", "STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET"):
        monkeypatch.delenv(var, raising=False)

    settings = Settings(
        _env_file=None,
        database_url="postgresql://user:pass@localhost:5432/db",
        supabase_url="https://stub.supabase.co",
        supabase_anon_key="stub-anon-key",
        supabase_service_role_key="stub-service-role-key",
        # anthropic_api_key / stripe_secret_key / stripe_webhook_secret
        # deliberately omitted — this must not raise.
    )
    assert settings.anthropic_api_key == ""
    assert settings.stripe_secret_key == ""
    assert settings.stripe_webhook_secret == ""


def test_health_ok_without_anthropic_or_stripe_configured(monkeypatch):
    """The literal ask: GET /health must work with these unconfigured."""
    monkeypatch.setattr("app.main.settings.anthropic_api_key", "")
    monkeypatch.setattr("app.main.settings.stripe_secret_key", "")
    monkeypatch.setattr("app.main.settings.stripe_webhook_secret", "")

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_delta_voice_raises_clear_error_when_anthropic_not_configured(monkeypatch):
    """Boot-time leniency shouldn't become a confusing failure later — the
    feature itself must fail fast with an actionable message the moment
    it's actually used without a key, not a cryptic SDK auth error."""
    from pipeline.llm import delta_voice as delta_voice_module

    monkeypatch.setattr(delta_voice_module.settings, "anthropic_api_key", "")

    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY is not configured"):
        delta_voice_module.DeltaVoice()
