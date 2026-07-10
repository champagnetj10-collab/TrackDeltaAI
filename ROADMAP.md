# TrackDelta AI — Roadmap: MVP to Version 1.0

**Status:** Engineering Reference
**Date:** July 10, 2026
**Owner:** Lead Engineer (with Founder approval on all gates; Atlas advisory on Delta voice/coaching quality)
**Companion documents:** `TrackDelta_AI_PRD.md`, `01_MVP_Feature_Specification.md`, `03_Driver_DNA_Technical_Specification.md`, `04_System_Architecture.md`, `05_90_Day_Engineering_Roadmap.md`

---

## How to Read This Document

`05_90_Day_Engineering_Roadmap.md` covers Day 0 → Beta Ready (its milestones M1–M6). This document picks up from where the codebase actually is today and carries the product to **Version 1.0**. Each milestone states:
- **Depends on** — what must already be true before it can start
- **Deliverables** — the concrete things that get built or decided
- **Effort estimate** — engineer-time for a small team (1 lead engineer, Founder for testing/business decisions, Atlas advisory on coaching/voice quality), not calendar time unless noted
- **Exit criteria** — observable, testable conditions for "done"

Nothing below is marked done unless it has been verified, not just built.

---

## Current State Snapshot (as of this document)

### Built and verified working end-to-end (real infrastructure)
- Monorepo, Docker Compose, CI scaffold
- Real Supabase project wired: Auth (JWKS/ES256), Postgres (SQLAlchemy + Alembic), Storage (native S3-compatible API)
- Row Level Security policies across all tables
- Registration → email confirmation → login → logout → password reset, tested live in-browser against production Supabase
- Protected-route middleware, server-side upload validation
- Session upload flow (presigned URL → S3 → Celery task enqueue)
- Stripe subscription scaffold (checkout, portal, webhook handlers) — code complete, **never exercised against a real Stripe account**
- Full QA pass: responsive layout, accessibility (`role="alert"`, label associations), error-state messaging, Strict Mode double-invocation bugs fixed
- Complete responsive UI shell: dashboard, upload, session list, session/debrief page, DNA profile page, billing, settings

### Built and unit/integration-tested with synthetic data (never run on real telemetry)
- `.ibt` binary parser (`IbtParser`) — byte layout reconstructed from iRacing SDK documentation, **never validated against a real `.ibt` file**
- Feature extractor, Driver DNA engine (EWMA merge, confidence scoring, classification), coaching engine — all unit-tested in isolation
- Cross-stage integration test proving parser → extractor → DNA → coaching wire together correctly and DNA evolves sensibly across multiple sessions (synthetic data)
- Delta voice (LLM) integration code complete — **untested against a real Anthropic API key** (key is still a placeholder)
- Standalone `scripts/validate_ibt.py` diagnostic tool with physical-plausibility sanity checks, ready for the first real file
- 101 backend tests passing

### Explicitly not started
- Delta Conversations (Pro follow-up chat) — no model, router, or UI
- Onboarding survey flow (3–4 question intro, DNA explainer) — users go straight from registration to an empty dashboard
- Progress tracking / DNA evolution charts (Pro) — `GET /dna/history` endpoint exists, no frontend chart
- Track reference data — `tracks` / `track_corners` tables have **0 rows**; every session currently produces session-level features only, no corner-level detail
- Error monitoring / alerting (Sentry or equivalent) — not configured anywhere
- Legal pages (Terms of Service, Privacy Policy), support channel, refund policy
- Pricing decision — PRD still lists this as open ($15/$20/$25/$19 per month under consideration)
- Beta user recruitment

**The three unvalidated risks that gate this roadmap:** real iRacing telemetry (M1), a real Anthropic response (M1), and a real credit card (M4). Nothing downstream of those should be treated as proven until each is retired.

---

## Milestone Overview

