"""Driver DNA model — versioned snapshots of a driver's profile."""
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class DriverDNA(Base):
    __tablename__ = "driver_dna"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("sessions.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    schema_version: Mapped[str] = mapped_column(String(20), default="1.0")

    # Metadata
    total_sessions: Mapped[int] = mapped_column(Integer, default=0)
    total_clean_laps: Mapped[int] = mapped_column(Integer, default=0)
    overall_confidence: Mapped[float] = mapped_column(Float, default=0.0)

    # DNA attributes stored as JSONB for schema flexibility
    # Each attribute follows: { "value": ..., "confidence": "low", "confidence_score": 0.2 }
    braking: Mapped[dict | None] = mapped_column(JSONB)
    throttle: Mapped[dict | None] = mapped_column(JSONB)
    steering: Mapped[dict | None] = mapped_column(JSONB)
    consistency: Mapped[dict | None] = mapped_column(JSONB)
    risk: Mapped[dict | None] = mapped_column(JSONB)
    pressure: Mapped[dict | None] = mapped_column(JSONB)
    learning: Mapped[dict | None] = mapped_column(JSONB)

    # Per-track profiles
    track_profiles: Mapped[dict | None] = mapped_column(JSONB)

    # Is this the latest DNA version for this driver?
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<DriverDNA user={self.user_id} sessions={self.total_sessions} confidence={self.overall_confidence:.2f}>"
