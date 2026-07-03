"""Sessions router — upload, status, debrief retrieval."""
import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.session import Session as SessionModel
from app.models.debrief import Debrief
from app.services.storage import StorageService
from app.config import settings

router = APIRouter(prefix="/sessions", tags=["sessions"])

CurrentUser = Annotated[User, Depends(get_current_user)]
DB = Annotated[Session, Depends(get_db)]


class UploadUrlRequest(BaseModel):
    filename: str


class UploadUrlResponse(BaseModel):
    session_id: uuid.UUID
    presigned_url: str


class UploadCompleteRequest(BaseModel):
    driver_note: str | None = None


class ProcessingStatusResponse(BaseModel):
    session_id: uuid.UUID
    status: str
    processing_error: str | None


@router.post("/upload-url", response_model=UploadUrlResponse)
def request_upload_url(
    body: UploadUrlRequest,
    current_user: CurrentUser,
    db: DB,
):
    """Step 1: Request a presigned S3 URL for direct upload."""
    # Enforce free tier limits
    if current_user.subscription_tier == "free":
        if current_user.monthly_uploads_used >= settings.free_tier_monthly_uploads:
            raise HTTPException(
                status_code=402,
                detail=f"You've reached your {settings.free_tier_monthly_uploads} session limit for this month. Upgrade to Pro for unlimited uploads.",
            )

    # Create session record
    session = SessionModel(user_id=current_user.id)
    db.add(session)
    db.commit()
    db.refresh(session)

    # Generate presigned S3 URL
    storage = StorageService()
    s3_key = f"users/{current_user.id}/sessions/{session.id}/{body.filename}"
    presigned_url = storage.generate_upload_url(
        bucket=settings.s3_bucket_telemetry,
        key=s3_key,
        expiry_seconds=900,  # 15 minutes
    )

    # Store S3 key on session
    session.raw_file_s3_key = s3_key
    db.commit()

    return UploadUrlResponse(session_id=session.id, presigned_url=presigned_url)


@router.post("/{session_id}/upload-complete")
def upload_complete(
    session_id: uuid.UUID,
    body: UploadCompleteRequest,
    current_user: CurrentUser,
    db: DB,
):
    """Step 2: Notify that S3 upload is done; enqueue processing."""
    session = _get_session_or_404(session_id, current_user.id, db)

    session.driver_note = body.driver_note
    session.processing_status = "parsing"
    db.commit()

    # Increment monthly upload counter
    current_user.monthly_uploads_used += 1
    db.commit()

    # Enqueue the Celery pipeline task
    from pipeline.tasks.process_session import process_session_task
    process_session_task.delay(str(session.id))

    return {"status": "processing", "session_id": session_id}


@router.get("/{session_id}/status", response_model=ProcessingStatusResponse)
def get_status(session_id: uuid.UUID, current_user: CurrentUser, db: DB):
    """Poll processing status."""
    session = _get_session_or_404(session_id, current_user.id, db)
    return ProcessingStatusResponse(
        session_id=session.id,
        status=session.processing_status,
        processing_error=session.processing_error,
    )


@router.get("")
def list_sessions(current_user: CurrentUser, db: DB, limit: int = 20, offset: int = 0):
    """List the user's sessions (most recent first)."""
    sessions = (
        db.query(SessionModel)
        .filter(SessionModel.user_id == current_user.id)
        .order_by(SessionModel.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return sessions


@router.get("/{session_id}")
def get_session(session_id: uuid.UUID, current_user: CurrentUser, db: DB):
    return _get_session_or_404(session_id, current_user.id, db)


@router.get("/{session_id}/debrief")
def get_debrief(session_id: uuid.UUID, current_user: CurrentUser, db: DB):
    session = _get_session_or_404(session_id, current_user.id, db)
    if not session.debrief_id:
        raise HTTPException(status_code=404, detail="Debrief not ready yet.")
    debrief = db.query(Debrief).filter(Debrief.id == session.debrief_id).first()
    if not debrief:
        raise HTTPException(status_code=404, detail="Debrief not found.")
    return debrief


# --- Helpers ---

def _get_session_or_404(session_id: uuid.UUID, user_id: uuid.UUID, db: Session) -> SessionModel:
    session = (
        db.query(SessionModel)
        .filter(SessionModel.id == session_id, SessionModel.user_id == user_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return session
