# Outreach Daily Operating System

How to run creator outreach repeatably without it degrading into spam.

---

## The honest constraint on volume

You asked for 10–20 outreaches/day. That number is achievable, but not on day one and not
at the personalization quality this campaign depends on. Two independent limits:

**1. Deliverability.** New domain, no sending history. Going 0 → 20/day is the classic
pattern spam filters are built to catch. Getting `trackdeltaai.com` flagged also breaks your
Supabase signup/password-reset emails. See the ramp table in `26_Creator_Outreach_Templates.md`.

**2. Research time.** Honest personalization means actually watching 2–3 recent videos and
finding something real to say. That's 15–25 min per creator. 20/day = 6+ hours of research
daily. The volume that's actually sustainable solo is **5–8/day of genuinely researched
outreach**, or 15–20/day if you drop to shallow personalization — which is the thing you
explicitly said you didn't want.

**Recommendation:** target **5–8/day sustained**, ramping per the deliverability table.
That's 25–40/week, which against a realistic 15–25% reply rate for well-researched founder
outreach in a niche community is 4–10 conversations/week. That's plenty for a beta.

---

## Daily loop (about 90 minutes)

### Block 1 — Research (45 min, 3–4 creators)
For each creator:
1. Watch/skim 2–3 recent videos. Note one specific thing: a technique they explained, a
   struggle they described, a take you disagree with.
2. Find their contact route. **Published email only** — never guess. No public email → DM route.
3. Fill their row in `25_Creator_Outreach_Database.md`. Status → `RESEARCHED`.
4. If you couldn't find anything real to say → mark `SKIP`. That's a valid outcome, not a failure.

### Block 2 — Draft (30 min)
1. Use the skeleton in `26_Creator_Outreach_Templates.md`.
2. Replace every `[SPECIFIC]` with real detail. **If any bracket survives, it's not sendable.**
3. Read it out loud. If it sounds like marketing, rewrite it.
4. Save as Gmail draft. Status → `DRAFTED`.

### Block 3 — Send + log (15 min)
1. Send only drafts that clear the pre-send checklist below.
2. Log date sent, set follow-up date (+4 days). Status → `SENT`.
3. Check for replies. Reply to any human within 24h — this is the whole point.

---

## Pre-send checklist (per message)

- [ ] Name spelled correctly, correct person
- [ ] Contains a specific, true detail about *them* — not "I love your content"
- [ ] Every `[BRACKET]` replaced
- [ ] Does NOT ask them to promote/advertise
- [ ] Does ask for criticism explicitly
- [ ] Email address is published, not guessed
- [ ] Plain text, no tracking pixel, no shortened links
- [ ] Product can actually deliver what the email implies *(see blocker in file 26)*
- [ ] Read out loud, doesn't sound corporate or AI-written

---

## Weekly review (Fridays, 20 min)

Log in `25_Creator_Outreach_Database.md`:

| Metric | Target | Why it matters |
|---|---|---|
| Sent | 25–40 | Volume |
| Bounce rate | **0%** | Any bounce = list quality problem, stop and fix |
| Reply rate | 15–25% | Below 10% → personalization isn't landing, rewrite the opener |
| Positive replies | 3–8 | The actual goal |
| Onboarded testers | 2–5 | The *real* actual goal |
| Telemetry files received | ≥2 | The thing that unblocks parser validation |

**If reply rate drops below 10% two weeks running:** stop sending. The message is wrong, and
more volume makes it worse, not better. Rewrite the opener and test on 5.

---

## Follow-up cadence

| Touch | Timing | Rule |
|---|---|---|
| Initial | Day 0 | |
| Follow-up 1 | Day +4–5 | Must add something new, not just "bumping this" |
| Follow-up 2 | Day +11–12 | Final. Gracious, no ask, leaves door open |
| — | — | **Then stop permanently.** No third follow-up, ever. |

Three unanswered emails is where founder outreach becomes harassment. The sim racing
community is small and talks to each other; a reputation for pestering people spreads faster
than the product will.

---

## When someone replies

**Positive →** Send access same day. Ask for exactly one thing: a real `.ibt` with completed
laps. Don't dump a feature tour on them. Ask what they'd want it to tell them *before* they
see the output — that answer is worth more than the feedback afterwards.

**Critical →** Thank them properly and ask a follow-up question. A creator who tells you why
it's useless is more valuable than three who say "cool idea." Log the criticism verbatim in
the database Notes; do not paraphrase it into something more comfortable.

**"Not interested" / no reply →** Mark it, move on, never contact again. Don't retarget them
in six months. Don't add them to a newsletter.

**Asks about payment/sponsorship →** Be straight: there's no budget right now, this is genuinely
a "help me build it" ask, and if it becomes good and they like it, that conversation can happen
later. Don't imply a payday that doesn't exist.

---

## Guardrails

- Never invent personalization. If you don't know something real, do the research or skip.
- Never contact direct competitors (Trophi.ai / Driver61, VRS, Coach Dave) posing as a fan.
- Never claim TrackDelta is the first or only AI coaching tool — this niche knows better.
- Never send to a guessed address.
- Never send before the product can do what the email implies.
- Respect subreddit and Discord rules on unsolicited DMs. Participate before pitching.
