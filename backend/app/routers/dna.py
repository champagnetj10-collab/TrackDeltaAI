"""DNA router — Driver DNA profile retrieval."""
import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.dna import DriverDNA

router = APIRouter(prefix="/dna", tags=["dna"])

CurrentUser = Annotated[User, Depends(get_current_user)]
DB = Annotated[Session, Depends(get_db)]


@router.get("")
def get_current_dna(current_user: CurrentUser, db: DB):
    """Get the driver's current (latest) DNA profile."""
    dna = (
        db.query(DriverDNA)
        .filter(DriverDNA.user_id == current_user.id, DriverDNA.is_current == True)  # noqa: E712
        .first()
    )
    if not dna:
        raise HTTPException(
            status_code=404,
            detail="Upload your first session to start building your Driver DNA.",
        )
    return dna


@router.get("/history")
def get_dna_history(current_user: CurrentUser, db: DB):
    """Pro only: full DNA version history for trend analysis."""
    if current_user.subscription_tier != "pro":
        raise HTTPException(status_code=403, detail="DNA history is available on Pro.")

    history = (
        db.query(DriverDNA)
        .filter(DriverDNA.user_id == current_user.id)
        .order_by(DriverDNA.created_at.desc())
        .all()
    )
    return history