| Milestone | Objective | Effort (eng-time) | Primary Gate |
|---|---|---|---|
| **M1** — Real-Data Validation & Hardening | Prove the pipeline works on real telemetry and real LLM output | 1–2 weeks | A real `.ibt` file and an Anthropic key exist and produce a trustworthy debrief |
| **M2** — Feature-Complete Private Alpha | Ship the rest of the PRD's V1 feature list | 3–4 weeks | Founder can run the complete product loop themselves, daily, without friction |
| **M3** — Closed Beta | Validate the product with real drivers who aren't us | 1–2 weeks setup + 3–4 weeks observation | 10 beta drivers, per PRD success criteria |
| **M4** — Paid Launch Readiness Gate | Everything that must be true before a stranger's credit card is charged | 1–2 weeks | See dedicated gate checklist below |
| **M5** — First 100 Paying Customers | Prove the business, not just the product | Ongoing / GTM-driven | 100 active paying subscribers, retention holding |
| **M6** — Version 1.0 | Full PRD V1 scope, hardened, proven at scale | 2–4 weeks (post-M5 data) | Unit economics validated; infra scales without re-architecture |

---

## M1 — Real-Data Validation & Hardening

### Objective
Confirm the parser correctly reads a real `.ibt` file and the LLM produces a debrief that sounds like Delta, not a chatbot.

### Depends on
- A real `.ibt` file from a tester (see checklist already provided separately — practice session, 5+ laps, single car/track)
- A real Anthropic API key

### Deliverables
1. Run `scripts/validate_ibt.py` against the real file; fix any byte-layout mismatches the sanity checks or manual review surface in `pipeline/parser/ibt_parser.py`
2. Re-run the full synthetic test suite after any parser changes to confirm no regressions
3. Manually cross-check parsed output (track, car, lap count, lap times) against what the tester actually remembers driving
4. Swap in a real `ANTHROPIC_API_KEY`; generate 3–5 real debriefs from real sessions
5. Founder + Atlas review those debriefs against the Delta voice rules in `CLAUDE.md` (no compliments, no invented data, no false precision, confidence always communicated) — iterate on the system prompt in `delta_voice.py` until this passes
6. Seed track reference data (`tracks` / `track_corners`) for at least the tracks the tester's file(s) cover, so corner-level features stop silently degrading to session-level-only
7. Repeat with a second and third real file if available (different track/car), to catch parser assumptions that only broke on the first file by luck

### Effort estimate
- Parser fixes: 1–3 days if byte layout is close; up to a week if the struct assumptions are fundamentally wrong and need rework against the actual SDK headers
- Delta voice prompt iteration: 2–3 review cycles, ~3–4 days total (bounded by Founder/Atlas availability, not engineering time)
- Track data seeding (per track): ~1 day per track including manual corner-boundary validation against real telemetry

### Exit criteria
- A real `.ibt` file parses with no sanity-check warnings from `validate_ibt.py`, and the output is confirmed correct by the person who drove the session
- A real LLM-generated debrief passes Founder + Atlas review with no invented data and correct confidence framing
- At least one track has seeded corner data validated against real telemetry (corner-level coaching, not just session-level, is demonstrated end-to-end)
- Full test suite still green after any parser changes

---

## M2 — Feature-Complete Private Alpha

### Objective
Close the gap between what's built and the PRD's full Version 1 in-scope feature list.

### Depends on
- M1 complete (no point building Conversations/progress tracking on top of an unvalidated pipeline — bugs found there would need to be re-fixed downstream anyway)

