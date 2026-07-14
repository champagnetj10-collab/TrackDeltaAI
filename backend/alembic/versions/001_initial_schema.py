"""Initial schema — all core tables

Revision ID: 001
Revises:
Create Date: 2026-06-30
"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("display_name", sa.String(100)),
        sa.Column("iracing_member_id", sa.String(50)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("experience_level", sa.String(50)),
        sa.Column("irating_range", sa.String(50)),
        sa.Column("primary_goal", sa.String(100)),
        sa.Column("main_frustration", sa.String(100)),
        sa.Column("stripe_customer_id", sa.String(100)),
        sa.Column("subscription_tier", sa.String(20), server_default="free"),
        sa.Column("subscription_status", sa.String(20)),
        sa.Column("subscription_period_end", sa.DateTime(timezone=True)),
        sa.Column("monthly_uploads_used", sa.Integer, server_default="0"),
        sa.Column("monthly_uploads_reset_at", sa.DateTime(timezone=True)),
    )

    # --- tracks ---
    op.create_table(
        "tracks",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("iracing_track_name", sa.String(200), nullable=False),
        sa.Column("configuration", sa.String(100)),
        sa.Column("total_length_m", sa.Float),
        sa.Column("country", sa.String(100)),
        sa.Column("surface_type", sa.String(50), server_default="asphalt"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- track_corners ---
    op.create_table(
        "track_corners",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("track_id", sa.String(100), sa.ForeignKey("tracks.id"), index=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("corner_type", sa.String(50), nullable=False),
        sa.Column("sequence_number", sa.Integer, nullable=False),
        sa.Column("entry_pct", sa.Float, nullable=False),
        sa.Column("apex_pct", sa.Float, nullable=False),
        sa.Column("exit_pct", sa.Float, nullable=False),
        sa.Column("reference_brake_point_pct", sa.Float),
        sa.Column("expected_min_speed_kph", sa.Float),
        sa.Column("trail_braking_expected", sa.Boolean, server_default="false"),
        sa.Column("notes", sa.Text),
    )

    # --- debriefs (before sessions — FK target) ---
    op.create_table(
        "debriefs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), unique=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("debrief_content", postgresql.JSONB, nullable=False),
        sa.Column("dna_version_id", postgresql.UUID(as_uuid=True)),
        sa.Column("dna_confidence_at_debrief", sa.Float),
        sa.Column("llm_model_used", sa.String(100)),
        sa.Column("llm_prompt_tokens", sa.Integer),
        sa.Column("llm_completion_tokens", sa.Integer),
        sa.Column("llm_total_cost_usd", sa.Float),
    )

    # --- sessions ---
    op.create_table(
        "sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("raw_file_s3_key", sa.String(500)),
        sa.Column("file_size_bytes", sa.BigInteger),
        sa.Column("iracing_track_name", sa.String(200)),
        sa.Column("track_config", sa.String(100)),
        sa.Column("car_name", sa.String(200)),
        sa.Column("car_class", sa.String(100)),
        sa.Column("session_type", sa.String(50)),
        sa.Column("session_date", sa.Date),
        sa.Column("total_laps", sa.Integer),
        sa.Column("clean_laps", sa.Integer),
        sa.Column("best_lap_time_ms", sa.Integer),
        sa.Column("mean_lap_time_ms", sa.Integer),
        sa.Column("session_duration_s", sa.Integer),
        sa.Column("processing_status", sa.String(50), server_default="pending", index=True),
        sa.Column("processing_started_at", sa.DateTime(timezone=True)),
        sa.Column("processing_completed_at", sa.DateTime(timezone=True)),
        sa.Column("processing_error", sa.Text),
        sa.Column("driver_note", sa.Text),
        sa.Column("features_s3_key", sa.String(500)),
        sa.Column("debrief_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("debriefs.id"), nullable=True),
    )
    op.create_index("idx_sessions_status", "sessions", ["processing_status"])

    # --- driver_dna ---
    op.create_table(
        "driver_dna",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), index=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sessions.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("schema_version", sa.String(20), server_default="1.0"),
        sa.Column("total_sessions", sa.Integer, server_default="0"),
        sa.Column("total_clean_laps", sa.Integer, server_default="0"),
        sa.Column("overall_confidence", sa.Float, server_default="0.0"),
        sa.Column("braking", postgresql.JSONB),
        sa.Column("throttle", postgresql.JSONB),
        sa.Column("steering", postgresql.JSONB),
        sa.Column("consistency", postgresql.JSONB),
        sa.Column("risk", postgresql.JSONB),
        sa.Column("pressure", postgresql.JSONB),
        sa.Column("learning", postgresql.JSONB),
        sa.Column("track_profiles", postgresql.JSONB),
        sa.Column("is_current", sa.Boolean, server_default="true"),
    )
    op.create_index("idx_dna_current", "driver_dna", ["user_id", "is_current"])

    # --- conversations ---
    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("debrief_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("debriefs.id", ondelete="CASCADE")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "conversation_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id", ondelete="CASCADE"), index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("llm_tokens_used", sa.Integer),
    )

    # --- subscription_events ---
    op.create_table(
        "subscription_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("event_type", sa.String(100)),
        sa.Column("stripe_event_id", sa.String(200), unique=True),
        sa.Column("event_data", postgresql.JSONB),
        sa.Column("processed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("subscription_events")
    op.drop_table("conversation_messages")
    op.drop_table("conversations")
    op.drop_index("idx_dna_current", "driver_dna")
    op.drop_table("driver_dna")
    op.drop_index("idx_sessions_status", "sessions")
    op.drop_table("sessions")
    op.drop_table("debriefs")
    op.drop_table("track_corners")
    op.drop_table("tracks")
    op.drop_table("users")
