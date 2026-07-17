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
| File Storage | Supabase Storage (native REST API — raw telemetry + processed features + debriefs). Not AWS S3, despite the `s3_bucket_*` setting names in `config.py`; those are just bucket-name strings, no AWS credentials involved. See `app/services/storage.py`. |
| Auth | Supabase Auth (JWT — JWKS/ES256 for current projects, HS256 fallback for legacy) |
| LLM | Anthropic Claude API |
| Payments | Stripe |
| Email | Supabase Auth's built-in email delivery (verification, password reset) — not Resend. `RESEND_API_KEY` exists in config but no code calls the Resend API; it's unused. See "Known Gaps" below. |
| Frontend Hosting | Vercel (live at `frontend-nine-xi-85.vercel.app`, project `trackdelta/frontend`) |
| Backend Hosting | Railway (live at `trackdeltaai-production.up.railway.app`, auto-deploys on push to `master`) |

---

## Repository Structure

```
trackdelta/
├── frontend/          # Next.js 14 web application
├── backend/
│   ├── app/            # FastAPI REST API
│   ├── pipeline/        # Celery async processing pipeline (parser, DNA, coaching, LLM voice)
│   ├── alembic/         # DB migrations
│   ├── tests/
│   └── scripts/validate_ibt.py  # manual real-.ibt validation tool (see "Known Gaps")
├── marketing/          # Content/growth playbooks — not engineering, see marketing/README.md
├── .github/workflows/  # GitHub Actions CI (runs on push/PR to master)
├── docker-compose.yml  # Local development environment
├── .env.example        # All required environment variables (documented)
└── CLAUDE.md           # This file
```

Product/architecture docs (`PRD`, `MVP Feature Spec`, `User Journey`, `Driver DNA Spec`,
`System Architecture`, `90-Day Roadmap`) live as `.md` files at the **repo root**, not in a
`docs/` directory — an empty `docs/` and empty top-level `pipeline/` still exist as inert
leftovers from the original scaffold; the real pipeline code has always lived under
`backend/pipeline/`, co-located with the API for a single Railway service/Dockerfile.

---

## The Processing Pipeline (Most Important Architecture Decision)

Intelligence lives in the engineering layer. The LLM is the voice, not the brain.

```
.ibt Upload → Supabase Storage
    ↓
Telemetry Parser     (backend/pipeline/parser/ibt_parser.py)     — parse binary .ibt format
    ↓
Feature Extractor    (backend/pipeline/extraction/feature_extractor.py) — per-corner braking/throttle/speed/steering
    ↓
Driver DNA Engine    (backend/pipeline/dna/dna_engine.py)        — EWMA update, classification, confidence scoring
    ↓
Coaching Engine      (backend/pipeline/coaching/coaching_engine.py) — identify opportunities, strengths, time estimate
    ↓
Delta Voice (LLM)    (backend/pipeline/llm/delta_voice.py)       — Anthropic API → natural language debrief
    ↓
Store debrief → Notify user
```

**Never pass raw telemetry to the LLM.** The LLM only receives structured coaching output + DNA summary.

All five stages are fully implemented and unit-tested (104 backend tests, all synthetic/mocked
data). **None of it has been run against a real .ibt file or a real Anthropic/Stripe call** —
see "Known Gaps" below before treating this as production-validated.

---

## Current Phase: Beta Readiness

Phase 0 (Foundation) through Phase 4 (LLM voice) are all implemented. The product's full
telemetry-to-debrief pipeline exists, is unit-tested, and both the backend (Railway) and
frontend (Vercel) are live in production against a real Supabase project (migrations
applied, RLS enabled, storage buckets created).

**What's done:**
- [x] Monorepo structure, Next.js 14 frontend, FastAPI backend, Celery pipeline skeleton
- [x] Supabase project created; migrations 001 (schema) + 002 (RLS) applied to production
- [x] Supabase Auth wired to FastAPI JWT middleware (JWKS + legacy HS256)
- [x] Supabase Storage buckets created and configured (`trackdelta-raw-telemetry`,
      `trackdelta-processed-features`, `trackdelta-debriefs`)
