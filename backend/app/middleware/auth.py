"""
JWT authentication middleware.
Validates Supabase JWTs on protected routes and injects the user_id.
"""
import uuid
from typing import Any
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User

security = HTTPBearer()


def _decode_token(credentials: HTTPAuthorizationCredentials) -> dict[str, Any]:
    """Decode and verify a Supabase-issued JWT. Raises 401 on failure."""
    try:
        # Supabase JWTs are signed with the project JWT secret
        return jwt.decode(
            credentials.credentials,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}") from e


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> uuid.UUID:
    """Validates the Bearer JWT and returns the authenticated user's UUID."""
    payload = _decode_token(credentials)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(status_code=401, detail="Invalid token: no subject")
    return uuid.UUID(user_id_str)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Returns the full User record for the authenticated user.

    Supabase handles auth directly (the frontend never talks to our API to
    register) — so the first time a valid Supabase JWT reaches any endpoint,
    we sync it into our own `users` table if a row doesn't exist yet. Email
    and display name are pulled straight from the verified JWT claims.
    """
    payload = _decode_token(credentials)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(status_code=401, detail="Invalid token: no subject")
    user_id = uuid.UUID(user_id_str)

    user = db.query(User).filter(User.id == user_id).first()
    if user is not None:
        return user

    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token: no email claim")

    user_metadata = payload.get("user_metadata") or {}
    user = User(
        id=user_id,
        email=email,
        display_name=user_metadata.get("display_name"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
