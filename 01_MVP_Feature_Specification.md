# TrackDelta AI — MVP Feature Specification
**Document:** 01 of 05  
**Version:** 1.0  
**Status:** Engineering Reference  
**Date:** June 30, 2026

---

## Guiding Filter

Before every feature decision, ask one question:

> *"Does this help a driver become faster, more consistent, or more confident?"*

If the answer is no, it does not belong in the MVP.

---

## 1. In Scope — Version 1

### Feature 1.1 — Authentication & Account Management

**What it does:** Allows a driver to create and manage their TrackDelta account.

**Functional Requirements:**
- Email + password registration
- Email verification (required before first upload)
- Secure login with session tokens
- Password reset via email
- Account settings: update display name, email, password
- Account deletion (data privacy requirement)

**Acceptance Criteria:**
- A driver can register, verify their email, and log in within 3 minutes
- Password reset completes in under 5 minutes
- Failed login attempts are rate-limited (5 attempts before temporary lockout)
- Sessions expire after 30 days of inactivity; user is prompted to re-authenticate

**Explicitly Not Included:**
- Social login (Google, Apple, Discord) — adds OAuth complexity; defer to Phase 2
- Two-factor authentication — defer unless security requirements demand it
- Team accounts / shared access

---

### Feature 1.2 — Driver Onboarding

**What it does:** Collects the minimum context needed for Delta to start understanding the driver. Sets expectations for Driver DNA.

**Functional Requirements:**

Step 1 — Welcome Screen
- Introduce Delta in Delta's voice (calm, professional)
- Set expectation: Delta learns over time; the first session has low confidence

