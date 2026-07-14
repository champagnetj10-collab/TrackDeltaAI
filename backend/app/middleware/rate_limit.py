"""
Lightweight Redis-backed rate limiting.

Fixed-window counter per (scope, user) keyed in Redis. Fails open — if Redis
is unreachable (e.g. local dev without `docker-compose up`), the request is
allowed through rather than raising, consistent with this codebase's other
graceful-degradation points (CELERY_TASK_ALWAYS_EAGER, lazy Anthropic/Stripe
validation). This is abuse mitigation for beta, not a security boundary.

Keyed by authenticated user ID rather than IP — every rate-limited endpoint
here requires auth, and what actually matters is one account hammering
uploads or Stripe calls, not raw per-IP traffic.
"""
import logging
import time

import redis
from fastapi import Depends, HTTPException

from app.config import settings
from app.middleware.auth import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

_redis_client: redis.Redis | None = None


def _get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(
            settings.redis_url, socket_connect_timeout=1, socket_timeout=1
        )
    return _redis_client


def _check(key: str, limit: int, window_seconds: int) -> None:
    bucket = int(time.time()) // window_seconds
    redis_key = f"ratelimit:{key}:{bucket}"
    try:
        client = _get_redis()
        count = client.incr(redis_key)
        if count == 1:
            client.expire(redis_key, window_seconds)
    except redis.RedisError as exc:
        logger.warning("Rate limiter: Redis unavailable, allowing request through (%s)", exc)
        return

    if count > limit:
        raise HTTPException(
            status_code=429,
            detail=f"Too many requests — try again in a moment (limit: {limit} per {window_seconds}s).",
        )


def rate_limit(limit: int, window_seconds: int, scope: str):
    """FastAPI dependency factory — use in a route's `dependencies=[...]`:

        @router.post("/upload-url", dependencies=[rate_limit(10, 60, "upload-url")])

    `current_user` here reuses FastAPI's per-request dependency cache, so this
    doesn't re-run JWT verification if the route already depends on it.
    """
    def _dependency(current_user: User = Depends(get_current_user)) -> None:
        _check(f"{scope}:{current_user.id}", limit, window_seconds)
    return Depends(_dependency)
