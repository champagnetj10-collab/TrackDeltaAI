# Landing Page A/B Testing Ideas

Test ideas grounded in the actual current landing page (`frontend/app/page.tsx`) and pricing page (`frontend/app/pricing/page.tsx`). **This document proposes tests; it does not implement them.** Running actual A/B tests requires an experimentation tool/flagging setup, which is a separate engineering task — do not modify the frontend code based on this document without that infrastructure decision made first.

---

## 1. Testing Discipline (apply to every test below)

- One variable per test — never change the headline and the CTA color in the same test, or you won't know which change drove the result
- Define the success metric *before* launching the test — for this product, prioritize "started registration" and "completed first upload" over raw click-through, since a click that doesn't lead to an activated user isn't worth much (mirrors the North Star metric discipline from the roadmap)
- Minimum sample size before calling a winner — don't stop a test after a few dozen visitors; talk to whoever owns analytics (file 21) about what's statistically meaningful given actual traffic volume
- Never run a test that would require the copy to say something untrue about the product — brand voice guide rules apply to test variants exactly as much as to the shipped version

---

## 2. Hero Section Tests

**Current copy:** Headline "The engineer who knows how you drive." / Subhead about Delta analyzing telemetry and Driver DNA / Primary CTA "Start for free" / Secondary CTA "See pricing"

| Test | Variant A (current) | Variant B | Variant C |
|---|---|---|---|
| Headline | "The engineer who knows how you drive." | "Stop guessing why you're losing time." (pain-first framing) | "Your telemetry, finally explained." (benefit-first, plainer) |
| Primary CTA copy | "Start for free" | "Get your first debrief free" (more specific to the actual deliverable) | "Upload your first session" (most literal/direct) |
| Subhead length | Current 3-sentence version | Shorter, single-sentence version | Longer version explicitly naming the free tier limit up front |
| Hero visual | Current TelemetryShowcase panel (radar + trace + corner deltas) | Same panel but leading with a real (permissioned) user's debrief screenshot once available | Video/GIF loop of the actual upload → debrief flow instead of a static panel |

**Hypothesis to test first:** pain-first vs. benefit-first headline framing, since the brand voice guide's audience research suggests this driver already feels the frustration (PRD's "The Frustration" framing) — worth validating which framing converts better rather than assuming.

---

## 3. Pricing Page Tests

**Current copy:** Free ($0, 3 sessions/mo) vs Pro ($29/mo, unlimited), "Most popular" badge on Pro, FAQ accordion below.

| Test | Variant A (current) | Variant B |
|---|---|---|
| Plan order | Free card left, Pro card right | Pro card left/emphasized, Free card secondary (tests whether leading with the more expensive option anchors perception of value) |
| "Most popular" badge | Present on Pro | Removed, replaced with a specific stat once available ("Chosen by X% of active drivers") |
| Annual pricing | Not currently offered | Add an annual option at a discount, test take-rate before committing engineering time to build real annual billing |
| FAQ order | Current order (telemetry support → cancel → rollover → privacy) | Privacy/trust question moved to position 1, testing whether trust-first ordering reduces bounce for skeptical first-time visitors |

---

## 4. Social Proof Tests (once real data exists — do not fabricate any of this pre-launch)

Once there are real users:
- Test adding a specific, honest stat near the hero CTA (e.g., "X sessions analyzed so far") vs. no stat at all — small, honest numbers can sometimes hurt more than help if they read as "not many people use this yet"; test rather than assume
- Test adding 1-2 real (permissioned) testimonial quotes on the landing page vs. none
- Test a "as seen in" or "used by drivers who race with [creator]" line once a real creator collab exists — never before

---

## 5. Upload/Onboarding Flow Tests

- Test the exact free-tier framing at the point of first upload: "3 sessions per month, no card required" (current) vs. a version that explicitly previews what they'll get ("Your first debrief in under 2 minutes")
- Test whether showing the processing-step stepper (already built, see the upload page redesign) with slightly more/less educational copy during the wait affects drop-off during the ~90-second processing window

---

## 6. What This Requires Before Any Test Actually Runs

- A feature-flagging or A/B testing tool wired into the Next.js frontend (e.g., a lightweight approach using Vercel Edge Config / middleware-based variant assignment, or a third-party tool) — not built yet, a real engineering decision
- Analytics events firing on the actual success metrics (registration started, registration completed, first upload completed) — ties directly to file 21's KPI definitions and needs to exist before any test result can be trusted
- A documented rollback plan for any losing variant

## 7. Sequencing

Per [ROADMAP.md](../ROADMAP.md), formal A/B testing infrastructure is a post-M4 (launch-readiness) concern — don't let testing-infrastructure work compete with M1-M4 priorities. Pre-infrastructure, use qualitative signal instead: watch session recordings (if a tool like that gets added) and direct user feedback to make informed one-at-a-time copy changes, and log what changed and when so a later, more rigorous test can validate or correct the informal decision.
