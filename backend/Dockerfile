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

# Default: run the API. Shell form (not exec-array form) so $PORT actually
# expands — Railway injects PORT at runtime and expects the process to bind
# to it. railway.json's startCommand already does this explicitly, but this
# fallback keeps the image correct even if run directly (e.g. `docker run`)
# or on a platform that invokes the image's own CMD instead of an override.
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
