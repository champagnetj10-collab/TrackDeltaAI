# TrackDelta AI — User Journey
**Document:** 02 of 05  
**Version:** 1.0  
**Status:** Engineering & Design Reference  
**Date:** June 30, 2026

---

## Overview

This document maps the complete experience of a TrackDelta driver — from discovery through their first session debrief to becoming a regular user. It captures both the functional steps and the emotional state of the driver at each moment.

The emotional journey matters as much as the functional one. Our driver is often frustrated after a session, uncertain about what to work on, and skeptical of another telemetry tool that won't tell them anything they couldn't figure out themselves. Every interaction should move them from frustration toward clarity and confidence.

---

## Journey 1 — First-Time User (New Account to First Debrief)

### Stage 1: Discovery & Arrival

**Context:** The driver heard about TrackDelta from a Discord server, a Reddit post, or a fellow league racer. They are curious but guarded. They have probably tried other telemetry tools and found them complex or generic.

**Emotional state:** Skeptical. Hopeful but not optimistic. "I'll give it a shot."

**What happens:**
- Driver lands on the TrackDelta marketing page
- They see Delta described not as telemetry software but as an AI race engineer that learns how *they* drive
- The value proposition is clear within 10 seconds: upload a session, get coaching from Delta
- CTA: "Start for free — no credit card required"

**Design principle:** The landing page must answer the skeptic's question immediately: *"How is this different from what I already have?"* The answer is not features — it is philosophy. Delta knows you. It doesn't compare you to an ideal lap. It coaches you based on how *you* drive.

---

### Stage 2: Account Creation

**Steps:**
1. Driver clicks "Start for free"
2. Registration form: display name, email address, password
3. Driver submits form → email verification sent
4. Driver clicks verification link → account confirmed
5. Redirected to onboarding

**Emotional state:** Cautious optimism. They want to get to the product quickly. Every unnecessary step here costs goodwill.

**Design principle:** Minimal friction. No address, no phone number, no card. Name, email, password. Done.

**Error states:**
- Email already registered → clear message with link to login or password reset
- Weak password → inline guidance on requirements before submission
- Verification email not received → resend option available after 60 seconds

---

### Stage 3: Onboarding

**Steps:**

**Screen 1 — Welcome from Delta**
Delta speaks directly to the driver for the first time. Tone: calm, professional, honest.

> *"I'm Delta — your AI race engineer. I'm going to help you become a faster, more consistent driver.*
>
> *But I want to be upfront with you: after your first session, my confidence in your driving profile will be low. That's honest, not a limitation. Every session I analyze makes me better at understanding how you drive. The more we work together, the more useful I become.*
>
> *Let's start with a few quick questions."*

**Screen 2 — Four Questions**

Progress indicator: Step 1 of 4

Q1: "How long have you been racing on iRacing?"
- Less than 6 months
- 6 months to 2 years
- 2 to 5 years
- 5+ years

Q2: "What's your approximate iRating?"
- Under 1,000
- 1,000 – 2,000
- 2,000 – 3,500
- 3,500+

Q3: "What's your primary goal right now?"
- Find more raw pace
- Improve my consistency
- Prepare for competitive league racing
- Better understand my driving style

Q4: "What frustrates you most after a session?"
- I know I'm losing time but don't know exactly where
- My lap times are inconsistent and I don't know why
- I don't know what to practice next
- I have no one to debrief with

Each question is a single screen. Large tap targets. Fast to complete.

**Screen 3 — Your Driver DNA Has Started**

> *"Based on what you've told me, I've initialized your Driver DNA. Right now it's almost empty — just a starting point. After your first session, I'll begin filling it in.*
>
> *Driver DNA is never finished. It grows with every lap you share with me."*

Shows a visual of a nearly-empty DNA card with placeholder values and "Data needed" labels.

**Screen 4 — Upload Your First Session**

> *"You're ready. Upload your most recent iRacing session and I'll get to work.*
>
> *Your .ibt files are in: Documents → iRacing → telemetry → [track name]*
>
> *I'll have your coaching debrief ready in about 60 seconds."*

Large upload CTA. File path guidance prominent. Option to "remind me later" if they want to return.

**Emotional state at end of onboarding:** The driver understands what Delta is. They have been treated honestly. They are ready to upload. They feel like this is different — not because of hype, but because Delta spoke to them directly and set honest expectations.

---

### Stage 4: First Upload

**Steps:**
1. Driver locates their `.ibt` file (with path guidance provided in onboarding)
2. Drags file onto upload zone or uses file picker
3. Optional: types a session note ("Working on Turn 3 braking, struggled with consistency")
4. Clicks upload

**Processing states (displayed in sequence):**