Step 2 — Driver Profile Survey (4 questions maximum)
- "How long have you been racing on iRacing?" (Under 1 year / 1–3 years / 3+ years)
- "What is your approximate iRating?" (Under 1,000 / 1,000–2,000 / 2,000–3,500 / 3,500+)
- "What is your primary goal right now?" (Improve my consistency / Find more raw pace / Prepare for competitive racing / Just enjoy the sport)
- "What frustrates you most after a session?" (I know I'm losing time but don't know where / My pace is inconsistent / I don't know what to practice / I have no one to debrief with)

Step 3 — Driver DNA Introduction
- Brief explanation of what Driver DNA is and how it builds over time
- Explicit honesty: "After your first session, Delta's confidence will be low. That's expected. Every session makes it better."
- Visual preview of what a DNA profile looks like when mature

Step 4 — First Upload Prompt
- Clear CTA to upload their first iRacing session
- Brief explanation of where to find the `.ibt` file (with path guidance: `Documents/iRacing/telemetry/`)

**Acceptance Criteria:**
- Onboarding completes in under 3 minutes
- Survey answers are stored to Driver DNA initial context
- A driver who skips onboarding can still upload — but is prompted again on next login
- Onboarding is shown once; not repeated on subsequent logins

---

### Feature 1.3 — Session Upload

**What it does:** Accepts an iRacing `.ibt` telemetry file and initiates the processing pipeline.

**Functional Requirements:**

File Acceptance:
- File type: `.ibt` only
- Maximum file size: 250 MB (typical iRacing session is 30–120 MB; 250 MB provides margin)
- Client-side validation before upload: file type, size, basic header check
- Clear error messages for rejected files (wrong type, too large, corrupted)

Upload Experience:
- Drag-and-drop or file picker
- Progress bar during upload
- Optional session note field: "What were you working on? How did it feel?" (max 280 characters)
- Processing states communicated clearly:
  1. **Uploading** — file transfer in progress
  2. **Reading Session** — parsing metadata
  3. **Analyzing with Delta** — feature extraction and coaching engine running
  4. **Ready** — debrief available

Session Metadata (extracted and displayed on confirmation):
- Track name and configuration
- Car class and car name
- Session type (practice / qualifying / race / time trial)
- Session date and total laps completed
- Session duration

**Acceptance Criteria:**
- Upload + processing completes in under 90 seconds for a typical session (30–80 laps, standard track)
- If processing exceeds 3 minutes, the user receives a notification and can navigate away; debrief is available when ready
- Failed processing displays a clear error message and offers a retry
- Duplicate upload detection: if the same session file is uploaded again, the system warns the driver before reprocessing
- Free tier enforcement: if driver has reached monthly upload limit, upload is blocked with a clear message and upgrade CTA

**Free Tier Limit:**
- 3 sessions per calendar month
- Counter displayed on upload page: "2 of 3 sessions used this month"
- Resets on the 1st of each month

---

### Feature 1.4 — Coaching Debrief

**What it does:** Delivers Delta's complete coaching analysis of the session. This is the core product.

**Functional Requirements:**

The debrief is a single, scrollable page. It is written by Delta. It is not a dashboard. It is a structured coaching document.

**Section 1 — Session Header**
- Track name, car, session type, date
- Best lap time
- Total laps / clean laps
- Session quality indicator (laps within 102% of best lap / total laps — communicated as "session consistency")

**Section 2 — Delta's Overview**
- 2–4 sentences in Delta's voice
- References specific observations from the data
- Sets the tone: honest, specific, forward-looking
- Never begins with "Great session" or any variant of generic praise

**Section 3 — Top Opportunities**
- 2–3 specific areas where time is being lost (minimum 2; maximum 3)
- Each opportunity includes:
  - Corner or zone name (specific, e.g., "Turn 7 — The Hairpin")
  - What Delta observed ("Your brake application is consistently 18–22 meters earlier than your three fastest laps")
  - Why it costs time ("This results in lower entry speed and a delayed throttle point")
  - Estimated time available at this location: range with confidence label
  - Suggested behavioral change ("Try moving your brake point 10 meters later and maintaining light brake pressure through turn-in")
- If Delta cannot identify 3 well-supported opportunities, it reports 2 and states why: *"I identified two clear opportunities today. I want to see another session before making a third recommendation — the data isn't conclusive yet."*

**Section 4 — Top Strengths**
- 2–3 specific things the driver is doing well
- Evidence-based: must reference the data
- Not generic ("You're very consistent") — specific ("Your minimum apex speed through Turns 3 and 4 was higher than your 5 fastest sessions combined — your commitment on high-speed entries is a genuine strength")

**Section 5 — Estimated Time Available**
- A range, never a single number
- Confidence level: Very Low / Low / Moderate / High
- Brief explanation of how the estimate was derived
- If confidence is below the "Low" threshold (typically first 1–2 sessions), this section displays: *"Delta needs more data to estimate available time reliably. After 3–4 sessions on this track, I'll have a better picture."*

**Section 6 — Driver DNA Update**
- Brief note on what changed in the driver's DNA this session
- What new patterns were observed or confirmed
- What confidence level changed and why
- Example: *"Your braking profile confidence has moved from Very Low to Low. I'm beginning to see a consistent tendency toward early brake release — I'll watch this over the next two sessions."*

**Section 7 — Practice Plan**
- 3–5 specific, actionable objectives for the next session
- Ordered by estimated impact (highest first)
- Each objective is 1–3 sentences, actionable, not vague
- Practice plan is scoped to the same track if the driver is likely to return; otherwise general

**Section 8 — One Clear Objective**
- A single sentence. Bold. The most important thing Delta wants the driver to focus on.
- This is the thing they should think about while falling asleep.

**Debrief Behavior Rules:**
- Delta never invents data. Every claim is traceable to telemetry features.
- Delta never makes absolute precision claims. Ranges and confidence levels are mandatory on estimates.
- Delta acknowledges when data is insufficient rather than filling gaps with assumptions.
- The debrief is generated once and stored. It does not regenerate on reload.

**Acceptance Criteria:**
- Debrief is readable on desktop in under 5 minutes
- Every opportunity contains a corner name, observation, and specific recommendation
- Estimated time available always includes a confidence label and explanation
- DNA update section reflects changes from this specific session
- One clear objective is always present and always a single sentence

---

### Feature 1.5 — Driver DNA Profile

**What it does:** Gives the driver a clear, honest picture of how Delta understands them as a driver.

**Functional Requirements:**

Accessible from the main navigation as "My DNA."

**DNA Card (primary display):**

| Attribute | Value | Confidence |
|---|---|---|
| Braking Style | Late Braker | ████░ High |
| Corner Entry | High Commitment | ███░░ Moderate |
| Throttle Application | Aggressive Initial | ████░ High |
| Consistency | 8.4 / 10 | ████░ High |
| Risk Profile | Moderately Aggressive | ███░░ Moderate |
| Pressure Performance | Strong | ██░░░ Low |
| Learning Style | Focused Objectives | ███░░ Moderate |

Beneath the card:
- Sessions analyzed: [N]
- Laps analyzed: [N]
- DNA last updated: [date]
- "Driver DNA confidence grows with every session."

**Confidence Communication:**
- Visual: filled dots or bar (5-level scale)
- Text label: Very Low / Low / Moderate / High / Very High
- When hovering/tapping any attribute: brief tooltip explaining what it means and what data it's based on

**DNA History (Pro):**
- Chart showing how each attribute has changed over time
- Timestamps of major confidence upgrades

**Acceptance Criteria:**
- DNA profile loads in under 1 second
- Confidence levels are accurate to the current state of the DNA model
- Attributes with Very Low confidence are displayed differently (greyed out, italic) with text: *"Not enough data yet — Delta needs more sessions to form a reliable view."*
- The page never displays an empty state without explanation

---

### Feature 1.6 — Session History

**What it does:** Allows drivers to review past sessions and track progress over time.

**Functional Requirements:**

List View:
- Sessions sorted by date (most recent first)
- Per session: track, car, date, best lap time, session type, top opportunity from debrief
- Click to open full debrief

Free Tier: Last 5 sessions visible. Older sessions show greyed-out cards with "Upgrade to Pro to access full history."

Pro Tier: Complete history, no limit.

**Acceptance Criteria:**
- Session list loads in under 2 seconds
- Clicking a session opens the stored debrief (does not regenerate)
- Free tier limit is enforced consistently
- Sessions are never deleted unless the user explicitly requests it

---

### Feature 1.7 — Delta Conversations (Pro Only)

**What it does:** Allows Pro drivers to ask Delta follow-up questions after reading their debrief.

**Functional Requirements:**
- Chat interface attached to each debrief
- Delta has full context of: current session debrief, current Driver DNA, driver onboarding answers
- Delta answers questions about the session, the driver's tendencies, or specific recommendations
- Delta does not have access to general racing knowledge outside of what's grounded in the driver's data (it's a race engineer, not a search engine)
- If a question requires data Delta doesn't have, Delta says so clearly

**Conversation Limits:**
- 20 messages per session conversation (prevent abuse)
- Conversations are stored and reviewable

**Delta Conversation Behavior:**
- Stays in character (calm, professional, evidence-based)
- Does not answer questions unrelated to the driver's racing (e.g., "what's the weather in Monaco?")
- If asked to fabricate data: *"I can only work with what's in your telemetry. I don't want to guess."*

**Acceptance Criteria:**
- Response latency under 5 seconds for typical questions
- Context from the session debrief is always present in responses
- Conversation history is preserved and viewable later
- 20-message limit is clearly communicated before it's reached

---

### Feature 1.8 — Subscription & Billing

**What it does:** Manages Free and Pro tier access, upgrades, and billing.

**Functional Requirements:**
- Free tier is available without a credit card
- Pro upgrade via Stripe checkout
- Monthly and annual billing options (annual at a discount)
- Subscription management: view plan, cancel, update payment method
- Cancellation: access continues until end of billing period
- Failed payment handling: grace period of 3 days before downgrade to Free

**Usage Indicator (Free Tier):**
- Always visible on the upload page and dashboard: "X of 3 sessions used this month"
- Resets on the 1st of each month (based on UTC)

**Acceptance Criteria:**
- Upgrade flow completes in under 2 minutes
- Cancellation is available without contacting support
- Downgrade from Pro to Free does not delete data — it limits access
- All billing is handled by Stripe; TrackDelta never stores card numbers

---

## 2. Explicit Exclusions — Version 1

This section is as important as the feature list. Scope creep kills MVPs. Every item below was considered and deliberately deferred.

| Feature | Why Excluded | When to Revisit |
|---|---|---|
| Assetto Corsa Competizione | Different telemetry format (`.ld`), doubles parser work, splits focus | Phase 2, after iRacing validation |
| rFactor 2 / other sims | Same as above, smaller audience | Phase 3+ |
| Desktop companion app (auto-upload) | Manual upload validates coaching value first; friction is acceptable for MVP | Phase 2 if upload friction is cited as retention barrier |
| Real-time / live telemetry | Fundamentally different architecture; WebSocket pipeline is a separate product | Phase 5+ |
| Video analysis | Complex ML capability separate from telemetry; significant cost | Phase 4+ |
| Setup recommendations | Requires car physics model, setup database; enormous scope | Phase 4+ |
| Mobile application | Drivers debrief at their rig; desktop-first is appropriate for MVP | Phase 3 if mobile usage data warrants it |
| Social features / sharing | Privacy complexity; adds distraction from core coaching loop | Phase 3+ |
| Leaderboards / peer comparison | Shifts focus from self-improvement to comparison; conflicts with "Coach, Don't Judge" | Evaluate carefully; may never fit brand |
| Team / coach portal | B2B product requires separate design; different buyer, different UX | Phase 4+ |
| iRacing API integration | iRacing does not offer a first-party public API for telemetry; file-based is correct | Re-evaluate if iRacing opens API |
| AI-generated visualizations / charts | Adds UI complexity without proving core value | Phase 2 after core coaching proven |
| Email digests / reports | Not core to the session loop; adds infrastructure | Phase 3 |
| Two-factor authentication | Good security practice; not blocking for MVP | Phase 2 |
| Social login (Google / Apple) | Reduces signup friction but adds OAuth complexity; acceptable for MVP | Phase 2 |
| Third-party API / webhooks | No external consumers yet | Phase 4+ |
| Offline mode | Web-based MVP; offline not required | Evaluate with desktop app |

---

## 3. Definition of Done

A feature is done when:
1. It works correctly on Chrome, Firefox, and Edge (desktop)
2. It handles error states gracefully (no unhandled exceptions shown to users)
3. It is covered by unit tests for core business logic
4. It passes a manual QA pass by a team member who did not build it
5. It is accessible to keyboard navigation and meets WCAG AA contrast standards
6. It performs within defined latency targets (defined per feature above)

A feature is not done because it works on the builder's machine.

---

## 4. MVP Success Gate

Before declaring the MVP complete and opening to beta users, the following must all be true:

- A complete `.ibt` session can be uploaded and produce a full coaching debrief end-to-end
- Driver DNA generates and updates correctly across at least 3 sequential sessions
- Delta's debrief is reviewed by 3 internal testers who all confirm: "This coaching is specific to my driving, not generic"
- The estimated time available is suppressed or labeled Very Low Confidence for sessions with insufficient data
- The system handles a processing failure gracefully (user is notified; no data is lost)
- Free tier limits are enforced correctly
- Pro upgrade flow works end-to-end including Stripe

If any of these are not true, the MVP is not done.
