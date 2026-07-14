"""Subscription event model — audit log of processed Stripe webhook events."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SubscriptionEvent(Base):
    __tablename__ = "subscription_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    event_type: Mapped[str | None] = mapped_column(String(100))
    stripe_event_id: Mapped[str | None] = mapped_column(String(200), unique=True)
    event_data: Mapped[dict | None] = mapped_column(JSONB)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<SubscriptionEvent {self.event_type} user={self.user_id}>"