| State | Message | Estimated duration |
|---|---|---|
| Uploading | "Uploading your session..." + progress bar | 5–30 seconds |
| Reading Session | "Reading session data... [Track Name], [Car], [N] laps" | 5–15 seconds |
| Analyzing with Delta | "Delta is analyzing your session..." | 20–60 seconds |
| Ready | "Your coaching debrief is ready." | — |

During the "Analyzing with Delta" state, a brief, non-promotional message rotates:
- *"Delta is looking at your braking zones, throttle application, and corner exits."*
- *"Driver DNA is updating based on what Delta finds in this session."*
- *"Delta only shares recommendations it can support with data from your laps."*

These build expectation for what the debrief will contain. They reinforce the "Truth over Confidence" principle even during loading.

**Error states:**
- Wrong file type: "This file doesn't look like an iRacing telemetry file. Look for a .ibt file in Documents → iRacing → telemetry."
- File too large: "This file is larger than 250 MB. Large sessions can sometimes be split by iRacing. Try uploading the most recent portion."
- Processing failure: "Something went wrong while analyzing this session. We've logged the error. Please try again — if it fails a second time, contact support." [Retry button visible]
- Insufficient laps: "This session only contains [N] laps. Delta needs at least 5 complete laps to generate a reliable coaching debrief. Try uploading a longer session."

---

### Stage 5: First Debrief

This is the moment. Everything before this was setup. The debrief must earn the driver's trust immediately.

**What the driver expects:** Another generic analysis. Graphs. Tips they've already heard.

**What they should get:** Delta telling them something specific about *how they drive* that no other tool has ever said to them.

**The first debrief experience:**

The debrief page loads. The driver's name appears in the header. Delta's overview appears first — not a summary of features, but an observation from this specific session.

The first sentence should reference something concrete. Not: *"You had a productive session today."* But: *"Your pace in the first half of this session was strong — laps 8 through 14 put you consistently within 0.3 seconds of your best. The second half dropped off, and I want to show you where."*

As the driver reads down:
- The opportunities section names corners specifically. The driver recognizes those corners. They know Turn 7. Delta knowing Turn 7 — and what happened there — is surprising and credible.
- The strengths section says something the driver did not know about themselves. It names a thing they do well that they haven't been able to see in a graph.
- The estimated time available section is honest about its uncertainty. This builds trust, not doubt.
- The DNA update section is brief but meaningful: *"I'm just getting started understanding how you drive. After a few more sessions, this profile will tell a much clearer story."*
- The practice plan is specific. The driver can do these things. They are not generic.
- One Clear Objective is something they will think about.

**Emotional state at end of first debrief:** If the debrief has done its job, the driver feels something specific and rare: *"Delta saw what I couldn't see."*

That feeling — not the feature list, not the UI, not the price — is what converts a first-time visitor into a returning user.

---

### Stage 6: Post-Debrief

**What happens after reading:**

- Driver can explore their Driver DNA profile (now has initial data)
- Driver can ask Delta a follow-up question (Pro) or is prompted to upgrade (Free)
- Driver sees their session in the session history (first entry)
- Clear prompt: "Come back after your next session. Delta will remember everything from today."

**Free tier prompt (if applicable):**
"You have 2 sessions remaining this month. Delta's coaching improves with every session — consider upgrading to Pro for unlimited uploads."

---

## Journey 2 — Return User (Ongoing Session Loop)

This is the loop that makes TrackDelta a habit. The driver finishes a session, opens TrackDelta, uploads, and reads the debrief. Then they practice the objective. Then they do it again.

### Stage 1: Post-Session (The Habit)

**Context:** The driver has just finished an iRacing session. They may have driven well or poorly. They are curious about what Delta found.

**Emotional state:** Variable — could be frustrated, energized, confident, or disappointed. Delta must meet them where they are.

**What happens:**
1. Driver closes iRacing
2. Opens TrackDelta (ideally in a bookmarked browser tab)
3. Navigates to "Upload Session"

---

### Stage 2: Upload (Familiar, Fast)

By the second session, the driver knows where to find their `.ibt` file. The upload experience should be identical — frictionless, predictable.

The session note field is more valuable here: "Tried moving brake point later at T3 per last week's objective." This note is referenced by the coaching engine and Delta can acknowledge progress directly.

Processing states are the same. The driver trusts them now.

---

### Stage 3: Return Debrief

**What's different from the first debrief:**

Delta now has context. The return debrief should feel noticeably more personal than the first.

**Delta's overview references the previous session:**
> *"Last session, I asked you to focus on your brake point at Turn 3. Let's see what happened."*

Or if they didn't improve:
> *"The Turn 3 brake point is still earlier than optimal — I don't think last session's practice reached it yet. That's not a concern; this is a pattern that takes time to change. Let me show you what I did see improve."*

This is the moment when the driver realizes Delta remembers. That Delta is tracking their development, not just processing data. This is when the product becomes a relationship.

