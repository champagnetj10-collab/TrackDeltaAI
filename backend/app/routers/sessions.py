"""Sessions router — upload, status, debrief retrieval."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import rate_limit
from app.models.debrief import Debrief
from app.models.session import Session as SessionModel
from app.models.user import User
from app.services.storage import StorageService

router = APIRouter(prefix="/sessions", tags=["sessions"])

CurrentUser = Annotated[User, Depends(get_current_user)]
DB = Annotated[Session, Depends(get_db)]


class UploadUrlRequest(BaseModel):
    filename: str


class UploadUrlResponse(BaseModel):
    session_id: uuid.UUID
    presigned_url: str


class UploadCompleteRequest(BaseModel):
    # 280 to match the frontend's displayed character counter — the UI
    # promises this limit, so the API should actually enforce its own
    # contract rather than silently accepting anything sent directly.
    driver_note: str | None = Field(default=None, max_length=280)


class ProcessingStatusResponse(BaseModel):
    session_id: uuid.UUID
    status: str
    processing_error: str | None


@router.post(
    "/upload-url",
    response_model=UploadUrlResponse,
    dependencies=[rate_limit(10, 60, "sessions-upload-url")],
)
def request_upload_url(
    body: UploadUrlRequest,
    current_user: CurrentUser,
    db: DB,
):
    """Step 1: Request a presigned S3 URL for direct upload."""
    if not body.filename.lower().endswith(".ibt"):
        raise HTTPException(
            status_code=400,
            detail=(
                "This doesn't look like an iRacing telemetry file. "
                "Look for a .ibt file in Documents → iRacing → telemetry."
            ),
        )

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
    # Deliberately not using body.filename in the key: it's user-controlled
    # and unsanitized (path segments like "../../etc/passwd.ibt" collapsed
    # into an unintended key when tried; emoji/unicode filenames produced
    # a key with an empty final segment). The original filename isn't
    # displayed or stored anywhere downstream, so there's nothing to lose
    # by not using it here.
    storage = StorageService()
    s3_key = f"users/{current_user.id}/sessions/{session.id}/session.ibt"
    presigned_url = storage.generate_upload_url(
        bucket=settings.s3_bucket_telemetry,
        key=s3_key,
        expiry_seconds=900,  # 15 minutes
    )

    # Store S3 key on session
    session.raw_file_s3_key = s3_key
    db.commit()

    return UploadUrlResponse(session_id=session.id, presigned_url=presigned_url)


@router.post(
    "/{session_id}/upload-complete",
    dependencies=[rate_limit(10, 60, "sessions-upload-complete")],
)
def upload_complete(
    session_id: uuid.UUID,
    body: UploadCompleteRequest,
    current_user: CurrentUser,
    db: DB,
):
    """Step 2: Notify that S3 upload is done; enqueue processing."""
    session = _get_session_or_404(session_id, current_user.id, db)

    storage = StorageService()
    file_size = storage.get_object_size(settings.s3_bucket_telemetry, session.raw_file_s3_key)
    if file_size is None:
        raise HTTPException(
            status_code=400,
            detail="We couldn't find your uploaded file. Please try uploading again.",
        )
    if file_size == 0:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty. Please try uploading again.",
        )
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if file_size > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=(
                f"This file is larger than {settings.max_upload_size_mb} MB. Large sessions "
                "can sometimes be split by iRacing — try uploading the most recent portion."
            ),
        )

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
        if session.processing_status == "failed":
            detail = session.processing_error or "This session failed to process and has no debrief."
            raise HTTPException(status_code=422, detail=detail)
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
