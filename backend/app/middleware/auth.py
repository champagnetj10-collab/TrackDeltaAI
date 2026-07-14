"""
JWT authentication middleware.
Validates Supabase JWTs on protected routes and injects the user_id.

Supabase projects created after their asymmetric-keys rollout sign access
tokens with ES256 using a per-project JWKS (no shared secret exists to
configure) rather than the legacy HS256 + static "JWT secret" scheme. This
verifies against whichever the project actually uses: if
SUPABASE_JWT_SECRET is configured, HS256 is used (legacy projects);
otherwise the JWKS published at {SUPABASE_URL}/auth/v1/.well-known/jwks.json
is fetched, cached, and used for ES256 verification (current projects).
"""
import time
import uuid
from typing import Any

import httpx
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User

security = HTTPBearer()

_JWKS_CACHE_TTL_S = 3600
_jwks_cache: dict[str, Any] = {"keys": [], "fetched_at": 0.0}


def _fetch_jwks(force: bool = False) -> list[dict[str, Any]]:
    now = time.monotonic()
    if force or not _jwks_cache["keys"] or (now - _jwks_cache["fetched_at"]) > _JWKS_CACHE_TTL_S:
        url = f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
        response = httpx.get(url, timeout=5.0)
        response.raise_for_status()
        _jwks_cache["keys"] = response.json().get("keys", [])
        _jwks_cache["fetched_at"] = now
    return _jwks_cache["keys"]


def _find_jwk(kid: str | None) -> dict[str, Any] | None:
    for key in _fetch_jwks():
        if key.get("kid") == kid:
            return key
    # Key rotation: refetch once in case a new signing key was published.
    for key in _fetch_jwks(force=True):
        if key.get("kid") == kid:
            return key
    return None


def _decode_token(credentials: HTTPAuthorizationCredentials) -> dict[str, Any]:
    """Decode and verify a Supabase-issued JWT. Raises 401 on failure."""
    token = credentials.credentials

    if settings.supabase_jwt_secret:
        try:
            return jwt.decode(
                token, settings.supabase_jwt_secret,
                algorithms=["HS256"], options={"verify_aud": False},
            )
        except JWTError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {e}") from e

    try:
        header = jwt.get_unverified_header(token)
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}") from e

    alg = header.get("alg", "ES256")
    jwk = _find_jwk(header.get("kid"))
    if jwk is None:
        raise HTTPException(status_code=401, detail="Invalid token: unknown signing key")

    try:
        return jwt.decode(token, jwk, algorithms=[alg], options={"verify_aud": False})
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
