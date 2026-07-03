# TrackDelta — developer convenience targets
# Usage: make <target>

.PHONY: help up down api worker migrate lint test frontend-dev

help:
	@echo ""
	@echo "TrackDelta development commands:"
	@echo ""
	@echo "  make up           Start all local services (postgres, redis, api, worker)"
	@echo "  make down         Stop and remove containers"
	@echo "  make migrate      Run Alembic migrations"
	@echo "  make lint         Lint backend (ruff) + frontend (eslint)"
	@echo "  make test         Run backend tests"
	@echo "  make api          Start API server only (requires postgres + redis)"
	@echo "  make worker       Start Celery worker only"
	@echo "  make frontend-dev Start Next.js dev server"
	@echo ""

up:
	docker compose up

down:
	docker compose down

migrate:
	docker compose run --rm migrate

api:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

worker:
	cd backend && celery -A pipeline.worker worker --loglevel=info

lint:
	cd backend && ruff check .
	cd frontend && npm run lint

test:
	cd backend && pytest -v

frontend-dev:
	cd frontend && npm run dev
