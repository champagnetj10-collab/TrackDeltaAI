# TrackDelta AI — System Architecture
**Document:** 04 of 05  
**Version:** 1.0  
**Status:** Engineering Reference  
**Date:** June 30, 2026

---

## 1. Architecture Philosophy

TrackDelta's architecture is guided by the same principles that guide the product:

- **Simplicity before complexity.** We build the simplest architecture that can do the job correctly. We do not build for scale we do not yet have.
- **Intelligence in the engineering, not the model.** The analysis pipeline is where our technical differentiation lives. The LLM is downstream of that.
- **Explainability.** Every coaching output must be traceable to specific telemetry measurements and algorithm steps. No black boxes in the coaching pipeline.
- **Correctness before performance.** Getting the analysis right is more important than making it fast. We optimize once we have proven correctness.

---

## 2. System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DRIVER (Browser)                            │
│                     Next.js Web Application                         │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTPS
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          API GATEWAY                                │
│                    FastAPI (Python) — REST API                      │
│         Auth middleware · Rate limiting · Request validation        │
└────┬──────────────┬──────────────┬──────────────────┬──────────────┘
     │              │              │                  │
     ▼              ▼              ▼                  ▼
┌─────────┐  ┌──────────┐  ┌──────────────┐  ┌────────────────┐
│  Auth   │  │  Upload  │  │  Session     │  │  Subscription  │
│ Service │  │  Service │  │  Service     │  │  Service       │
│         │  │          │  │              │  │                │
│ Supabase│  │ S3 + SQS │  │ Read debrief │  │ Stripe API     │
└─────────┘  └────┬─────┘  │ DNA profile  │  └────────────────┘
                  │        │ History      │
                  ▼        └──────────────┘
