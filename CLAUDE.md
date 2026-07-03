# TrackDelta AI — Engineering Briefing for Claude Code

This document exists so Claude Code has full context when opening this project.
Read it before writing any code.

---

## What We're Building

TrackDelta AI is the world's first AI race engineer that understands the driver — not just the data.

**Delta** is the AI race engineer at the center of the product. Delta analyzes iRacing telemetry sessions and delivers personalized coaching debriefs grounded in each driver's unique **Driver DNA** — a continuously evolving model of how they brake, steer, apply throttle, handle pressure, and learn.

**Mission:** Help every racing driver become the best version of themselves.
**North star metric:** Measurable lap time improvement after 4+ sessions with Delta.

---

## Founding Principles (Apply to Every Line of Code)

- **Drivers First.** Every feature must help a driver become faster, more consistent, or more confident.
- **Truth Over Confidence.** If Delta doesn't know something, it says so. Confidence levels are always communicated.
- **Coach, Don't Judge.** Delta coaches based on the driver's own tendencies, not a generic ideal.
- **Personalization Over Generalization.** Generic coaching is worthless. Everything references this driver's data.
- **Simplicity Before Complexity.** Build the simplest correct thing. Optimize later.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS |
| Backend API | Python FastAPI + Uvicorn |
| Task Queue | Celery + Redis |
| Database | PostgreSQL (Supabase) + SQLAlchemy + Alembic |
| File Storage | AWS S3 (raw telemetry + processed features) |
| Auth | Supabase Auth (JWT) |
| LLM | Anthropic Claude API |
| Payments | Stripe |
| Email | Resend |
| Frontend Hosting | Vercel |
| Backend Hosting | Railway |

---

## Repository Structure

```
trackdelta/
├── frontend/          # Next.js 14 web application
├── backend/           # FastAPI REST API
├── pipeline/          # Celery async processing pipeline
├── docs/              # Product and architecture documentation
├── .github/workflows/ # GitHub Actions CI
├── docker-compose.yml # Local development environment
├── .env.example       # All required environment variables (documented)
└── CLAUDE.md          # This file
```

---

## The Processing Pipeline (Most Important Architecture Decision)

Intelligence lives in the engineering layer. The LLM is the voice, not the brain.

```
.ibt Upload → S3
    ↓
Telemetry Parser     (ibt_parser.py)    — parse binary .ibt format
    ↓
Feature Extractor    (feature_extractor.py) — per-corner braking/throttle/speed/steering
    ↓
Driver DNA Engine    (dna_engine.py)    — EWMA update, classification, confidence scoring
    ↓
Coaching Engine      (coaching_engine.py) — identify opportunities, strengths, time estimate
    ↓
Delta Voice (LLM)    (delta_voice.py)   — Anthropic API → natural language debrief
    ↓
Store debrief → Notify user
```

**Never pass raw telemetry to the LLM.** The LLM only receives structured coaching output + DNA summary.

---

## Current Phase: Phase 0 — Foundation

**Goal:** Infrastructure ready; auth working; database schema deployed; Docker Compose running.

### Sprint 0.1 — Tooling (Days 1–4) ← WE ARE HERE
- [x] Monorepo structure
- [x] Next.js 14 frontend scaffold
- [x] FastAPI backend scaffold
- [x] Pipeline skeleton
- [x] Docker Compose (PostgreSQL + Redis + API + Worker)
- [x] .env.example
- [x] GitHub Actions CI
- [ ] Pre-commit hooks

### Sprint 0.2 — Data Layer & Auth (Days 5–10)
- [ ] Supabase project created
- [ ] Database migrations run (Alembic)
- [ ] Supabase Auth wired to FastAPI JWT middleware
- [ ] S3 buckets created and configured
- [ ] `GET /health` and `GET /me` endpoints working

### Sprint 0.3 — Frontend Shell (Days 11–14)
- [ ] Registration / login / password reset flows
- [ ] Authenticated app shell with navigation
- [ ] Dashboard empty state
- [ ] Deploy to Vercel staging

---

## Database Schema Overview

Key tables (full schema in `backend/alembic/versions/001_initial_schema.py`):

- `users` — accounts, subscription tier, monthly upload counter
- `sessions` — uploaded .ibt sessions, processing status, metadata
- `driver_dna` — versioned DNA snapshots per driver (JSONB attributes)
- `debriefs` — stored coaching debrief content (JSONB)
- `conversations` + `conversation_messages` — Delta chat history
- `tracks` + `track_corners` — track reference data (corner definitions)
- `subscription_events` — Stripe webhook events

---

## API Conventions

- Base: `/v1/`
- Auth: `Authorization: Bearer <supabase_jwt>`
- Errors: `{ "error": { "code": "string", "message": "string" } }`
- All endpoints require auth except `/health` and `/webhooks/stripe`

---

## Delta's Character (Critical — Never Violate)

Delta is a calm, professional, trusted AI race engineer. When generating any Delta-facing output:

- **DO:** Reference specific corners by name. Cite data. Use ranges for estimates. Communicate confidence.
- **DO:** Say "I don't know" or "I need more data" when true.
- **DON'T:** Start with compliments ("Great session!"). Invent data. State false precision. Use filler phrases.
- **DON'T:** Sound like a chatbot. Sound like a race engineer.

---

## Key Files to Know

| File | Purpose |
|---|---|
| `backend/app/main.py` | FastAPI app entry point |
| `backend/app/config.py` | All settings from env vars |
| `backend/app/database.py` | SQLAlchemy engine + session |
| `backend/alembic/versions/001_initial_schema.py` | Full DB schema |
| `pipeline/tasks/process_session.py` | Main Celery task orchestrator |
| `pipeline/parser/ibt_parser.py` | iRacing .ibt binary parser (Phase 1) |
| `pipeline/dna/dna_engine.py` | Driver DNA EWMA update logic (Phase 2) |
| `pipeline/coaching/coaching_engine.py` | Coaching output generation (Phase 3) |
| `pipeline/llm/delta_voice.py` | Anthropic API integration (Phase 4) |
| `frontend/app/(app)/sessions/[id]/page.tsx` | Debrief display page |
| `frontend/app/(app)/dna/page.tsx` | Driver DNA profile page |

---

## Full Documentation

All product and architecture decisions are documented in `/docs/`:
- `PRD.md` — Product Requirements Document
- `01_MVP_Feature_Specification.md`
- `02_User_Journey.md`
- `03_Driver_DNA_Technical_Specification.md`
- `04_System_Architecture.md`
- `05_90_Day_Engineering_Roadmap.md`

When making architectural decisions, check these documents first.

---

## Running Locally

```bash
# Start all services
docker-compose up

# Backend runs at: http://localhost:8000
# Frontend runs at: http://localhost:3000
# API docs at:     http://localhost:8000/docs

# Run backend separately
cd backend && uvicorn app.main:app --reload

# Run frontend separately
cd frontend && npm run dev

# Run Celery worker
cd backend && celery -A pipeline.worker worker --loglevel=info
```

---

*Every Lap Better.*
