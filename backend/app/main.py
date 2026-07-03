"""
TrackDelta AI — FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import sessions, users, dna

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

# Routers
app.include_router(sessions.router, prefix="/v1")
app.include_router(users.router, prefix="/v1")
app.include_router(dna.router, prefix="/v1")


@app.get("/health", tags=["meta"])
def health_check():
    """Health check — used by Railway and load balancers."""
    return {"status": "ok", "service": "trackdelta-api", "version": "0.1.0"}


@app.get("/", tags=["meta"])
def root():
    return {"message": "TrackDelta AI API. Every Lap Better."}
