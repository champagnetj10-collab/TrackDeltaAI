"""Debrief model — Delta's complete coaching output for one session."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Debrief(Base):
    __tablename__ = "debriefs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"), unique=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Full debrief content — structured JSON (see Architecture doc for schema)
    debrief_content: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # DNA state at time of debrief
    dna_version_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("driver_dna.id"))
    dna_confidence_at_debrief: Mapped[float | None] = mapped_column(Float)

    # LLM usage tracking (cost monitoring)
    llm_model_used: Mapped[str | None] = mapped_column(String(100))
    llm_prompt_tokens: Mapped[int | None] = mapped_column(Integer)
    llm_completion_tokens: Mapped[int | None] = mapped_column(Integer)
    llm_total_cost_usd: Mapped[float | None] = mapped_column(Float)

    def __repr__(self) -> str:
        return f"<Debrief session={self.session_id}>"