### Deliverables
1. **Delta Conversations (Pro)** — `conversations` / `conversation_messages` tables already exist in the schema; build the SQLAlchemy models, `POST /debriefs/{id}/conversations`, `POST /conversations/{id}/messages` endpoints, LLM context-injection (session debrief + DNA + driver profile), 20-message limit enforcement, out-of-scope question handling, and the chat UI gated behind Pro
2. **Onboarding flow** — post-registration survey (platform pre-selected as iRacing, optional iRacing member ID, 3–4 experience/goal questions), brief Driver DNA explainer, under 3 minutes end-to-end per PRD §8.1
3. **Progress tracking (Pro)** — frontend charts consuming the existing `GET /dna/history` endpoint: best lap time trend by track, consistency score trend, DNA attribute evolution
4. **Session notes** — optional free-text note on upload ("was pushing too hard early on"), surfaced to the LLM as context
5. **Expand track reference data** — target 5 tracks total (PRD's Sprint 1.2 target), prioritized by whatever tracks the alpha/beta cohort actually drives
6. **Free tier enforcement pass** — confirm the monthly upload counter, usage indicator, and upgrade CTA all work correctly end-to-end (built but not yet load-bearing-tested with real usage patterns)

### Effort estimate
- Delta Conversations: 5–7 days (backend + LLM context wiring + UI)
- Onboarding flow: 2–3 days
- Progress tracking charts: 3–4 days
- Session notes: 1 day
- Track data (per additional track beyond M1's first): ~1 day each × 4 tracks = 4 days
- **Total: ~3–4 weeks**

### Exit criteria
- Founder completes the full loop unassisted: register → onboarding → upload → debrief → ask Delta a follow-up question → view progress trend — with zero engineering intervention
- All PRD §8 "In Scope — Version 1" features are present in the running app
- Free tier limits and Pro gating verified with real accounts, not just unit tests

---

## M3 — Closed Beta

### Objective
Validate the product with real drivers, not the Founder, against the PRD's beta success criteria.

### Depends on
- M2 complete
- Monitoring in place (you cannot debug 10 strangers' problems by asking them to read you a stack trace)

### Deliverables
1. Error monitoring/alerting configured (Sentry or equivalent) across frontend and backend
2. Structured logging sufficient to reconstruct "what happened to this specific session" without database access
3. Recruit 10 beta drivers per PRD's plan: 1,500–4,000 iRating, active league racers, sourced from Discord/Reddit/Founder's network, committed to 4+ sessions over 3 weeks
4. Feedback collection wired up: 3-question survey after first debrief, 15-minute call after 2+ weeks, exit NPS survey
5. A visible feedback/bug-report channel (even something as simple as a monitored email or Discord channel) — beta users need a way to tell you something's wrong that isn't "silently churn"

### Effort estimate
- Monitoring + logging setup: 2–3 days
- Beta recruitment: calendar-driven, not eng-driven — budget 1–2 weeks of Founder outreach in parallel with the above
- Observation window: 3–4 calendar weeks (per PRD beta commitment), engineering time during this window is mostly reactive bug-fixing, budget ~30–40% of one engineer's time

### Exit criteria (PRD beta success criteria)
- 8 of 10 drivers return after their first debrief
- 6 of 10 drivers show measurable lap-time improvement at a given track during the beta period
- At least 3 drivers say, unprompted, "this is different from what I've tried before"
- No critical bug prevents a debrief from completing for any beta driver

---

## M4 — Paid Launch Readiness Gate

### Objective
Clear every billing, legal, and operational-safety requirement for charging a stranger's credit card. A product can pass M3 (drivers love it) and still not be safe to charge for — this gate is non-negotiable.

### Depends on
- M3 complete — do not finalize pricing or open real billing on an unvalidated product; beta feedback may change what you're charging for

### Deliverables — grouped by risk category

**Billing & business**
- [ ] Pro tier pricing finalized (PRD flags $15/$20/$25/$19 per month as still open — beta feedback and willingness-to-pay signals should inform this)
- [ ] Free tier session limit finalized (PRD/MVP spec currently disagree — 2/month vs. 3/month — resolve before launch)
- [ ] Stripe integration tested against a **real Stripe account** in live mode with a real card (currently only code-complete, never exercised — `subscriptions.py` explicitly documents this gap)
- [ ] Failed-payment → grace period → downgrade path tested with an actual failed charge, not just webhook simulation
- [ ] Refund/cancellation policy written and reachable from the billing page

**Legal & trust**
- [ ] Terms of Service published
- [ ] Privacy Policy published — must accurately describe what telemetry data is stored, for how long, and that it's never sent raw to the LLM (this is a real differentiator worth stating explicitly)
- [ ] Data retention / deletion policy (what happens to a user's `.ibt` files and DNA if they cancel or request deletion)

**Operational safety**
- [ ] Support channel exists and is monitored (email at minimum) — 100 paying customers means real support volume, not beta-tester goodwill
- [ ] Cost controls on Anthropic API usage — a runaway loop or abuse pattern should not be able to produce an unbounded bill; rate limit debrief generation and Delta Conversations per user
- [ ] Abuse/fraud prevention on free tier (e.g. disposable-email signup loops to bypass the monthly upload limit) — at minimum, confirm Supabase's existing protections are sufficient
- [ ] Backups confirmed for the production database (Supabase's own backup policy reviewed, not assumed)
- [ ] Security pass on the auth/RLS layer specifically — with real paying customers, a data-isolation bug (User A seeing User B's telemetry) is a trust-ending incident, not a bug ticket

**Product**
- [ ] All error states tested with real failure injection (invalid file, insufficient laps, unknown track, processing failure + retry, duplicate upload) — per PRD §User Journey error states
- [ ] Load check: confirm Celery/Redis + the Anthropic API can handle plausible concurrent-upload volume for 100 active users without silent queueing delays that blow past the 90-second processing target

### Effort estimate
1–2 weeks, mostly non-engineering-parallelizable (legal drafting, Stripe live testing, support process setup can happen alongside engineering hardening)

### Exit criteria
Every checkbox above is checked, verified by actually doing the thing (real charge, real refund, real deletion request) — not by code review alone.

---

## M5 — First 100 Paying Customers

### Objective
Primarily a business/GTM milestone. Engineering's role: fix what breaks, watch the metrics, keep the product honest under real load.

### Depends on
- M4 complete (do not open paid signups before the gate above is cleared)

### What this milestone actually requires
- **Go-to-market execution** (Founder-led): beta cohort's word-of-mouth, Discord/Reddit community presence, content, direct outreach — the PRD's target persona (1,000–5,000 iRating competitive iRacing drivers) is a specific, findable community, not a mass-market funnel
- **Engineering's ongoing role**: monitor the metrics that matter —
  - Session return rate (D7, D30)
  - Free → Pro conversion rate
  - Processing time staying under the 90-second target as volume grows
  - Support ticket themes (these are free product feedback)
- **Retention engineering as needed**: if data shows drivers churn after session 1–2 because DNA confidence is still "Very Low," that's a signal to revisit onboarding messaging or consider adjusting the free tier limit — decisions grounded in real conversion data, not guesses

### Effort estimate
Not a fixed-duration engineering sprint. Budget roughly 20–30% of one engineer's ongoing time for bug-fixing, metric monitoring, and small retention-driven iterations, in parallel with whatever GTM cadence the Founder runs. Calendar time to 100 paying customers depends entirely on GTM execution and cannot be honestly estimated as an engineering timeline.

### Exit criteria
- 100 active paying (Pro tier) subscribers
- Retention holding at a level the Founder considers healthy (informed by M3's beta benchmarks, not an arbitrary number)
- No unresolved critical bugs affecting billing or data integrity

---

## M6 — Version 1.0

### Objective
The PRD's full "Version 1" feature list, running reliably for a real, paying, growing user base, with headroom to keep scaling without a rewrite.

### Depends on
- M5 in progress or complete — V1.0 is earned with usage evidence, not declared on a calendar date

### Deliverables
1. Full PRD §7 "In Scope — Version 1" feature list live and stable (all of M1–M4's deliverables, proven under real paid usage rather than just beta conditions)
2. Infra scaling pass informed by real M5 data: database indexing/query performance under real session volume, Celery worker concurrency tuned to actual concurrent-upload patterns, S3/storage costs reviewed at scale
3. Cost model validated: LLM cost per debrief, storage cost per user, infra cost per active user — confirmed against actual Pro-tier pricing to know the business has positive unit economics, not just plausible ones
4. Documented incident-response process (what happens when the pipeline breaks at 2am for 100 paying users, not 1 beta tester)
5. A formal decision, backed by M5 data, on what from the PRD's Post-MVP Phases 2–6 (desktop auto-upload, ACC support, real-time coaching, etc.) comes next — this roadmap deliberately stops at V1.0 and does not pre-commit to Phase 2 scope

### Effort estimate
2–4 weeks of engineering, but gated on having enough real M5 usage data to make the scaling/cost decisions correctly — starting this work before that data exists means guessing.

### Exit criteria
- All PRD V1 features live, stable, and used by real paying customers
- Unit economics confirmed profitable (or knowingly subsidized with a clear runway rationale)
- Infrastructure has headroom for the next order of magnitude of users without requiring emergency architecture changes
- The North Star metric (PRD §5) — percentage of active drivers showing statistically meaningful lap-time improvement after 4+ sessions — is being measured, not just aspired to, with a number the Founder can point to

---

## Dependency Chain

```
M1 (Real-Data Validation)
  └─ requires: real .ibt file + real Anthropic key
  └─ blocks: M2 (don't build Conversations/progress-tracking on an unvalidated pipeline)

M2 (Feature-Complete Alpha)
  └─ requires: M1 complete
  └─ blocks: M3 (beta users need the full V1 feature set, not a partial one)

M3 (Closed Beta)
  └─ requires: M2 complete + monitoring in place
  └─ blocks: M4 (pricing/limits should be informed by beta signal, not guessed)

M4 (Paid Launch Gate)
  └─ requires: M3 complete
  └─ blocks: M5 (do not open real billing before this gate clears — this is the
               one dependency in this roadmap that must not be skipped or reordered)

M5 (First 100 Paying Customers)
  └─ requires: M4 complete
  └─ blocks: M6 (V1.0 scaling decisions require real usage data from M5)

M6 (Version 1.0)
  └─ requires: M5 in progress, with enough real usage data to make scaling/cost
               decisions on evidence rather than guesses
```

The one hard rule in this chain: **M4 cannot be skipped or compressed to hit a growth target sooner.** Everything else can slip a bit under schedule pressure; billing correctness, data privacy, and security cannot.

---

## Risks

| Risk | Probability | Impact | Response |
|---|---|---|---|
| Real `.ibt` byte layout is substantially different from the SDK-doc-derived assumptions | Medium | High | `validate_ibt.py` is built specifically to surface this fast; budget the wider 1-week estimate in M1, not the optimistic 1–3 day one |
| Delta's voice doesn't pass Founder/Atlas review on the first real LLM output | High | Medium | Budgeted as 2–3 iteration cycles in M1, consistent with the original 90-day roadmap's assumption |
| Track reference data is expensive to build accurately | Medium | High | Seed incrementally (M1: 1 track, M2: 5 tracks) prioritized by what real users actually drive, not a fixed pre-selected list |
| Beta drivers don't show measurable improvement (North Star metric fails) | Medium | High | This is a product-validation risk, not an engineering one — if M3's exit criteria aren't met, the right response is to stop and revisit the coaching engine, not to proceed to M4 anyway |
| Stripe live-mode testing surfaces integration issues late | Low–Medium | High | Explicitly scheduled in M4 rather than assumed correct from code review, because it never happened before now |
| GTM execution (M5) takes far longer than engineering readiness | High | Medium | Expected and fine — M5 is explicitly not treated as an engineering-timeline milestone in this document |
| Anthropic API cost scales faster than Pro revenue per user | Low–Medium | Medium | Cost-per-debrief tracking is part of M4's cost controls and M6's unit-economics validation, not left until it's already a problem |

---

## Explicitly Out of Scope for Version 1.0

Per the PRD's Post-MVP Roadmap (§15), deliberately deferred past V1.0 — not part of any milestone above:

- Desktop companion app / auto-upload
- Assetto Corsa Competizione (or any non-iRacing) support
- Real-time / live telemetry coaching
- Mobile application
- Video analysis
- Setup recommendations
- Peer comparison / leaderboards / social features
- Team or coach portal
- Real-world motorsport telemetry (AiM, MoTeC, VBOX)
- Delta voice interface (audio debriefs)

A decision on which of these comes next is deferred to the M6 exit review, informed by real M5 usage data — see M6 deliverable 5.
