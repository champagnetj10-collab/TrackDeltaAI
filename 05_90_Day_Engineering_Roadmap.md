# TrackDelta AI — 90-Day Engineering Roadmap
**Document:** 05 of 05  
**Version:** 1.0  
**Status:** Engineering Reference  
**Date:** June 30, 2026

---

## Guiding Principles for This Roadmap

**Optimize for the most valuable product, not the most features.**

The goal of these 90 days is a single, verifiable outcome:

> *Delta consistently helps a competitive sim racer become measurably faster.*

Every sprint is evaluated against this outcome. If we are building things that do not contribute to it, we are building the wrong things.

**Dependencies are real.** The pipeline must exist before coaching can be tested. Coaching must work before the UI matters. Sequence matters more than speed.

**Scope is the enemy.** When in doubt, do less and do it correctly. A smaller product that earns trust is worth more than a larger product that fails quietly.

---

## Team

| Role | Focus |
|---|---|
| **Founder** | Product decisions, testing, user feedback, business operations, final approval on all coaching output |
| **Atlas** | Strategic product advisory, content quality review, Delta voice quality |
| **Lead Engineer** | Architecture, backend pipeline, frontend, coordination |

*Note: A small team with a clear roadmap can build this. The sequencing below is designed to be achievable. If additional engineering capacity becomes available, Phase 1 and Phase 2 can be parallelized more aggressively.*

---

## Milestone Overview

| Milestone | Target | Description |
|---|---|---|
| M1: Foundation | Week 2 | Infrastructure running; can authenticate and store data |
| M2: Pipeline Alpha | Week 5 | Can parse a real `.ibt` file and extract corner-level features |
| M3: DNA V1 | Week 8 | Driver DNA generates correctly after first session |
| M4: Coaching Engine | Week 10 | Structured coaching output generates from session features + DNA |
| M5: Delta V1 | Week 12 | First complete end-to-end debrief from upload to Delta's voice |
| M6: Beta Ready | Week 13 | Product is ready for 10 beta users from the iRacing community |

---

## Phase 0 — Foundation (Days 1–14)

### Objective
Everything needed to build exists, is documented, and works reliably. No feature work starts until this phase is complete.

### Sprint 0.1 — Repository & Tooling Setup (Days 1–4)

**Tasks:**
- [ ] Initialize monorepo structure: `/frontend`, `/backend`, `/pipeline`, `/docs`
- [ ] Frontend: Next.js 14 project with TypeScript, Tailwind CSS, ESLint configured
- [ ] Backend: FastAPI project structure with uvicorn, Pydantic, SQLAlchemy configured
- [ ] Docker Compose: PostgreSQL + Redis + API + Celery worker running locally
- [ ] GitHub repository with branch protection on `main`
- [ ] GitHub Actions: basic lint + test pipeline on PR
- [ ] `.env.example` file with all required variables documented
- [ ] Pre-commit hooks: Ruff (Python linting), ESLint (JS/TS)

**Definition of done:**
- `docker-compose up` brings up all services without errors
- `pytest` runs (no tests yet, but the framework is configured)
- `next dev` runs without errors
- CI pipeline runs on a test PR

---

### Sprint 0.2 — Data Layer & Auth (Days 5–10)

**Tasks:**
- [ ] Supabase project created (staging and production environments)
- [ ] Database schema implemented: `users`, `sessions`, `driver_dna`, `debriefs`, `conversations`, `tracks`, `track_corners`, `subscription_events`
- [ ] SQLAlchemy models matching schema
- [ ] Alembic migrations configured; initial migration created and tested
- [ ] Supabase Auth integrated into FastAPI (JWT verification middleware)
- [ ] Row-level security policies configured in Supabase
- [ ] S3 buckets created: `raw-telemetry`, `processed-features`, `debriefs`
- [ ] S3 client configured in backend; presigned URL generation tested
- [ ] Basic user CRUD endpoints: `GET /me`, `PATCH /me`
- [ ] Health check endpoint: `GET /health`

**Definition of done:**
- Can create a user in Supabase Auth, receive a JWT, and call authenticated endpoints
- Database schema matches spec; migrations run cleanly
- Presigned S3 URL generation tested manually

---

### Sprint 0.3 — Frontend Shell & Auth Flows (Days 11–14)

