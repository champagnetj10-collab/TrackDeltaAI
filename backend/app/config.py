"""
TrackDelta AI — Application Configuration
All settings are read from environment variables.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Environment ---
    environment: str = "local"

    # --- Database ---
    database_url: str

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"

    # --- Celery ---
    # When true, .delay()/.apply_async() run the task synchronously in-process
    # instead of going through the Redis broker. For local dev without a
    # running Redis instance (or a separate worker process) — never set this
    # in staging/production, where the pipeline must run asynchronously.
    celery_task_always_eager: bool = False

    # --- Supabase ---
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str

    # --- JWT (Supabase signs with this secret) ---
    supabase_jwt_secret: str = ""  # Set in production

    # --- AWS S3 ---
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "us-east-1"
    s3_bucket_telemetry: str = "trackdelta-raw-telemetry"
    s3_bucket_processed: str = "trackdelta-processed-features"
    s3_bucket_debriefs: str = "trackdelta-debriefs"
    # Optional: point boto3 at any S3-compatible endpoint instead of AWS —
    # e.g. Supabase Storage's S3 API, or a local MinIO instance for dev.
    # Leave unset to use real AWS S3.
    s3_endpoint_url: str | None = None

    # --- Anthropic ---
    anthropic_api_key: str
    anthropic_model: str = "claude-sonnet-4-5"

    # --- Stripe ---
    stripe_secret_key: str
    stripe_webhook_secret: str
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
