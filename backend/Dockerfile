FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# This is the ONE authoritative start command — railway.json deliberately
# does not define its own `deploy.startCommand`, so Railway runs this CMD
# directly rather than a second, possibly-conflicting definition.
#
# Shell form (no JSON array brackets) is required here, not a style choice:
# Docker always wraps a shell-form CMD in `/bin/sh -c "..."` and bakes that
# into the image at build time, which guarantees $PORT gets expanded by a
# real shell no matter how the container is invoked at runtime. An earlier
# version relied on railway.json's startCommand to supply $PORT instead —
# that field is a bare string Railway can invoke directly (exec-style,
# no shell), which produced `Error: Invalid value for '--port': '$PORT' is
# not a valid integer` because the literal text "$PORT" was passed straight
# to uvicorn's Click-based CLI with nothing to substitute it first.
#
# ${PORT:-8000} still falls back to 8000 if PORT is ever unset (e.g. a
# local `docker run` with no -e PORT=... passed) — not a hardcoded
# production port, just a default for that one local/manual case.
#
# PROCESS_TYPE branches the same image between the web service and the
# Celery worker service, both deployed from this one Dockerfile. Unset (or
# any value other than "worker") keeps the original uvicorn behavior, so
# the existing web service's deploy config needs no changes.
CMD if [ "$PROCESS_TYPE" = "worker" ]; then celery -A pipeline.worker worker --loglevel=info; else uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}; fi