- [x] `GET /health` and `GET /me` live in production
- [x] Registration / login / password reset flows, authenticated app shell, dashboard
- [x] Backend deployed to Railway (auto-deploy on push to `master`), CI green on both jobs
- [x] Terms of Service / Privacy Policy pages, branded 404/error pages
- [x] Frontend deployed to Vercel (`frontend-nine-xi-85.vercel.app`); Railway's
      `FRONTEND_URL` and `CORS_ORIGINS` point at it and are verified working (preflight
      returns `access-control-allow-origin` for the real domain)
- [x] Redis-backed rate limiting on session upload and Stripe checkout/portal endpoints
      (fails open if Redis is unreachable — see `app/middleware/rate_limit.py`)

**Known Gaps — required before opening the beta:**
- [ ] **Real `.ibt` file validation — PENDING INTEGRATION TESTING.** The parser, feature
      extractor, DNA engine, and coaching engine have only ever run against synthetically
      constructed test fixtures (104+ passing unit tests) — never a real iRacing telemetry
      dump. `backend/scripts/validate_ibt.py` exists specifically for this and has not yet
      been run. **Do not treat the parser as trustworthy until this has been done and its
      output manually cross-checked** against a remembered real session (track/car/lap
      times/top speed) — see the script's own docstring for what a clean run does and does
      not prove. Deliberately deferred until a real .ibt file is available (per user
      decision) — do this before opening the beta.
- [ ] Stripe checkout/portal/webhook has never been exercised against a real Stripe account
      (only a fake/mocked client in tests) — see `app/routers/subscriptions.py` docstring.
      `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` is still a placeholder on Vercel.
- [ ] `delta_voice.py` (the Anthropic integration) has never called the real Anthropic API —
      only a fake injected client in tests.
- [ ] `tracks` / `track_corners` reference data is completely empty in production — corner-
      level coaching features degrade to session-level-only until this is seeded.
- [ ] Email is fully handled by Supabase Auth's own shared SMTP (low rate limits, generic
      `noreply@...` sender). For beta-scale signups with a branded sender address, configure
      a custom SMTP provider in Supabase's Auth settings (Resend is already in the tech
      stack/config for this purpose, just not wired up anywhere yet).
- [ ] No error-monitoring/observability tooling (e.g. Sentry) configured yet.
- [ ] No custom domain — frontend is on its `*.vercel.app` URL, backend on its
      `*.up.railway.app` URL. Fine for beta; revisit before public launch.

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
| `backend/alembic/versions/002_row_level_security.py` | RLS policies (defense-in-depth; backend connects as table-owner and bypasses these) |
| `backend/app/middleware/auth.py` | Supabase JWT verification (JWKS/HS256) |
| `backend/app/middleware/rate_limit.py` | Redis-backed rate limiting (fails open) |
| `backend/app/services/storage.py` | Supabase Storage integration |
| `backend/pipeline/tasks/process_session.py` | Main Celery task orchestrator |
| `backend/pipeline/parser/ibt_parser.py` | iRacing .ibt binary parser — **unvalidated against real data, see Known Gaps** |
| `backend/pipeline/dna/dna_engine.py` | Driver DNA EWMA update logic |
| `backend/pipeline/coaching/coaching_engine.py` | Coaching output generation |
| `backend/pipeline/llm/delta_voice.py` | Anthropic API integration — never called against the real API |
| `backend/scripts/validate_ibt.py` | Manual diagnostic for validating the parser against a real `.ibt` file |
| `frontend/app/(app)/sessions/[id]/page.tsx` | Debrief display page |
| `frontend/app/(app)/dna/page.tsx` | Driver DNA profile page |

---

## Full Documentation

Product and architecture docs live as `.md` files at the **repo root** (not `/docs/` —
see "Repository Structure" above):
- `TrackDelta_AI_PRD.md` — Product Requirements Document
- `01_MVP_Feature_Specification.md`
- `02_User_Journey.md`
- `03_Driver_DNA_Technical_Specification.md`
- `04_System_Architecture.md`
- `05_90_Day_Engineering_Roadmap.md`
- `ROADMAP.md` — a newer/separate roadmap doc; check both this and `05_90_Day_...` for now
  since they haven't been reconciled into one authoritative source

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