**Tasks:**
- [ ] Next.js app router structure: public routes + `/app/*` authenticated layout
- [ ] Supabase Auth client configured in frontend
- [ ] Registration page: form, submission, email verification state
- [ ] Login page: form, error handling, redirect to `/app/dashboard`
- [ ] Password reset flow: request page + reset page
- [ ] Email verification page (handles link from email)
- [ ] App shell: sidebar navigation, top bar, authenticated layout wrapper
- [ ] Dashboard page: empty state (no sessions yet)
- [ ] 404 and error pages
- [ ] Vercel project configured for staging environment

**Definition of done:**
- Complete auth flow works end-to-end: register → verify email → login → see dashboard
- Unauthenticated users redirected to /login from /app/* routes
- Deploys to Vercel staging without errors

**M1 — Foundation ✓**

---

## Phase 1 — Telemetry Pipeline (Days 15–35)

### Objective
Given a real `.ibt` file from iRacing, extract structured, meaningful features at the corner level. This is the technical foundation of everything that follows. Take the time to get it right.

### Sprint 1.1 — .ibt Parser (Days 15–21)

**Tasks:**
- [ ] Research and select `.ibt` parsing approach: evaluate `irsdk` Python library vs. custom binary parser
- [ ] Implement `TelemetryParser` class with full interface:
  - Input: S3 key of `.ibt` file
  - Output: `ParsedSession` (metadata + per-channel arrays)
- [ ] Extract and validate all required telemetry channels (see DNA Spec Section 2)
- [ ] Implement lap detection algorithm (complete lap identification from `LapDistPct`)
- [ ] Implement clean lap filtering (exclude incidents, outlier lap times, telemetry gaps)
- [ ] Unit tests with synthetic `.ibt` files:
  - Known-good session → assert correct metadata extraction
  - Session with incidents → assert incident laps excluded
  - Session with telemetry gap → assert gap laps excluded
- [ ] Manual test: parse a real iRacing session file, inspect output
- [ ] Celery task wrapper: `parse_telemetry_task(session_id)` → calls parser → stores result
- [ ] Session upload endpoint: `POST /sessions/upload-url` + `POST /sessions/{id}/upload-complete`
- [ ] Processing status endpoint: `GET /sessions/{id}/status`
- [ ] Upload UI in frontend: file dropzone, status polling, processing states display

**⚠️ Engineering challenge:** The `.ibt` format is binary and documented via the iRacing SDK. Read the SDK documentation carefully before writing the parser. Do not make assumptions about channel availability — some channels may not be present in all session types.

**Definition of done:**
- A real `.ibt` session file uploaded through the UI is parsed without error
- Clean lap count is correct (verified manually against iRacing's own session data)
- All required channels are present and correctly typed
- Unit tests pass

---

### Sprint 1.2 — Track Reference Data (Days 15–21, parallel)

*This work is partly parallelizable with 1.1 — track data can be built while the parser is being developed.*

**Tasks:**
- [ ] Design and document track reference schema (matches database schema in Architecture doc)
- [ ] Build track reference for Watkins Glen Full — the initial test track:
  - Define all corners with entry/apex/exit LapDistPct values
  - Classify each corner type
  - Set reference brake point (derived from analysis of iRacing community fast laps or team testing)
  - Set expected minimum speed at apex
- [ ] Build track reference for 4 additional priority tracks (target: 5 tracks total by end of Phase 1)
- [ ] Database seed script: load track + corner data into development and staging databases
- [ ] Admin endpoint (internal, auth-protected): `GET /tracks`, `GET /tracks/{id}` 
- [ ] Validation: manually verify corner boundaries using a parsed session telemetry file

**Definition of done:**
- 5 tracks seeded in the database with complete corner definitions
- Corner boundaries validated against real telemetry (correct LapDistPct values for at least 3 corners per track verified manually)

---

### Sprint 1.3 — Feature Extraction (Days 22–35)

**Tasks:**
- [ ] Implement `FeatureExtractionService`:
  - Corner segmentation from `LapDistPct` using track reference data
  - Braking features per corner per lap (see DNA Spec Section 4.3)
  - Throttle features per corner per lap
  - Speed features per corner per lap
  - Steering features per corner per lap
  - Session-level aggregations (mean, std_dev, trend)
  - Consistency metrics (lap time CV, hot lap percentage)
  - Session degradation metric (early vs. late pace)
- [ ] Handle edge cases:
  - Corner where braking data is incomplete (driver didn't brake — e.g., flat-out turn)
  - Corner at start/finish line where `LapDistPct` wraps
  - First and last lap partial corner data
- [ ] Unit tests with synthetic corner data:
  - Known late braker telemetry → assert brake_application_delta is positive
  - Known inconsistent lapper → assert lap_time_cv above threshold
  - Session with flat-out corner → assert braking features are null/zero, not error
- [ ] Integration test: full parse → extract pipeline on a real session file
- [ ] Store extracted features as JSON to S3 (`processed-features` bucket)
- [ ] Performance target: feature extraction for a 30-lap session completes in under 20 seconds

**Definition of done:**
- Full pipeline (parse → extract) runs on 3 real iRacing session files without error
- Feature output reviewed manually by Founder for sanity: values make intuitive sense for the sessions tested
- Unit tests pass
- Performance target met

**M2 — Pipeline Alpha ✓**

---

## Phase 2 — Driver DNA (Days 36–56)

### Objective
Driver DNA generates correctly from session features and updates meaningfully across multiple sessions. The internal model is accurate; the visible profile is honest.

### Sprint 2.1 — DNA Engine V1 (Days 36–46)

**Tasks:**
- [ ] Implement `DriverDNAEngine`:
  - Cold start: create empty DNA record for new driver
  - Attribute calculations (see DNA Spec Section 5.2):
    - Braking: style classification, mean brake delta, trail braking usage
    - Throttle: style classification, ramp rate, modulation
    - Consistency: score calculation formula
    - Risk: incident rate, classification (requires session data)
  - EWMA update logic (alpha = 0.3)
  - Confidence scoring per attribute (see DNA Spec Section 6.2)
  - Classification re-evaluation after each update
  - DNA versioning: mark previous as not current, create new version
- [ ] Unit tests:
  - 5 sessions of "late braker" telemetry → assert style = LATE
  - 5 sessions of high-consistency telemetry → assert score > 8.0
  - 1 session (cold start) → assert all confidences are Very Low
  - Consistency score formula: known CV → assert expected score
- [ ] Integrate DNA engine into Celery pipeline (step 3 after feature extraction)
- [ ] `GET /dna` endpoint returning current DNA for authenticated user
- [ ] DNA Profile page in frontend: displays current DNA with confidence indicators

**Definition of done:**
- DNA generates after first session (cold start) and updates correctly for subsequent sessions
- Unit tests pass
- DNA profile page displays in browser with correct confidence levels
- Founder tests with their own iRacing sessions: "The profile is starting to make sense"

---

### Sprint 2.2 — DNA Quality & Validation (Days 47–56)

**Tasks:**
- [ ] Build internal DNA validation tool:
  - Given a session + DNA output, produce a table of: "attribute → value → calculation trace"
  - Engineering-only; used to validate that DNA values are correct
- [ ] Validate DNA output against 3 real driver sessions (Founder drives known style, we verify DNA reflects it)
- [ ] Implement Pressure Performance attribute (requires multi-session data):
  - Early vs. late session pace delta
  - Classification thresholds
- [ ] Implement per-corner profile storage in DNA `track_profiles`
- [ ] Add confidence suppression logic: attributes below minimum threshold show "not enough data" in API response
- [ ] DNA version history endpoint: `GET /dna/history` (returns array of DNA snapshots with timestamps)
- [ ] DNA history chart in frontend (Pro-only): show how key attributes have changed over sessions
- [ ] Integration test: upload 5 sessions in sequence, verify DNA evolves correctly after each

**Definition of done:**
- Internal validation tool confirms DNA values are correct on 3 real-world session tests
- Pressure performance attribute generates after 5+ qualifying sessions
- Confidence suppression correctly hides low-confidence attributes from API
- DNA history shows correct evolution over multiple sessions

**M3 — Driver DNA V1 ✓**

---

## Phase 3 — Coaching Engine (Days 57–70)

### Objective
Given session features and DNA, produce a structured coaching output that a real race engineer would recognize as correct. This output becomes Delta's script.

### Sprint 3.1 — Core Coaching Logic (Days 57–65)

**Tasks:**
- [ ] Implement `CoachingEngine`:
  - Opportunity identification:
    - For each corner: calculate time loss estimate (vs. driver's own best)
    - Rank by estimated impact
    - Filter: minimum confidence threshold, minimum time loss threshold (5 ms)
    - Select top 2–3
    - Generate opportunity text data: corner name, observation, impact, recommendation template
  - Strength identification:
    - Identify corners where driver consistently exceeds their median (positive speed delta)
    - Identify DNA attributes with High confidence and strong classification
    - Select top 2–3 strengths
  - Time available estimate:
    - Sum top 3 opportunity time losses
    - Apply confidence adjustment (multiply by 0.7 for Moderate confidence, 0.5 for Low)
    - Return as [min, max] range with confidence label
    - Suppress if overall confidence is Very Low (Session 1)
  - Practice plan generation:
    - Map each opportunity to a specific, structured practice objective
    - Sequence by impact
    - Return 3–5 items
  - One clear objective: highest-impact, most-actionable item from practice plan
  - DNA update summary: what changed this session (attribute deltas, confidence changes)
- [ ] Unit tests:
  - Known session with braking issue at T7 → assert T7 is in top opportunities
  - Session with insufficient data → assert time_available is suppressed
  - Known strength in high-speed corners → assert high-speed strength identified
- [ ] Coaching output validation:
  - Founder reviews structured coaching output from 3 real sessions
  - Assessment: "Does this output, if spoken aloud by a real engineer, make sense?"

**Definition of done:**
- Coaching engine produces structured output for all 5 test track sessions
- Founder review passes: structured output is correct and actionable for all 3 validation sessions
- Unit tests pass

---

### Sprint 3.2 — Coaching Output Refinement (Days 66–70)

**Tasks:**
- [ ] Edge case handling:
  - Session with no clear opportunities (all corners within threshold): output "session was strong, here are incremental improvements"
  - Session on track with no corner reference data: graceful degradation
  - First session (cold start): adjusted output acknowledging low DNA confidence throughout
- [ ] Recommendation text templates:
  - Build a library of specific, actionable recommendation templates per coaching scenario
  - Template parameters: corner name, measured delta, suggested change
  - Example: "At {corner_name}, your brake point averaged {delta_m} meters earlier than your 3 fastest laps. Try moving your brake point {target_delta_m} meters later and maintaining light brake pressure through turn-in."
- [ ] Coach output schema validation: enforce that all required fields are present before passing to LLM
- [ ] Full pipeline integration test: upload → parse → extract → DNA → coaching in one flow

**Definition of done:**
- All edge cases handled gracefully (no unhandled exceptions in any test session)
- Recommendation templates reviewed and approved by Founder
- Full pipeline integration test passes on 5 sessions across 3 tracks

**M4 — Coaching Engine ✓**

---

## Phase 4 — Delta's Voice (Days 71–84)

### Objective
Convert structured coaching output into Delta's natural language debrief. The coaching must sound like a real, trusted race engineer — not a language model summarizing data.

### Sprint 4.1 — LLM Integration & Prompt Engineering (Days 71–78)

**Tasks:**
- [ ] Anthropic API client setup with retry logic and error handling
- [ ] Design and implement Delta's system prompt:
  - Character definition (calm, professional, honest, specific)
  - Voice prohibitions ("never start with a compliment", "never invent data")
  - Confidence communication rules
  - Formatting requirements (section structure)
- [ ] Build structured prompt builder: converts `CoachingOutput + DNA + SessionMetadata` → prompt
- [ ] Initial debrief generation tested on 3 sessions
- [ ] Founder + Atlas review: read generated debriefs and assess quality
  - Does Delta sound like a real engineer?
  - Is the coaching specific (references corners by name)?
  - Are confidence levels communicated correctly?
  - Are there any invented observations not present in the coaching data?
- [ ] Iterate on system prompt and prompt structure based on review
- [ ] Target: 3 rounds of review + iteration

**⚠️ This sprint requires tight collaboration between engineering and the Founder/Atlas.** The quality of Delta's voice is a product decision, not just an engineering one. Build in review cycles.

**Definition of done:**
- 3 debrief generations reviewed and approved by Founder and Atlas
- No invented data in any approved debrief
- Confidence levels correctly communicated in all sections
- Time to generate: under 15 seconds

---

### Sprint 4.2 — Debrief Storage, Display & Full Pipeline (Days 79–84)

**Tasks:**
- [ ] Store generated debrief in database (`debriefs` table)
- [ ] Log LLM usage: model, tokens, cost per debrief
- [ ] `GET /sessions/{id}/debrief` endpoint returns stored debrief
- [ ] Debrief page in frontend:
  - Session header section
  - Delta overview section
  - Opportunities section (expandable cards)
  - Strengths section
  - Time available card (with confidence display)
  - DNA update section
  - Practice plan section
  - One clear objective (prominent, bold)
- [ ] Processing completion state: redirect user from upload page to debrief when ready
- [ ] Full end-to-end test: upload a real session → receive complete debrief in browser
- [ ] Measure total pipeline time: target under 90 seconds from upload complete to debrief available

**Definition of done:**
- Complete end-to-end flow works: file upload → processing → debrief displayed in browser
- Debrief UI is readable and well-formatted on desktop
- Total pipeline time under 90 seconds on a 30-lap session
- Founder runs the full flow with their own session: "This is the product"

**M5 — Delta V1 ✓**

---

## Phase 5 — Subscription, Polish & Beta (Days 85–90)

### Objective
The product is complete enough for 10 real users. It handles errors gracefully, enforces subscription limits, and is something we're proud to put in front of our first beta drivers.

### Sprint 5.1 — Subscription System (Days 85–87)

**Tasks:**
- [ ] Stripe integration:
  - Products and prices configured in Stripe (monthly + annual Pro)
  - Checkout session endpoint: `POST /subscriptions/checkout`
  - Customer portal endpoint: `POST /subscriptions/portal`
  - Webhook handler: `POST /webhooks/stripe`
    - Handle: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.payment_failed`
- [ ] Free tier enforcement:
  - Monthly upload counter (reset on 1st of month)
  - Upload blocked with clear message when limit reached
  - Usage indicator in upload UI
- [ ] Pro feature gating:
  - Delta conversations: blocked for Free users with upgrade prompt
  - Session history: Free users see last 5 only
  - DNA history: Pro only
- [ ] Billing page in frontend: current plan, usage, upgrade CTA, manage billing link

**Definition of done:**
- Complete upgrade flow works end-to-end (checkout → Pro access)
- Free tier limit is enforced and tested
- Subscription cancellation works
- Failed payment downgrades correctly after grace period

---

### Sprint 5.2 — Delta Conversations (Days 85–88, parallel)

**Tasks:**
- [ ] Conversation endpoint: `POST /debriefs/{id}/conversations`
- [ ] Message endpoint: `POST /conversations/{id}/messages`
- [ ] LLM conversation handler:
  - Context injection: current session debrief + DNA + driver profile
  - Delta character enforcement in conversation context
  - 20-message limit enforced
  - Out-of-scope question handling: "I can only work with what's in your telemetry data"
- [ ] Conversation UI in frontend (Pro only):
  - Chat interface below debrief
  - Pro gate: upgrade prompt for Free users
  - Loading state for responses
  - Message limit indicator

**Definition of done:**
- Delta can answer 5 test follow-up questions correctly using session context
- Delta stays in character for all test questions
- Delta responds correctly to out-of-scope questions
- 20-message limit enforced

---

### Sprint 5.3 — Error Handling, Onboarding & Beta Readiness (Days 88–90)

**Tasks:**
- [ ] Onboarding flow implemented in frontend (4-question survey + DNA introduction)
- [ ] All error states implemented (see User Journey doc Section 4):
  - Invalid file upload
  - Insufficient laps
  - Unknown track (reduced debrief)
  - Processing failure (with retry)
  - Duplicate upload detection
- [ ] Session history page with Free/Pro gating
- [ ] Basic account settings page
- [ ] Email: verification, password reset (Resend configured)
- [ ] Test on 3 real iRacing sessions end-to-end, including:
  - First-time user onboarding flow
  - 3 sequential sessions (verify DNA evolves correctly)
  - Error state: upload a non-.ibt file (verify graceful error)
  - Free tier upload limit reached (verify enforcement)
  - Pro upgrade flow (verify access unlocks)
- [ ] Bug fixes from testing
- [ ] Deploy to production environment
- [ ] Monitoring and alerts configured (Sentry, logging)

**Definition of done (Beta Ready):**
All of the following are true:

- [ ] A new user can register, complete onboarding, and upload their first session without assistance
- [ ] The full debrief generates correctly for all 5 test tracks
- [ ] Driver DNA updates correctly over 3 sequential sessions
- [ ] All error states display a clear, honest message — no raw errors shown to users
- [ ] Free tier limits are enforced correctly
- [ ] Pro upgrade works end-to-end
- [ ] Delta conversations work for Pro users
- [ ] Session history is paginated and gated correctly
- [ ] Application deployed to production and accessible
- [ ] Monitoring is active — errors are being logged and alerted

**M6 — Beta Ready ✓**

---

## Day-by-Day Summary

| Days | Focus | Milestone |
|---|---|---|
| 1–4 | Repository, tooling, Docker setup | — |
| 5–10 | Database schema, auth, S3 integration | — |
| 11–14 | Frontend shell, auth flows | **M1: Foundation** |
| 15–21 | .ibt parser + track reference data (parallel) | — |
| 22–35 | Feature extraction, pipeline integration | **M2: Pipeline Alpha** |
| 36–46 | Driver DNA engine V1 | — |
| 47–56 | DNA validation, edge cases, frontend DNA page | **M3: DNA V1** |
| 57–65 | Coaching engine core logic | — |
| 66–70 | Coaching refinement, templates, integration | **M4: Coaching Engine** |
| 71–78 | LLM integration, Delta prompt engineering, review | — |
| 79–84 | Debrief storage, display, end-to-end flow | **M5: Delta V1** |
| 85–88 | Subscription system + Delta conversations | — |
| 88–90 | Onboarding, error handling, beta testing | **M6: Beta Ready** |

---

## Beta Launch Plan (Day 90+)

Once M6 is achieved:

**Beta cohort:** 10 competitive iRacing drivers
- Recruited from: Discord leagues, Reddit (r/iRacing, r/simracing), direct outreach from Founder's network
- Target profile: 1,500–4,000 iRating, active league racer, willing to give honest feedback
- Commitment: upload at least 4 sessions over 3 weeks; provide written feedback

**Beta success criteria:**
- 8 of 10 drivers return after their first debrief (upload at least one more session)
- 6 of 10 drivers show measurable improvement in lap time at a given track across the beta period
- At least 3 drivers say, unprompted: "This is different from what I've tried before"
- No critical bugs that prevent a debrief from completing

**Feedback collection:**
- After first debrief: 3-question survey ("Did Delta identify what was actually wrong?" / "How specific was the coaching?" / "Would you use this regularly?")
- After 2+ weeks: 15-minute call with Founder
- Exit survey: NPS + open-ended feedback

**What we do with beta feedback:**
- Coaching quality issues → coaching engine + LLM prompt iteration
- Delta voice issues → prompt engineering iteration
- UI friction points → frontend polish Sprint
- Missing features → evaluated against "does this help drivers improve?" filter before adding

---

## Risks to the Roadmap

| Risk | Probability | Impact | Response |
|---|---|---|---|
| `.ibt` parser takes longer than estimated | Medium | High | Allocate buffer in Sprint 1.1; research irsdk thoroughly before writing custom code |
| Track reference data quality is poor | Medium | High | Validate against real telemetry before proceeding to feature extraction; factor in extra time |
| LLM prompt engineering takes more iterations | High | Medium | Plan for 3+ revision cycles in Sprint 4.1; Atlas and Founder must be available for review |
| Coaching engine outputs feel generic | Medium | High | Validate after coaching engine (M4) before LLM layer — generic issues are coaching engine problems, not LLM problems |
| Supabase or Railway has unexpected limitations | Low | Medium | Test infrastructure thoroughly in Phase 0; identify issues early |
| 90 days is not enough | Medium | Medium | Prioritize M5 (Delta V1) above all else; M6 polish can extend into beta period if needed; the MVP is "can Delta produce a debrief", not "is every feature polished" |

---

## What We Are Not Building in 90 Days

This is a reminder. When a great idea surfaces during development, it goes here.

- Desktop auto-upload companion app
- ACC support
- Real-time coaching
- Mobile application
- Video analysis
- Setup recommendations
- Peer comparison / leaderboards
- Team portal
- iRacing API integration (beyond file-based)
- Email session reports
- Automated session notifications (push/email)

These are sequenced for Phase 2+. Building any of them before M6 is a distraction from the mission.

---

## Closing Note

Ninety days is enough time to prove one thing: that Delta can make drivers faster.

If we prove that, we have the foundation to build everything else. If we do not prove that, no amount of additional features will save the product.

Build the debrief. Build the DNA. Make Delta sound like a real engineer. Get it in front of 10 drivers who care.

Everything else can wait.

*Every Lap Better.*