**DNA updates should be clearly visible:**
- "Your consistency score moved from 6.2 to 7.1 this session. Three sessions of focused work on the same track is showing results."
- "I've upgraded the confidence in your braking profile from Low to Moderate. I now have enough data to say with reasonable confidence that you are a late braker with a tendency toward early release."

---

### Stage 4: Acting on Coaching

The practice plan and one clear objective are the driver's north star until their next session.

Between sessions, drivers may:
- Return to TrackDelta to re-read the debrief (stored, no regeneration)
- Ask Delta follow-up questions (Pro): "Why does releasing the brakes early cost me time? I thought I was doing it right."
- View their Driver DNA profile to see it evolving

**The loop closes:** The driver gets on track. They try the objective. They upload the next session. Delta tells them if it worked.

This is the flywheel. This is why TrackDelta must be a habit, not an occasional tool.

---

## Journey 3 — Upgrade to Pro

### Trigger Points (Natural Upgrade Moments)

The driver should feel the value of Pro before they see the paywall. The best moment to present an upgrade is when the driver wants something they cannot have on Free.

**Trigger 1 — Delta Conversations**
After reading their debrief, the driver wants to ask Delta a follow-up question. They click the chat icon. A message appears:

> *"Delta conversations are available on Pro. Delta would answer your question — and remember this conversation when you upload your next session."*
> 
> [Upgrade to Pro — $X/month] [Maybe later]

**Trigger 2 — Session History Limit**
The driver wants to compare today's session to one from 6 weeks ago. Older sessions are shown but greyed out:

> *"Your full session history is available on Pro. Unlock complete access to see how your driving has evolved."*

**Trigger 3 — Monthly Upload Limit**
The driver has used all 3 free sessions for the month and wants to upload another:

> *"You've reached your 3-session limit for June. Upgrade to Pro for unlimited sessions — Delta's coaching improves with every upload."*

**Trigger 4 — DNA Progress Teaser**
In the DNA profile, an expanded view (blurred) shows what the full profile looks like at High Confidence:

> *"Full Driver DNA with advanced attributes is available on Pro. More data, more confidence, more personalized coaching."*

### Upgrade Flow

1. Driver sees trigger and clicks upgrade CTA
2. Plan selection: Monthly ($X/mo) or Annual ($X/mo, X% savings)
3. Stripe checkout (hosted, secure)
4. Confirmation screen: "You're now on Pro. Unlimited sessions. Full Driver DNA. Delta conversations."
5. Redirect to session history or DNA profile — immediately showing what's now unlocked

---

## Journey 4 — Error & Edge Cases

### Not Enough Laps

If a session contains fewer than 5 complete laps:
> *"Delta needs at least 5 complete laps to generate a reliable coaching debrief. This session only has [N]. Upload a longer practice session for a full analysis."*

No partial debrief is generated. Better to be honest than to produce something unreliable.

### First Session on a New Track

When a driver uploads a session on a track Delta has not seen them race before:
> *"This is your first session at [Track Name] in Delta's memory. Delta doesn't yet have your tendencies for this specific circuit — the coaching here is based on your overall Driver DNA and will become more track-specific over time."*

This sets honest expectations and prevents confusion when coaching feels less precise than on a familiar track.

### Track Not in Reference Database

If the session is on a track not yet in TrackDelta's track reference database:

> *"Delta doesn't have corner reference data for [Track Name] yet. Basic session analysis is available, but corner-level coaching is limited. We're expanding our track database regularly — this track is queued for addition."*

A reduced debrief is delivered: session-level metrics, consistency analysis, and general Driver DNA update. No per-corner coaching. Be honest about why.

### Processing Failure

> *"Something went wrong during analysis. This isn't a problem with your telemetry file — it's on our side. We've been notified. Please try uploading again in a few minutes. If the problem persists, contact support and we'll investigate."*

No blame on the driver. No technical jargon. Clear next step.

### Very Low Data Quality Session

If a session contains excessive incidents, many incomplete laps, or highly erratic data (potential controller disconnect):
> *"This session had some data quality issues — possibly a controller disconnect or a high number of incidents. Delta completed an analysis, but confidence in these findings is lower than usual. The coaching below reflects what Delta could reliably identify."*

Deliver a reduced debrief with explicit confidence warnings throughout.

---

## Design Principles for the Journey

**1. Delta speaks first.** Every significant screen where Delta could add voice, Delta should. This is not a dashboard — it is a relationship between the driver and their engineer.

**2. Honesty at every step.** Low confidence is communicated early and often, especially in the first sessions. Drivers who are told the truth early will trust the product when it becomes confident later.

**3. Forward momentum.** Every screen should point to the next action. After the debrief: go practice. After practice: come back and upload. The loop is the product.

**4. No dead ends.** Every error state has a next step. Every empty state has an explanation and a way forward.

**5. The driver's name and their track.** Personalization at the simplest level matters. "Turn 7 at Watkins Glen" is more powerful than "a medium-speed corner."
