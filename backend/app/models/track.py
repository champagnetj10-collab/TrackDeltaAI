"""Track and corner reference data — used by the feature extraction pipeline."""
from datetime import datetime
from sqlalchemy import String, Float, Boolean, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)  # e.g. 'watkins_glen_full'
    iracing_track_name: Mapped[str] = mapped_column(String(200), nullable=False)
    configuration: Mapped[str | None] = mapped_column(String(100))
    total_length_m: Mapped[float | None] = mapped_column(Float)
    country: Mapped[str | None] = mapped_column(String(100))
    surface_type: Mapped[str] = mapped_column(String(50), default="asphalt")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<Track {self.id}>"


class TrackCorner(Base):
    __tablename__ = "track_corners"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)  # e.g. 'wg_t1'
    track_id: Mapped[str] = mapped_column(ForeignKey("tracks.id"), index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)  # e.g. "Turn 1 — The 90"
    corner_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # HAIRPIN | SLOW | MEDIUM | FAST | SWEEPER | CHICANE | COMPLEX
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # LapDistPct reference points
    entry_pct: Mapped[float] = mapped_column(Float, nullable=False)
    apex_pct: Mapped[float] = mapped_column(Float, nullable=False)
    exit_pct: Mapped[float] = mapped_column(Float, nullable=False)

    # Reference values for feature extraction
    reference_brake_point_pct: Mapped[float | None] = mapped_column(Float)
    expected_min_speed_kph: Mapped[float | None] = mapped_column(Float)
    trail_braking_expected: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<TrackCorner {self.id} ({self.corner_type})>"
