"""
TrackDelta AI — Application Configuration
All settings are read from environment variables.

Required for the app to boot at all (no default — Settings() raises if
missing): DATABASE_URL, SUPABASE_URL, SUPABASE_ANON_KEY,
SUPABASE_SERVICE_ROLE_KEY. Every request touches the database and/or
Supabase auth, so there's no meaningful degraded mode without these.

Deliberately NOT required to boot: ANTHROPIC_API_KEY, STRIPE_SECRET_KEY,
STRIPE_WEBHOOK_SECRET. These power specific features (Delta's narrative
debrief; billing) that are only reached well after startup, on specific
requests/tasks — the app (including GET /health) must come up and serve
traffic without them configured. Each is validated lazily, at the point
where that specific feature is actually invoked:
  - Anthropic: DeltaVoice.__init__ (pipeline/llm/delta_voice.py)
  - Stripe:    _require_stripe_configured() and the webhook handler
               (app/routers/subscriptions.py)
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Environment ---
    environment: str = "local"

    # --- Database (required to boot) ---
    database_url: str

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"

    # --- Celery ---
    # When true, .delay()/.apply_async() run the task synchronously in-process
    # instead of going through the Redis broker. For local dev without a
    # running Redis instance (or a separate worker process) — never set this
    # in staging/production, where the pipeline must run asynchronously.
    celery_task_always_eager: bool = False

    # --- Supabase (required to boot) ---
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str

    # --- JWT (Supabase signs with this secret) ---
    supabase_jwt_secret: str = ""  # Set in production

    # --- File storage (Supabase Storage buckets — see app/services/storage.py) ---
    s3_bucket_telemetry: str = "trackdelta-raw-telemetry"
    s3_bucket_processed: str = "trackdelta-processed-features"
    s3_bucket_debriefs: str = "trackdelta-debriefs"

    # --- Anthropic (optional at boot — required only to generate a debrief;
    # DeltaVoice.__init__ raises a clear error if this is blank when actually used) ---
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-5"

    # --- Stripe (optional at boot — required only for billing endpoints;
    # _require_stripe_configured() / the webhook handler check this when used) ---
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id_pro_monthly: str = ""
    stripe_price_id_pro_annual: str = ""

    # --- Email (Resend) ---
    resend_api_key: str = ""
    email_from: str = "delta@trackdelta.ai"

    # --- Business rules ---
    free_tier_monthly_uploads: int = 3
    max_upload_size_mb: int = 250
    min_laps_for_analysis: int = 5

    # --- CORS ---
    cors_origins: list[str] = [
        "http://localhost:3000",
        "https://trackdelta.ai",
        "https://www.trackdelta.ai",
    ]

    # --- Frontend (for building Stripe redirect URLs) ---
    frontend_url: str = "http://localhost:3000"


# Singleton — import this throughout the app
settings = Settings()
