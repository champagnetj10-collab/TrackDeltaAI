"""
JWT authentication middleware.
Validates Supabase JWTs on protected routes and injects the user_id.
"""
import uuid
from typing import Optional
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User

security = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> uuid.UUID:
    """
    Validates the Bearer JWT and returns the authenticated user's UUID.
    Raises 401 on invalid or expired tokens.
    """
    token = credentials.credentials

    try:
        # Supabase JWTs are signed with the project JWT secret
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
        user_id_str: Optional[str] = payload.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=401, detail="Invalid token: no subject")
        return uuid.UUID(user_id_str)

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}") from e


def get_current_user(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> User:
    """
    Returns the full User record for the authenticated user.
    Auto-creates the user record on first login (Supabase handles auth;
    we sync to our own users table on first API call).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User record not found. Complete registration first.")
    return user
