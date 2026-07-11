# Email Onboarding Sequence

Full email copy for the post-registration lifecycle. **This is content only — sending infrastructure (Resend, per the project's tech stack) needs to be configured and wired to these triggers as a separate engineering task.** Email verification/password-reset transactional emails already exist in the auth flow; this sequence is the *marketing/lifecycle* layer on top of that.

Voice: brand-account voice per [01_Brand_Voice_and_Style_Guide.md](01_Brand_Voice_and_Style_Guide.md) §4 — calm, specific, no hype. Subject lines follow the same rule as thumbnails: no false urgency, no clickbait.

---

## Sequence Overview

| # | Trigger | Goal |
|---|---|---|
| 1 | Immediately after email verification | Welcome, set expectations, remove friction to first upload |
| 2 | 24 hours after verification, if no session uploaded yet | Reduce friction, answer the most likely blocker |
| 3 | Immediately after first debrief completes | Reinforce value while it's freshest |
| 4 | 5-7 days after first debrief, if no second session uploaded | Nudge toward session #2 (this is the critical retention moment) |
| 5 | After 3rd completed session | Introduce DNA confidence progress + soft Pro mention |
| 6 | If free-tier limit hit for the month | Clear, honest upgrade prompt |
| 7 | 30 days of inactivity | Honest win-back, no guilt-tripping |

---

## Email 1 — Welcome (sent immediately after verification)

**Subject:** You're in. Here's how to get your first debrief.

```
Hey [First Name],

Welcome to TrackDelta.

Here's the whole process:
1. Upload your latest iRacing .ibt file (find it at Documents → iRacing → telemetry)
2. Delta parses it and builds your first Driver DNA snapshot
3. You get a full debrief — not a dashboard, an actual written breakdown of what happened and what to work on next

Your first session will have low confidence in a few areas, and that's expected — Delta is honest about what it doesn't know yet. It gets more accurate every session.

Upload your first session: [link]

If anything's unclear or breaks, just reply to this email — a real person reads these.

— The TrackDelta AI team
```

---

## Email 2 — Friction Reduction (24h after verification, no upload yet)

**Subject:** Where to find your .ibt file (30 seconds)

```
Hey [First Name],

Noticed you haven't uploaded a session yet — totally fine, just want to make sure the file location isn't the blocker.

Your .ibt files live at:
Documents → iRacing → telemetry

Any session works — practice, qualifying, race, doesn't matter. Drag it in here: [link]

If it's something else entirely (a bug, confusion about what this even does, anything), reply and tell me — genuinely helps.

— The TrackDelta AI team
```

---

## Email 3 — Post-First-Debrief Reinforcement (sent right after first debrief completes)

**Subject:** Your first debrief is ready

```
Hey [First Name],

Your first debrief is in: [link to debrief]

A few honest notes on session one specifically:
- Confidence will be low on most attributes right now — one session isn't enough for Delta to be sure of anything yet
- The "one clear objective" line is the single most useful thing to act on before your next session
- Your Driver DNA already exists and will keep sharpening from here

Upload session two whenever you're ready — that's when you'll actually start seeing the model move: [link]
```

---

## Email 4 — Second-Session Nudge (5-7 days after first debrief, no second upload)

**Subject:** One session isn't enough to know you yet

```
Hey [First Name],

Real talk: Delta's read on you after one session is a preliminary guess, not a real profile. The second and third sessions are where it actually starts to mean something.

If the first debrief felt useful, the fastest way to get real value out of this is just... another session, whenever you next race: [link]

If it didn't feel useful, I'd genuinely like to know why — reply and tell me what fell flat.
```

---

## Email 5 — Third-Session Milestone (after 3rd completed session)

**Subject:** Your Driver DNA just crossed into "Low → Moderate" confidence

```
Hey [First Name],

Three sessions in. Here's what's different now: [link to DNA page]

Patterns are starting to show up that one or two sessions can't reveal — consistency trends, recurring corners, whether your braking style is stable or still shifting.

If TrackDelta's become a real part of your post-session routine, Pro removes the monthly session cap and unlocks the full DNA history view, per-corner breakdown, and the ability to ask Delta follow-up questions about your own debrief: [link to /pricing]

No pressure either way — just flagging it now that there's enough history for it to actually matter.
```

---

## Email 6 — Free Tier Limit Hit

**Subject:** You've used your 3 free sessions this month

```
Hey [First Name],

You've hit the free tier's 3 sessions for this month. Nothing lost — it resets on the 1st, and everything you've built so far (your Driver DNA, past debriefs) stays exactly as it is.

If you'd rather not wait: Pro is $29/month, unlimited sessions, no cap. [link to /pricing]

Either way, see you next session.
```

---

## Email 7 — Win-Back (30 days inactive)

**Subject:** No pressure, just checking in

```
Hey [First Name],

Haven't seen a session from you in a while. No guilt trip here — just want to check the product isn't the reason.

If something about the debrief wasn't useful, or something broke, or life just got busy — any of those is a totally normal reason, and I'd genuinely like to know which one it was if you're up for a one-line reply.

If you do come back, your Driver DNA is still exactly where you left it: [link]
```

---

## Copy Principles Applied Throughout

- Every email is honest about confidence/certainty exactly the way the product itself is (Truth Over Confidence extends to lifecycle emails, not just in-app copy)
- No fake urgency, no countdown timers, no "act now" pressure — this audience is allergic to it (brand voice guide §2)
- Every email has exactly one clear CTA, never a wall of links
- Founder-accessible tone ("reply and tell me") — early on, actual replies should route to a real person, not an unmonitored inbox

## Implementation Notes for Engineering (when this gets built)

- Triggers 1-2 depend on the existing auth/verification event and an "uploaded first session" check against the `sessions` table
- Trigger 3 depends on the `processing_status == "completed"` transition already implemented in the pipeline
- Trigger 5 depends on `total_sessions` on the `driver_dna` table crossing 3
- Trigger 6 depends on the existing `monthly_uploads_used >= free_tier_monthly_uploads` check already enforced server-side in `sessions.py`
- Trigger 7 depends on a scheduled job checking last session date — doesn't exist yet, needs a scheduler (Celery beat or similar)
