"""Users router — profile management."""
import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])

CurrentUser = Annotated[User, Depends(get_current_user)]
DB = Annotated[Session, Depends(get_db)]


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    display_name: str | None
    iracing_member_id: str | None
    experience_level: str | None
    irating_range: str | None
    primary_goal: str | None
    main_frustration: str | None
    subscription_tier: str
    subscription_status: str | None
    subscription_period_end: datetime | None
    monthly_uploads_used: int

    class Config:
        from_attributes = True


class UpdateUserRequest(BaseModel):
    display_name: str | None = None
    iracing_member_id: str | None = None
    experience_level: str | None = None
    irating_range: str | None = None
    primary_goal: str | None = None
    main_frustration: str | None = None


@router.get("/me", response_model=UserResponse)
def get_me(current_user: CurrentUser):
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_me(body: UpdateUserRequest, current_user: CurrentUser, db: DB):
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user
