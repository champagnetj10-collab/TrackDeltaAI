# Creator Outreach — Message Templates

**Goal of every message here:** recruit an experienced sim racer to *test and criticize*
TrackDelta. Not to buy sponsorship. Not to get a shoutout. If a message reads like an ad
request, it's wrong.

---

## ⚠️ BLOCKER — do not send anything yet

Before a single one of these goes out, two things have to be true:

1. **`ANTHROPIC_API_KEY` must be live on Railway.** Right now it's a placeholder. A tester
   can upload a real `.ibt`, watch it process, and get **no debrief at all** — the one thing
   we're asking them to evaluate. Inviting a respected coach to test a product that cannot
   currently produce its core output is the fastest possible way to burn credibility with
   this exact community.
2. **One real `.ibt` with completed laps must run end-to-end successfully.** The parser has
   only ever been validated against a 56-second file with zero completed laps. Lap-splitting
   is still unverified against real data.

Everything below is ready to go the moment those two clear. Sending before then isn't
"moving fast," it's spending the one first impression we get on a broken demo.

---

## Sending discipline (deliverability)

`trackdeltaai.com` is a new domain with no sending reputation. Cold email from a cold domain
at volume gets you spam-foldered or blacklisted — and that would also break Supabase's auth
and password-reset emails, which ride the same domain reputation.

**Ramp schedule — do not skip:**

| Week | Max cold sends/day | Notes |
|---|---|---|
| 1 | 3–5 | Hand-sent, watch for bounces. Any bounce → stop, fix the list. |
| 2 | 5–8 | Only if week 1 had zero bounces and at least one reply. |
| 3 | 8–12 | |
| 4+ | 12–20 | Ceiling. Only with a warmed domain and a clean bounce rate. |

Other rules:
- **Never** send to a guessed address. A bounce costs more than a missed prospect.
- Keep a real reply-to that a human monitors (hello@trackdeltaai.com).
- Plain text. No tracking pixels, no images, no link shorteners — all three are spam signals
  and all three feel gross to a creator who notices.
- Max 2 follow-ups. Then stop. Permanently.

---

## Email 1 — Initial (long-form, for creators with a public business email)

