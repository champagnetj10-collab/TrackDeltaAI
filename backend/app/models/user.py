"""User model — mirrors the Supabase auth.users table with our extended fields."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(100))
    iracing_member_id: Mapped[str | None] = mapped_column(String(50))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Onboarding survey responses
    experience_level: Mapped[str | None] = mapped_column(String(50))
    irating_range: Mapped[str | None] = mapped_column(String(50))
    primary_goal: Mapped[str | None] = mapped_column(String(100))
    main_frustration: Mapped[str | None] = mapped_column(String(100))

    # Subscription
    stripe_customer_id: Mapped[str | None] = mapped_column(String(100))
    subscription_tier: Mapped[str] = mapped_column(String(20), default="free")
    subscription_status: Mapped[str | None] = mapped_column(String(20))
    subscription_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    monthly_uploads_used: Mapped[int] = mapped_column(Integer, default=0)
    monthly_uploads_reset_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