┌─────────────────────────────────────────────────────────────────────┐
│                      PROCESSING PIPELINE                            │
│                   (Asynchronous — Queue-driven)                     │
│                                                                     │
│   ┌────────────┐   ┌──────────────┐   ┌───────────────────────┐   │
│   │  Telemetry │   │   Feature    │   │     Driver DNA        │   │
│   │   Parser   │──▶│  Extraction  │──▶│       Engine          │   │
│   │            │   │   Service    │   │                       │   │
│   └────────────┘   └──────────────┘   └──────────┬────────────┘   │
│                                                   │               │
│                          ┌────────────────────────┘               │
│                          ▼                                         │
│              ┌───────────────────────┐                            │
│              │    Coaching Engine    │                            │
│              │  (Structured Output)  │                            │
│              └───────────┬───────────┘                            │
│                          │                                         │
│                          ▼                                         │
│              ┌───────────────────────┐                            │
│              │    LLM Service        │                            │
│              │  (Delta's Voice)      │                            │
│              │  Anthropic Claude API │                            │
│              └───────────┬───────────┘                            │
│                          │                                         │
│                          ▼                                         │
│              ┌───────────────────────┐                            │
│              │   Debrief Storage     │                            │
│              │   + Notify User       │                            │
│              └───────────────────────┘                            │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           DATA LAYER                                │
│                                                                     │
│   PostgreSQL (Primary DB)    │    S3 (File Storage)                │
│   - Users & auth             │    - Raw .ibt files                 │
│   - Sessions metadata        │    - Processed feature data         │
│   - Driver DNA (versioned)   │    - Debrief content                │
│   - Debriefs                 │                                     │
│   - Conversations            │    Redis (Queue + Cache)            │
│   - Subscriptions            │    - SQS for processing queue       │
│   - Track reference data     │    - Session cache                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack

### 3.1 Frontend

**Framework:** Next.js 14 (App Router)  
**Language:** TypeScript  
**Styling:** Tailwind CSS  
**State management:** React Query (server state) + Zustand (client state)  
**Charts:** Recharts (lightweight, sufficient for DNA trend charts)  
**File upload:** react-dropzone  
**Hosting:** Vercel

**Why Next.js:**
- Server-side rendering for initial page load performance
- App Router enables streaming (useful for debrief loading states)
- Strong TypeScript support
- Vercel deployment is zero-config and fast
- Large ecosystem for the components we need

**Why not a SPA (Vite/React):**
- SSR matters for first-load experience on the debrief page
- API routes in Next.js are convenient for BFF (backend-for-frontend) patterns

### 3.2 Backend

**Framework:** FastAPI (Python 3.11+)  
**Language:** Python  
**Runtime:** Uvicorn + Gunicorn  
**Task Queue:** Celery + Redis  
**Hosting:** Railway (initially); AWS ECS when scale demands it

**Why FastAPI:**
- Python is the right language for the data science work in the processing pipeline
- FastAPI has excellent async support and is significantly faster than Django/Flask
- Pydantic for request/response validation is excellent
- Auto-generated OpenAPI docs are useful for team communication

**Why Python for the pipeline:**
- numpy, pandas, scipy are the correct tools for telemetry signal processing
- Strong library support for statistical analysis
- Same language across API and pipeline avoids context switching

### 3.3 Database

**Primary:** PostgreSQL 15 via Supabase  
**Why Supabase:** Managed PostgreSQL with auth integration, real-time capabilities if needed later, good DX for a small team, generous free tier for early development

**Telemetry feature storage:** PostgreSQL with JSONB columns for per-lap feature arrays  
**Why not TimescaleDB initially:** Adds operational complexity; JSONB in Postgres is sufficient for MVP session volumes. Revisit when sessions/day exceeds ~500.

**Cache:** Redis (via Upstash for managed Redis)  
- Processing queue (Celery broker)
- Session cache for frequently-accessed debriefs
- Rate limiting counters

### 3.4 File Storage

**Provider:** AWS S3 (or Cloudflare R2 for cost — no egress fees)  
**Buckets:**
- `trackdelta-raw-telemetry` — uploaded `.ibt` files (private; lifecycle: delete after 90 days once processed)
- `trackdelta-processed-features` — extracted feature JSON per session (private; retain indefinitely)
- `trackdelta-debriefs` — stored debrief content as JSON (private; retain indefinitely)

**Access:** Presigned URLs for upload (frontend uploads directly to S3, bypassing API server for large files)

### 3.5 Authentication

**Provider:** Supabase Auth  
**Methods:** Email + password (MVP); Social auth in Phase 2  
**JWT:** Standard Supabase JWT tokens; validated by FastAPI middleware  
**Session:** 30-day token expiry; refresh token rotation

### 3.6 Payments

**Provider:** Stripe  
**Integration:** Stripe Checkout (hosted) for upgrade flow; Stripe Customer Portal for subscription management  
**Webhooks:** Stripe sends events to a FastAPI webhook endpoint for subscription state changes  
**What we store:** Stripe customer ID and subscription ID in our database; never card data

### 3.7 LLM Provider

**Provider:** Anthropic Claude API  
**Model:** Claude Sonnet (balance of quality and cost); evaluate Opus for complex debrief generation  
**Integration:** Structured prompt → structured response using Anthropic's tool use / structured output features  
**Usage pattern:** Called once per session (debrief generation) + per conversation message (Delta conversations)

### 3.8 Email

**Provider:** Resend (transactional email)  
**Use cases:** Email verification, password reset, (future) session-ready notifications

---

## 4. Data Architecture

### 4.1 Database Schema

```sql
-- USERS
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  display_name VARCHAR(100),
  iracing_member_id VARCHAR(50),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Onboarding survey responses
  experience_level VARCHAR(50),    -- 'under_1yr', '1_3yr', '3_5yr', '5yr_plus'
  irating_range VARCHAR(50),       -- 'under_1000', '1000_2000', etc.
  primary_goal VARCHAR(100),
  main_frustration VARCHAR(100),
  
  -- Subscription
  stripe_customer_id VARCHAR(100),
  subscription_tier VARCHAR(20) DEFAULT 'free',  -- 'free', 'pro'
  subscription_status VARCHAR(20),               -- 'active', 'canceled', 'past_due'
  subscription_period_end TIMESTAMPTZ,
  monthly_uploads_used INT DEFAULT 0,
  monthly_uploads_reset_at TIMESTAMPTZ
);

-- SESSIONS
CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- File reference
  raw_file_s3_key VARCHAR(500),
  file_size_bytes BIGINT,
  
  -- Session metadata (extracted during parsing)
  iracing_track_name VARCHAR(200),
  track_config VARCHAR(100),
  car_name VARCHAR(200),
  car_class VARCHAR(100),
  session_type VARCHAR(50),       -- 'practice', 'qualifying', 'race', 'time_trial'
  session_date DATE,
  total_laps INT,
  clean_laps INT,
  best_lap_time_ms INT,
  mean_lap_time_ms INT,
  session_duration_s INT,
  
  -- Processing state
  processing_status VARCHAR(50) DEFAULT 'pending',
  -- 'pending', 'uploading', 'parsing', 'extracting', 'coaching', 'complete', 'failed'
  processing_started_at TIMESTAMPTZ,
  processing_completed_at TIMESTAMPTZ,
  processing_error TEXT,
  
  -- Optional driver note
  driver_note TEXT,
  
  -- References
  features_s3_key VARCHAR(500),   -- Processed feature data location
  debrief_id UUID                 -- FK to debriefs table
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_status ON sessions(processing_status);

-- DRIVER DNA (versioned)
CREATE TABLE driver_dna (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  session_id UUID REFERENCES sessions(id),  -- Session that triggered this version
  created_at TIMESTAMPTZ DEFAULT NOW(),
  schema_version VARCHAR(20) DEFAULT '1.0',
  
  -- Metadata
  total_sessions INT,
  total_clean_laps INT,
  overall_confidence FLOAT,
  
  -- Core attributes stored as JSONB for flexibility
  braking JSONB,
  throttle JSONB,
  steering JSONB,
  consistency JSONB,
  risk JSONB,
  pressure JSONB,
  learning JSONB,
  
  -- Track profiles
  track_profiles JSONB,
  
  -- Is this the current (latest) DNA for this user?
  is_current BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_driver_dna_user_id ON driver_dna(user_id);
CREATE INDEX idx_driver_dna_current ON driver_dna(user_id, is_current);

-- DEBRIEFS
CREATE TABLE debriefs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Debrief content stored as structured JSONB
  -- Matches the coaching engine's output schema exactly
  debrief_content JSONB NOT NULL,
  
  -- DNA state at time of this debrief
  dna_version_id UUID REFERENCES driver_dna(id),
  dna_confidence_at_debrief FLOAT,
  
  -- LLM metadata
  llm_model_used VARCHAR(100),
  llm_prompt_tokens INT,
  llm_completion_tokens INT,
  llm_total_cost_usd FLOAT
);

-- DELTA CONVERSATIONS
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  debrief_id UUID REFERENCES debriefs(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE conversation_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  role VARCHAR(20) NOT NULL,  -- 'user' or 'delta'
  content TEXT NOT NULL,
  llm_tokens_used INT
);

-- TRACKS (reference data)
CREATE TABLE tracks (
  id VARCHAR(100) PRIMARY KEY,        -- e.g., 'watkins_glen_full'
  iracing_track_name VARCHAR(200) NOT NULL,
  configuration VARCHAR(100),
  total_length_m FLOAT,
  country VARCHAR(100),
  surface_type VARCHAR(50),           -- 'asphalt', 'dirt', 'mixed'
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE track_corners (
  id VARCHAR(100) PRIMARY KEY,        -- e.g., 'wg_t1'
  track_id VARCHAR(100) REFERENCES tracks(id),
  name VARCHAR(200) NOT NULL,
  corner_type VARCHAR(50) NOT NULL,   -- 'hairpin', 'slow', 'medium', 'fast', 'sweeper', 'chicane', 'complex'
  sequence_number INT NOT NULL,       -- Order around the track
  
  -- Position references (LapDistPct)
  entry_pct FLOAT NOT NULL,
  apex_pct FLOAT NOT NULL,
  exit_pct FLOAT NOT NULL,
  
  -- Reference values
  reference_brake_point_pct FLOAT,
  expected_min_speed_kph FLOAT,
  trail_braking_expected BOOLEAN DEFAULT FALSE,
  
  notes TEXT
);

-- SUBSCRIPTIONS
CREATE TABLE subscription_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  event_type VARCHAR(100),            -- Stripe event type
  stripe_event_id VARCHAR(200) UNIQUE,
  event_data JSONB,
  processed_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 4.2 JSONB Schema — Debrief Content

The debrief content stored in `debriefs.debrief_content` follows this structure:

```json
{
  "version": "1.0",
  "generated_at": "ISO8601 timestamp",
  
  "session_header": {
    "track_name": "Watkins Glen International — Full",
    "car_name": "Dallara Formula 3",
    "session_type": "Practice",
    "best_lap_time_ms": 102340,
    "total_laps": 34,
    "clean_laps": 31,
    "session_consistency_pct": 0.76
  },
  
  "delta_overview": {
    "text": "Delta's written overview paragraph..."
  },
  
  "opportunities": [
    {
      "rank": 1,
      "corner_id": "wg_t7",
      "corner_name": "Turn 7 — The Toe",
      "observation": "Your brake application is consistently 18–22 meters earlier than your three fastest laps...",
      "impact": "This results in lower entry speed and a delayed throttle point...",
      "estimated_time_ms_min": 180,
      "estimated_time_ms_max": 320,
      "time_confidence": "moderate",
      "recommendation": "Try moving your brake point 10 meters later..."
    }
  ],
  
  "strengths": [
    {
      "rank": 1,
      "area": "High-speed corner commitment",
      "observation": "Your minimum speed through Turns 1 and 2 was among your highest recorded...",
      "evidence": "Mean apex speed at T1: 187 kph vs. session average of 181 kph"
    }
  ],
  
  "time_available": {
    "estimate_ms_min": 400,
    "estimate_ms_max": 700,
    "confidence": "moderate",
    "explanation": "Based on sector time variance and gap between best and median laps...",
    "suppressed": false,
    "suppression_reason": null
  },
  
  "dna_update": {
    "text": "Delta's DNA update paragraph...",
    "attributes_updated": ["braking.style_confidence", "consistency.overall_score"],
    "confidence_changes": [
      {"attribute": "braking.style", "from": "low", "to": "moderate"}
    ]
  },
  
  "practice_plan": [
    {
      "rank": 1,
      "title": "Brake point at Turn 7",
      "detail": "Move brake point 10 meters later. Focus on...",
      "estimated_sessions_to_improve": 2
    }
  ],
  
  "one_clear_objective": {
    "text": "Next session: commit to a later brake point at Turn 7 and maintain light pressure through turn-in."
  }
}
```

---

## 5. Processing Pipeline — Detailed

### 5.1 Upload Flow

```
1. Frontend requests presigned S3 upload URL from API
   POST /api/sessions/upload-url
   → Returns: { session_id, presigned_url }

2. Frontend uploads .ibt directly to S3 using presigned URL
   PUT {presigned_url} (file bytes)

3. Frontend notifies API that upload is complete
   POST /api/sessions/{session_id}/upload-complete
   → API enqueues processing job to Celery queue
   → Returns: { status: 'processing' }

4. Frontend polls for status
   GET /api/sessions/{session_id}/status
   → Returns: { status: 'parsing' | 'extracting' | 'coaching' | 'complete' | 'failed' }
   → Polling interval: 3 seconds; stop after 'complete' or 'failed'
   → Consider WebSocket or SSE for Phase 2 to replace polling
```

### 5.2 Pipeline Worker — Step by Step

The processing pipeline runs as a Celery task. All steps run sequentially within one worker task.

**Step 1: Telemetry Parsing**

```python
class TelemetryParser:
    """
    Parses iRacing .ibt binary format.
    .ibt format: header block + variable definitions + data samples
    
    Libraries: irsdk (community Python library for .ibt parsing)
    Fallback: Custom binary parser if irsdk has limitations
    """
    
    def parse(self, s3_key: str) -> ParsedSession:
        # 1. Download .ibt from S3 to temp file
        # 2. Use irsdk to read header: track name, car, session type, date
        # 3. Extract all telemetry channels at full 60Hz rate
        # 4. Identify complete laps (LapDistPct cycle completion)
        # 5. Return ParsedSession with metadata + raw channel arrays per lap
        pass
```

**Step 2: Feature Extraction**

```python
class FeatureExtractionService:
    """
    Converts raw telemetry channels into structured, meaningful features.
    Requires: parsed session + track reference data
    """
    
    def extract(self, parsed_session: ParsedSession, track: Track) -> SessionFeatures:
        # 1. Load track corner definitions from database
        # 2. For each clean lap:
        #    a. Segment into corner windows using LapDistPct
        #    b. Extract braking features per corner
        #    c. Extract throttle features per corner
        #    d. Extract speed features per corner
        #    e. Extract steering features per corner
        # 3. Aggregate to session level
        # 4. Calculate consistency metrics
        # 5. Return SessionFeatures (all features structured as JSON)
        pass
```

**Step 3: Driver DNA Engine**

```python
class DriverDNAEngine:
    """
    Updates the driver's DNA model with features from the new session.
    Applies EWMA update to all quantitative attributes.
    Re-evaluates all classifications.
    Records version history.
    """
    
    def update(self, user_id: UUID, session_features: SessionFeatures) -> DriverDNA:
        # 1. Load current DNA from database (or create empty if first session)
        # 2. Calculate session weight (based on lap count and quality)
        # 3. Apply EWMA update to all quantitative attributes
        # 4. Re-evaluate all classification attributes (braking style, etc.)
        # 5. Update confidence scores
        # 6. Mark previous DNA version as not current
        # 7. Save new DNA version to database
        # 8. Return updated DNA
        pass
```

**Step 4: Coaching Engine**

```python
class CoachingEngine:
    """
    Analyzes session features and DNA to produce structured coaching output.
    This is where TrackDelta's core coaching intelligence lives.
    Output is structured data — NOT natural language.
    """
    
    def generate(self, session_features: SessionFeatures, dna: DriverDNA) -> CoachingOutput:
        # 1. Identify top opportunities (corners with highest time loss)
        #    - Rank corners by: estimated_time_loss + coaching_potential
        #    - Filter to top 3 with minimum confidence threshold
        # 2. Identify top strengths (corners or attributes where driver excels)
        # 3. Calculate session-level time available estimate
        #    - Sum time loss across priority corners
        #    - Apply confidence adjustment
        #    - Output as range [min, max] + confidence level
        # 4. Generate practice plan
        #    - Map top opportunities to specific, actionable objectives
        #    - Sequence by impact
        # 5. Select one clear objective (highest impact + most actionable)
        # 6. Generate DNA update summary (what changed this session)
        # 7. Return CoachingOutput (structured, no natural language)
        pass
```

**Step 5: LLM Service (Delta's Voice)**

```python
class DeltaVoiceService:
    """
    Converts structured coaching output into Delta's natural language debrief.
    Uses Anthropic Claude API with a carefully structured prompt.
    """
    
    def generate_debrief(
        self, 
        coaching_output: CoachingOutput,
        dna: DriverDNA,
        session_metadata: SessionMetadata,
        driver_profile: DriverProfile
    ) -> str:
        
        system_prompt = """
        You are Delta, the AI race engineer for TrackDelta AI.
        
        Your character:
        - Calm, professional, and trusted
        - Honest about uncertainty — always communicate confidence levels
        - Specific — reference corners by name, cite data, never generalize
        - Never start with compliments or enthusiasm ("Great session!")
        - Never invent information not provided in the coaching data
        - If something is an estimate, label it as an estimate
        
        Your job in this response:
        Write the coaching debrief sections as instructed in the user message.
        Use only the data provided. Do not add observations not present in the input.
        Write in second person ("Your braking..." not "The driver's braking...")
        """
        
        user_prompt = self._build_structured_prompt(
            coaching_output, dna, session_metadata, driver_profile
        )
        
        # Call Anthropic API
        # Parse response into debrief sections
        # Validate: check that all required sections are present
        # Return structured debrief content
        pass
```

**Step 6: Debrief Storage + Notification**

```python
# 1. Store completed debrief in debriefs table
# 2. Update session.processing_status = 'complete'
# 3. Update session.debrief_id
# 4. (Future) Send email/push notification to driver
# 5. Log processing metrics (total time, token usage, cost)
```

### 5.3 Pipeline Error Handling

Each step should:
- Catch exceptions and log with full context (session_id, user_id, step name, error)
- Update `session.processing_status = 'failed'` and `session.processing_error` with a driver-readable message
- Retry automatically for transient failures (S3 timeout, LLM API error): max 3 retries with exponential backoff
- For permanent failures (corrupt .ibt file, unknown track): fail immediately with a clear error message; do not retry

---

## 6. API Design

### 6.1 API Conventions

- Base URL: `https://api.trackdelta.ai/v1`
- Authentication: Bearer token in Authorization header (Supabase JWT)
- Content-Type: `application/json`
- Error format: `{ "error": { "code": "string", "message": "string" } }`
- Pagination: `?limit=20&offset=0` for list endpoints

### 6.2 Endpoints

**Authentication (delegated to Supabase — not custom endpoints)**

**Sessions**
```
POST   /sessions/upload-url           Request presigned S3 URL
POST   /sessions/{id}/upload-complete Notify upload complete; enqueue processing
GET    /sessions/{id}/status          Poll processing status
GET    /sessions                      List user's sessions (paginated)
GET    /sessions/{id}                 Get session metadata
GET    /sessions/{id}/debrief         Get debrief for session
DELETE /sessions/{id}                 Delete session (and associated files)
```

**Driver DNA**
```
GET    /dna                           Get current Driver DNA
GET    /dna/history                   Get DNA version history (Pro)
```

**Delta Conversations (Pro)**
```
POST   /debriefs/{id}/conversations           Start a conversation
GET    /debriefs/{id}/conversations/{conv_id} Get conversation messages
POST   /debriefs/{id}/conversations/{conv_id}/messages  Send a message
```

**User Profile**
```
GET    /me                            Get current user profile
PATCH  /me                            Update profile
DELETE /me                            Delete account
```

**Subscriptions**
```
GET    /subscriptions/current         Get current subscription status
POST   /subscriptions/checkout        Create Stripe checkout session
POST   /subscriptions/portal          Create Stripe customer portal session
POST   /webhooks/stripe               Stripe webhook handler (internal)
```

**Tracks (internal/admin)**
```
GET    /tracks                        List available tracks
GET    /tracks/{id}                   Get track with corner definitions
```

---

## 7. Frontend Architecture

### 7.1 Route Structure

```
/                          Landing page (public)
/login                     Login
/register                  Registration
/verify-email              Email verification
/app                       App shell (authenticated)
  /app/dashboard           Home — recent session, upload CTA
  /app/upload              Upload new session
  /app/sessions            Session history
  /app/sessions/[id]       Session debrief
  /app/dna                 Driver DNA profile
  /app/settings            Account settings
  /app/billing             Subscription management
/upgrade                   Upgrade to Pro (landing)
```

### 7.2 State Management

**Server state (React Query):**
- Sessions list
- Current session + debrief
- Driver DNA
- Subscription status

**Client state (Zustand):**
- Upload progress
- Processing status polling
- UI state (modals, toasts)

### 7.3 Key Component Hierarchy

```
<AppLayout>
  <Navigation />
  <main>
    <DashboardPage>
      <WelcomeBanner />
      <UploadCTA />
      <RecentSessionCard />
    </DashboardPage>
    
    <UploadPage>
      <FileDropzone />
      <SessionNoteInput />
      <ProcessingStatus />
    </UploadPage>
    
    <DebriefPage>
      <SessionHeader />
      <DeltaOverview />
      <OpportunitiesSection />
      <StrengthsSection />
      <TimeAvailableCard />
      <DNAUpdateCard />
      <PracticePlan />
      <OneClearObjective />
      <DeltaConversation />  {/* Pro only */}
    </DebriefPage>
    
    <DNAPage>
      <DNACard />
      <AttributeDetail />
      <DNAHistoryChart />  {/* Pro only */}
    </DNAPage>
  </main>
</AppLayout>
```

---

## 8. Security

### 8.1 Authentication & Authorization

- All `/app/*` routes require valid Supabase JWT
- Row-level security (RLS) enforced at the database level: users can only access their own records
- S3 presigned URLs expire after 15 minutes (upload) and 60 minutes (download)
- All S3 buckets are private; no public access

### 8.2 Rate Limiting

- Upload requests: 10 per hour per user (prevents abuse; well above normal usage)
- API requests: 100 per minute per user
- LLM conversation messages: 20 per conversation (enforced at API level)
- Stripe webhook endpoint: IP allowlisted to Stripe's published IP ranges

### 8.3 Data Privacy

- Raw `.ibt` files are deleted from S3 after 90 days (processed features are retained)
- Users can delete their account and all associated data
- No telemetry data is used to train third-party models
- Driver DNA is private to each user — never shared or benchmarked without explicit consent

---

## 9. Observability

### 9.1 Logging

**Structured JSON logs** at all layers:
- Every API request: method, path, user_id, status_code, duration_ms
- Every pipeline step: session_id, step_name, duration_ms, outcome
- Every LLM call: model, prompt_tokens, completion_tokens, cost_usd, duration_ms
- Every error: full stack trace, session_id, user_id, step name

**Provider:** Axiom or Papertrail (simple, low-cost for MVP)

### 9.2 Error Tracking

**Provider:** Sentry  
- Both frontend (JavaScript errors) and backend (Python exceptions)
- Alerts on new error types and error rate spikes

### 9.3 Key Metrics to Track from Day One

| Metric | Why |
|---|---|
| Sessions uploaded per day | Core engagement signal |
| Pipeline success rate | % of uploads that produce a debrief |
| Pipeline p95 latency | User experience quality |
| LLM cost per debrief | Unit economics |
| Free → Pro conversion rate | Business health |
| Session return rate (users who upload again within 7 days) | Product-market fit signal |

---

## 10. Infrastructure & Deployment

### 10.1 Environments

| Environment | Purpose | Hosting |
|---|---|---|
| Local | Development | Docker Compose |
| Staging | Pre-production testing | Vercel (FE) + Railway (BE) |
| Production | Live product | Vercel (FE) + Railway (BE) |

### 10.2 Local Development Setup

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: trackdelta
      POSTGRES_USER: trackdelta
      POSTGRES_PASSWORD: local_dev_only
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7
    ports:
      - "6379:6379"
  
  api:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://...
      REDIS_URL: redis://redis:6379/0
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
      AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}
    ports:
      - "8000:8000"
  
  worker:
    build: ./backend
    command: celery -A app.worker worker --loglevel=info
    environment:
      (same as api)