**Subject options** (pick per creator, don't A/B test on a list this small):
- `question from someone building a coaching tool`
- `building something and I need someone to tell me it's wrong`

**Body — Tom Noakes version (READY TO SEND once blocker clears):**

> Hi Tom,
>
> I read the story on your site about the seven iRacing accounts — quitting, letting the sub
> lapse, coming back months later hoping it'd be different. Then November 2023, where instead
> of grinding more laps you actually studied telemetry and went to 5k iRating in two months.
>
> That's basically the thesis of the thing I'm building, so I'd rather hear from you than
> from almost anyone else — including if you think it's a bad idea.
>
> I'm building TrackDelta AI. It reads your `.ibt` file and writes you a debrief. But the part
> I actually care about isn't "you braked 18m early at turn 7" — most tools already do that.
> It's trying to model *why* you drive the way you do across many sessions. Whether you're
> naturally a late braker who needs a setup that tolerates it, or someone whose consistency
> collapses under pressure specifically. Something closer to a race engineer who's known you
> for a season than a tool that diffs you against one reference lap.
>
> I'm not asking you to promote anything. I'm asking you to break it. Free access, upload real
> telemetry, and tell me honestly where it's wrong or useless. Especially if the answer is
> "this doesn't tell me anything I couldn't see myself in thirty seconds" — that's the most
> useful thing you could tell me.
>
> One thing I should say directly, because you'd think it anyway: you sell coaching at $67/hr
> and you're booked weeks out. I'm not trying to replace that, and honestly I don't think a
> tool can. The people I'm building for are the ones who can't get one of your slots or can't
> justify the money — the version of me who wanted to race and worked out early that the
> money wasn't there. If you look at it and think it undercuts what you do, I'd genuinely
> want to hear that too.
>
> Worth a look?
>
> — [Your name]
> TrackDelta AI · trackdeltaai.com

**Why this one works:** it opens with a specific, real detail only someone who read his site
would know (seven accounts, Nov 2023, the exact pivot), it names the competitive tension
before he has to, and it asks for criticism rather than promotion. No "I love your content."

---

## Email 1 — Generic skeleton (for creators after real research)

Fill the bracketed parts from **actual watched content**. If you can't fill `[SPECIFIC]`
with something real, don't send it.

> Hi [Name],
>
> [SPECIFIC — a real detail from a recent video or their own about page. What they said, what
> they were working through, why it stuck with you. One or two sentences. No flattery.]
>
> I'm building TrackDelta AI — it reads your iRacing `.ibt` file and writes a coaching debrief.
> The part I care about isn't telling you that you braked too early; it's trying to model
> *why* you drive the way you do over many sessions, and eventually tune coaching and setup
> around that instead of against a generic ideal lap.
>
> I'm not asking you to promote it. I'm looking for experienced racers to test it, upload real
> telemetry, and tell me where it's wrong. Free access, no strings. If you think it's useless
> I'd rather hear that now than after launch.
>
> [OPTIONAL — one honest sentence on why *their specific* audience or perspective would catch
> something I'd miss.]
>
> If it ends up being genuinely good and you want to talk about something more formal later,
> that door's open — but that's not what this is.
>
> — [Your name]
> trackdeltaai.com

---

## Email 2 — Follow-up #1 (send 4–5 days later)

Keep it shorter than the first. Add something, don't just "bump."

> Hi [Name] — following up once on the below, then I'll leave you alone.
>
> Since I wrote, [ONE REAL UPDATE — e.g. "I tested the parser against a real telemetry file
> for the first time and immediately found a bug that had been silently breaking one of the
> five driver-profile categories since day one. Fixed now, but it's a decent illustration of
> why I want real drivers on this instead of my own synthetic test data."]
>
> Still happy to hand over free access if you want to poke holes in it.
>
> — [Your name]

---

## Email 3 — Final follow-up (send 7 days after #2, then stop forever)

> Hi [Name] — last one from me, I promise.
>
> Leaving the door open: if you ever want early access to TrackDelta, just reply and it's
> yours, no expectations attached.
>
> Either way, [ONE GENUINE, SPECIFIC LINE — e.g. "the video on X was the clearest explanation
> of Y I've seen"]. Good luck with the channel.
>
> — [Your name]

---

## Short versions

### Instagram DM
> Hi [Name] — [SPECIFIC real detail, one line].
>
> I'm building an AI coaching tool for iRacing (reads your .ibt, writes a debrief, tries to
> model your actual driving style over time rather than compare you to one ideal lap).
>
> Not asking for a promo — looking for experienced racers to test it and tell me what's wrong
> with it. Free access. Interested?

### X / Twitter DM
> [SPECIFIC one-liner about their content].
>
> Building TrackDelta AI — reads your iRacing telemetry, writes a coaching debrief, models
> your driving style over sessions instead of diffing you against one reference lap.
>
> Looking for people to break it and tell me it sucks. Free access, no promo expected. Want in?

### Discord DM
*(Only after being a real participant in the server. Cold-DMing a Discord you just joined is
the fastest way to get banned and deserve it.)*

> hey [Name] — [SPECIFIC, casual, real].
>
> building an AI race engineer thing for iRacing. reads your .ibt and writes a debrief, but
> the actual idea is modelling *why* you drive how you drive across sessions rather than
> "here's where you're slower than the alien."
>
> not after a promo — want people who'll actually tell me it's rubbish if it is. free access
> if you want to try and break it

### Reddit DM
*(Read the subreddit rules first. Several sim racing subs ban unsolicited product DMs
outright. Contributing publicly and honestly is usually a better route than a DM.)*

> Hi — saw your [SPECIFIC post/comment] on r/[sub].
>
> I'm building an AI coaching tool for iRacing telemetry and I'm looking for experienced
> drivers to test it and tell me where it falls over. Free access, not asking you to promote
> anything.
>
> Happy to just send it over if you're curious — and equally happy to hear "no thanks."

---

## Founder post (for X / LinkedIn / Reddit / YouTube community tab)

Post this **before or alongside** outreach — it gives anyone who Googles you something real
to land on, and it does more work than any cold email.

> **Why I'm building TrackDelta AI**
>
> I wanted to be a racing driver.
>
> Not in a vague way. I loved the speed, the competition, the physical feeling of a car at the
> limit — the thing that makes you replay a corner in your head hours later.
>
> Then you find out what it costs. Not just the car and the track time. The coaching. The
> engineer who looks at your data and tells you what it means. A season of proper coaching
> costs more than a lot of families make in a year. For most people who love this sport, the
> ceiling isn't talent or effort. It's money. You find that out early and quietly stop
> mentioning it.
>
> I don't think that's how it should work. Not now, when the data exists and the tools to
> read it exist.
>
> So I'm building TrackDelta AI. You upload your iRacing telemetry and it writes you a debrief
> — but the goal isn't another tool that says "brake 18 metres later at turn 7." Plenty of
> those exist and they're fine. What I want is something that understands *why* you drive the
> way you do. That over many sessions learns you're a late braker who needs a setup that
> tolerates it, or that your consistency falls apart specifically under race pressure and not
> in practice. Something closer to an engineer who's known you for a season than a tool that
> compares you to a stranger's perfect lap.
>
> I should be honest about where this actually is: it's early, and I'm learning as I go. I
> found a bug last week — testing against a real telemetry file for the first time — that had
> been silently breaking part of the driver profile since the day I wrote it. My own tests
> never caught it because they were built on the same wrong assumption. That's the real
> version of building this, not the highlight reel.
>
> Which is exactly why I'd rather build it with racers than at them.
>
> If you race — sim or real — and you'd be willing to upload some telemetry, try it, and tell
> me honestly where it's wrong or useless, I'd genuinely like to hear from you. Especially if
> you think the whole idea is flawed. That's more useful to me right now than encouragement.
>
> [contact / link]
>
> — [Your name]

**Note on the founder post:** the specifics of *your* story need to be yours. I've written
the structure and the emotional beats from what you told me, but if any detail here isn't
literally true for you, change it. This post only works if it's true — and this community
in particular will smell a manufactured origin story immediately.
