"""Session model — one uploaded .ibt file from a driver."""
import uuid
from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # S3 reference
    raw_file_s3_key: Mapped[str | None] = mapped_column(String(500))
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger)

    # Session metadata (from .ibt parsing)
    iracing_track_name: Mapped[str | None] = mapped_column(String(200))
    track_config: Mapped[str | None] = mapped_column(String(100))
    car_name: Mapped[str | None] = mapped_column(String(200))
    car_class: Mapped[str | None] = mapped_column(String(100))
    session_type: Mapped[str | None] = mapped_column(String(50))
    session_date: Mapped[date | None] = mapped_column(Date)
    total_laps: Mapped[int | None] = mapped_column(Integer)
    clean_laps: Mapped[int | None] = mapped_column(Integer)
    best_lap_time_ms: Mapped[int | None] = mapped_column(Integer)
    mean_lap_time_ms: Mapped[int | None] = mapped_column(Integer)
    session_duration_s: Mapped[int | None] = mapped_column(Integer)

    # Processing state
    processing_status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    processing_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    processing_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    processing_error: Mapped[str | None] = mapped_column(Text)

    # Optional driver note
    driver_note: Mapped[str | None] = mapped_column(Text)

    # Processed data reference
    features_s3_key: Mapped[str | None] = mapped_column(String(500))
    debrief_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("debriefs.id"), nullable=True)

    def __repr__(self) -> str:
        return f"<Session id={self.id} track={self.iracing_track_name} status={self.processing_status}>"