```

### 10.3 CI/CD

**Provider:** GitHub Actions

Pipeline per PR:
1. Lint (ESLint for frontend, Ruff + mypy for backend)
2. Unit tests (pytest for backend, Jest for frontend)
3. Build check
4. Deploy to staging (on merge to `main`)

Production deploy: manual trigger from `main` branch after staging validation.

### 10.4 Environment Variables

All secrets managed in:
- Local: `.env` file (gitignored)
- Staging/Production: Railway environment variables (backend), Vercel environment variables (frontend)

Required variables:
```
# Backend
DATABASE_URL
REDIS_URL
ANTHROPIC_API_KEY
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
S3_BUCKET_TELEMETRY
S3_BUCKET_PROCESSED
STRIPE_SECRET_KEY
STRIPE_WEBHOOK_SECRET
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
RESEND_API_KEY
ENVIRONMENT  # 'local' | 'staging' | 'production'

# Frontend
NEXT_PUBLIC_SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY
NEXT_PUBLIC_API_URL
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY
```

---

## 11. Architecture Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| iRacing `.ibt` format changes between versions | Low | High | Pin irsdk version; monitor iRacing patch notes; abstract parser behind interface so replacement is isolated |
| LLM output quality is inconsistent (Delta sounds wrong) | Medium | High | Validate output structure before storing; build LLM evaluation suite with expected outputs; human review of first 100 debriefs |
| Pipeline latency exceeds 90 seconds | Medium | Medium | Profile each step; extract features can be optimized (vectorize numpy operations); LLM latency is the primary variable — use streaming if needed |
| Track reference data is wrong (incorrect corner definitions) | Medium | High | Validate reference data against known-fast driver telemetry; allow for easy override; clearly communicate in debrief when reference confidence is low |
| Cost per debrief becomes unsustainable | Low | Medium | Track LLM costs per debrief from day one; set budget alerts; evaluate cheaper models as coaching quality matures |
| S3 storage costs grow rapidly | Low | Low | Lifecycle policy deletes raw `.ibt` after 90 days; processed features are much smaller; monitor monthly |
