"""
TrackDelta AI — FastAPI Application Entry Point
"""
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import sessions, users, dna, subscriptions

# Every module below calls logging.getLogger(__name__) and logs at INFO
# (pipeline processing steps, DNA updates, etc.). Without this, Python's
# root logger defaults to WARNING and those INFO logs are silently dropped —
# on Railway (and any platform that just captures stdout/stderr) that means
# no visibility into what the pipeline is actually doing. This only adds
# visibility; it doesn't change any decision logic.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = FastAPI(
    title="TrackDelta AI API",
    description="The AI race engineer that understands the driver, not just the data.",
    version="0.1.0",
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url=None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Reformat FastAPI's default {"detail": ...} into the documented
    {"error": {"code", "message"}} shape (see CLAUDE.md API Conventions)."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": str(exc.status_code), "message": exc.detail}},
    )

# Routers
app.include_router(sessions.router, prefix="/v1")
app.include_router(users.router, prefix="/v1")
app.include_router(dna.router, prefix="/v1")
app.include_router(subscriptions.router, prefix="/v1")
# Stripe calls this directly — no /v1 prefix, no auth (webhook signature verifies instead).
app.include_router(subscriptions.webhook_router)


@app.get("/health", tags=["meta"])
def health_check():
    """Health check — used by Railway and load balancers."""
    return {"status": "ok", "service": "trackdelta-api", "version": "0.1.0"}


@app.get("/", tags=["meta"])
def root():
    return {"message": "TrackDelta AI API. Every Lap Better."}
