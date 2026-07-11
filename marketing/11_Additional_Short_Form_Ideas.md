# 100 Additional Short-Form Video Ideas (SF-51–SF-150)

Continues numbering from [03_Short_Form_Video_Ideas.md](03_Short_Form_Video_Ideas.md) (SF-01–SF-50) — these are new angles/formats, not repeats. Same storyboard structure ([05_CapCut_Editing_Template.md](05_CapCut_Editing_Template.md)) and CTA bank apply. Read [01_Brand_Voice_and_Style_Guide.md](01_Brand_Voice_and_Style_Guide.md) first.

**New formats introduced in this batch, not present in the original 50:** myth-busting, deep engineering explainers, track/car-class-specific content, reaction/duet/stitch, "Ask Delta" Q&A, data storytelling, honest competitive positioning, fast-numbers explainers, multi-part cliffhanger series, and UGC/community challenge prompts.

---

## Batch 6 (SF-51–60): Sim Racing Myth-Busting

**SF-51 — "Myth: later braking = faster lap"** (Education/Myth, 25s)
- Hook: "Everyone thinks later braking is the answer. The data says it's not that simple."
- Script: Show two laps — later brake point, slower overall lap due to lock-up/missed apex, vs. earlier smoother brake point, faster exit.
- Caption: "Brake point alone doesn't predict lap time. Modulation does. #SimRacingMyths #TrackDeltaAI"
- CTA: "Check your own brake data — link in bio."

**SF-52 — "Myth: more throttle = more speed"** (Education/Myth, 25s)
- Hook: "Flooring it earlier isn't always the fast way out of a corner."
- Script: Show wheelspin/instability from early full throttle vs. progressive roll-on reaching full throttle sooner in distance-covered terms.
- Caption: "Progressive beats aggressive, almost every time. #SimRacingMyths"
- CTA: "See your throttle trace — link in bio."

**SF-53 — "Myth: a smooth driver is always a slow driver"** (Education/Myth, 20s)
- Hook: "Smooth doesn't mean slow. It usually means the opposite."
- Script: Show a smooth steering/throttle trace correlating with a genuinely fast, consistent lap.
- Caption: "Smoothness is speed, not the absence of it. #SimRacingMyths #TrackDeltaAI"
- CTA: "Link in bio."

**SF-54 — "Myth: iRating tells you how fast you are"** (Education/Myth, 25s)
- Hook: "Your iRating and your actual pace are two different numbers."
- Script: Explain iRating reflects race results relative to a field, not raw pace; show a high-iRating driver's consistency score as the more telling stat.
- Caption: "iRating is a rating. Pace is a stat. Not the same thing. #SimRacingMyths"
- CTA: "See your real pace data — link in bio."

**SF-55 — "Myth: you need to fix everything at once"** (Education/Myth, 20s)
- Hook: "Trying to fix five things next session is why you fix zero things."
- Script: Show a cluttered "todo list" style debrief (bad example) vs. TrackDelta's single "one clear objective" line.
- Caption: "One focus beats five vague ones. #SimRacingMyths #TrackDeltaAI"
- CTA: "Get your one objective — link in bio."

**SF-56 — "Myth: telemetry is only for pros"** (Education/Myth, 20s)
- Hook: "You don't need to be fast to benefit from telemetry. You need it more if you're not."
- Script: Explain telemetry helps identify *why* you're not fast yet, which matters more the further you are from your potential.
- Caption: "The slower you are, the more telemetry has to tell you. #SimRacingMyths"
- CTA: "Link in bio."

**SF-57 — "Myth: a fast qualifying lap means you're race-ready"** (Education/Myth, 25s)
- Hook: "One hot lap doesn't predict how you'll do for 20 race laps."
- Script: Contrast single-lap quali conditions (light fuel, fresh tires, no traffic) with race conditions.
- Caption: "Two different skills. Train both. #SimRacingMyths #TrackDeltaAI"
- CTA: "Link in bio."

**SF-58 — "Myth: the AI is just guessing based on 'vibes'"** (Trust/Myth, 25s)
- Hook: "People assume the AI part just makes stuff up. Here's what actually happens before it writes a word."
- Script: Quick recap of the pipeline — parser, feature extraction, DNA engine, coaching engine all run *before* the LLM ever sees anything, and it only sees structured output.
- Caption: "The LLM is the voice. The engineering is the brain. #SimRacingMyths #TrackDeltaAI"
- CTA: "Link in bio."

**SF-59 — "Myth: setup matters more than driving"** (Education/Myth, 25s)
- Hook: "A perfect setup with the same braking mistake is still the same lap time."
- Script: Make the case that driver-side consistency/technique often has more available time than marginal setup tweaks, especially below a certain skill ceiling.
- Caption: "Fix the driver input before you chase the last click of setup. #SimRacingMyths"
- CTA: "Link in bio."

**SF-60 — "Myth: confidence in an app should always be high"** (Trust/Myth, 20s)
- Hook: "An app that's always '100% confident' is lying to you, not helping you."
- Script: Show the confidence tier system and why low-confidence-early is the honest state, not a bug.
- Caption: "High confidence should be earned by data, not defaulted to. #SimRacingMyths #TrackDeltaAI"
- CTA: "Link in bio."

---

## Batch 7 (SF-61–70): Deep Engineering Explainers

**SF-61 — "Why your DNA changes more after a bad session sometimes"** (Education/Tech, 30s)
- Hook: "A rough session can move your Driver DNA more than a clean one. Here's why."
- Script: Explain EWMA weighting (recent sessions influence more, alpha=0.3 in plain terms: "recent data always counts extra, but the model never forgets your history entirely").
- Caption: "Your DNA weighs recent data more, without discarding your history. #TrackDeltaAI #HowItWorks"
- CTA: "Link in bio."

**SF-62 — "What actually happens in the 90 seconds after you upload"** (Tech/Product, 35s)
- Hook: "90 seconds. Five real processing stages. Here's each one."
- Script: Parse → extract features → update DNA → coaching engine → Delta's voice, one visual beat per stage with the actual UI stepper shown.
- Caption: "Not a black box. Five real stages, in order. #TrackDeltaAI #HowItWorks"
- CTA: "Link in bio."

**SF-63 — "Why corner-level detail needs track data first"** (Tech/Education, 25s)
- Hook: "Why can't it just tell me about every corner immediately on any track?"
- Script: Explain corner boundaries (entry/apex/exit) need to be mapped per track first; without it, session-level analysis still works, corner-level waits.
- Caption: "Honest degradation beats fake precision. #TrackDeltaAI #HowItWorks"
- CTA: "Link in bio."

**SF-64 — "The difference between a 'session' feature and a 'DNA' feature"** (Tech/Education, 25s)
- Hook: "Two totally different things get calculated from the same lap. Here's the difference."
- Script: Session features = what happened *this* time; DNA = the long-term pattern across all sessions merged together.
- Caption: "One lap tells a story. Many laps reveal a pattern. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-65 — "How incident rate becomes a risk profile"** (Tech/Education, 25s)
- Hook: "One number turns into a whole risk classification. Here's the math, simplified."
- Script: incidents per 10 laps → conservative/moderate/aggressive/erratic buckets, explained with rough thresholds.
- Caption: "Risk profile isn't a vibe check, it's a formula. #TrackDeltaAI #HowItWorks"
- CTA: "Link in bio."

**SF-66 — "Why lap time alone doesn't measure consistency"** (Tech/Education, 25s)
- Hook: "Two drivers, same average lap time, completely different consistency scores. Here's why that matters."
- Script: Explain coefficient of variation (spread relative to average) vs. raw average, with a simple visual of tight vs. scattered lap times.
- Caption: "Average lap time hides the real story. Spread tells it. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-67 — "What 'hot lap percentage' actually counts"** (Tech/Education, 20s)
- Hook: "Here's the stat behind 'how many of your laps are actually good.'"
- Script: Define hot-lap percentage as laps within X% of your session best, tie to consistency score.
- Caption: "Not every lap counts the same toward this score. #TrackDeltaAI #HowItWorks"
- CTA: "Link in bio."

**SF-68 — "Why raw telemetry never reaches the AI"** (Tech/Trust, 30s)
- Hook: "The AI literally never sees your raw lap data. Here's what it sees instead."
- Script: Show the structured coaching JSON (opportunities, strengths, DNA summary) that's actually passed to the LLM, contrasted with raw telemetry it never touches.
- Caption: "Structured facts in, honest narration out. That's the whole job of the AI layer. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-69 — "How a debrief decides what NOT to tell you"** (Tech/Education, 25s)
- Hook: "Just as important as what's in your debrief is what's deliberately left out."
- Script: Explain minimum confidence/minimum time-loss thresholds that filter out noise from the opportunities list.
- Caption: "A short, focused debrief beats a long, noisy one. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-70 — "Why the practice plan has a success metric attached"** (Tech/Product, 25s)
- Hook: "Every drill comes with a way to know if it worked. Here's why that matters."
- Script: Show a practice plan item with its success metric, explain that a drill without a measurable target isn't really actionable.
- Caption: "A drill with no way to check it worked isn't a real drill. #TrackDeltaAI"
- CTA: "Link in bio."

---

## Batch 8 (SF-71–80): Track & Car-Class Specific

**SF-71 — "The corner sequence that separates good from great at [Track]"** (Education, 30s)
- Hook: "This esses section is where the real lap time separation happens."
- Script: Walk a specific multi-corner sequence, explain the entry-speed sacrifice for exit-speed payoff logic.
- Caption: "One corner's line depends on the next. #TrackDeltaAI #iRacing"
- CTA: "Link in bio."

**SF-72 — "GT3 braking vs. open-wheel braking, the real difference"** (Education, 30s)
- Hook: "Braking a GT3 car and braking an open-wheel car are not the same skill."
- Script: Contrast trail-braking tolerance, brake bias behavior, and ABS availability differences between classes.
- Caption: "Same principles, different execution per car class. #SimRacingEducation"
- CTA: "Link in bio."

**SF-73 — "Why oval racing consistency is a different beast"** (Education, 25s)
- Hook: "Oval consistency isn't about one perfect lap. It's about hundreds of identical ones."
- Script: Explain how oval racing rewards a different, tighter consistency band than road racing.
- Caption: "Ovals punish inconsistency harder than road courses. #SimRacingEducation #iRacing"
- CTA: "Link in bio."

**SF-74 — "The chicane everyone takes wrong"** (Education, 25s)
- Hook: "This chicane looks simple. Almost nobody takes the fast way through it."
- Script: Show the common (slower) line vs. the less-obvious faster line, tied to data not opinion.
- Caption: "Not every 'obvious' line is the fast one. #SimRacingEducation #TrackDeltaAI"
- CTA: "Link in bio."

**SF-75 — "Low-downforce vs high-downforce car braking differences"** (Education, 30s)
- Hook: "The same brake point in two different cars can mean two totally different outcomes."
- Script: Explain aero load effects on braking distance and trail-braking window differences between low and high downforce cars.
- Caption: "Your braking technique has to adapt to the car, not the other way around. #SimRacingEducation"
- CTA: "Link in bio."

**SF-76 — "Why endurance racing rewards a different DNA"** (Education, 25s)
- Hook: "The driver who wins a sprint race often isn't built for a 2-hour stint."
- Script: Tie consistency score and pressure-performance attribute to what endurance racing specifically rewards over raw one-lap pace.
- Caption: "Different race formats reward different DNA. #SimRacingEducation #TrackDeltaAI"
- CTA: "Link in bio."

**SF-77 — "The most common mistake at a fast, low-grip corner"** (Education, 25s)
- Hook: "This corner catches almost everyone the same way."
- Script: Walk a specific corner's common failure mode (e.g. trail-braking too deep on cold tires) with data-backed explanation.
- Caption: "The same mistake, session after session, until someone points it out. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-78 — "Rain/wet setup driving technique differences"** (Education, 25s)
- Hook: "Wet-weather driving isn't just 'be more careful.' It's a different technique entirely."
- Script: Explain reduced trail-braking tolerance, smoother throttle application requirements, and adjusted racing line (avoiding rubber-off-line grip loss).
- Caption: "Wet driving rewards smoothness even more than dry. #SimRacingEducation"
- CTA: "Link in bio."

**SF-79 — "Why the last sector often decides the lap"** (Education, 20s)
- Hook: "The final sector is where fatigue-driven mistakes actually show up in the data."
- Script: Show sector time variance increasing toward the end of a stint as a fatigue/focus signal.
- Caption: "Watch your last sector times. They tell on you. #TrackDeltaAI #SimRacingEducation"
- CTA: "Link in bio."

**SF-80 — "Track limits: what actually costs you time vs. what's just a rules risk"** (Education, 25s)
- Hook: "Running wide costs you time even when it doesn't cost you a penalty."
- Script: Explain how track-limit exploitation without penalty still often signals an inefficient line, tie to speed_ratio/reference metrics.
- Caption: "Even 'free' track limits usually aren't actually free. #SimRacingEducation #TrackDeltaAI"
- CTA: "Link in bio."

---

## Batch 9 (SF-81–90): Reaction / Duet / UGC Prompts

**SF-81 — "Reacting to a viral 'perfect lap' clip"** (Reaction, 30s)
- Hook: "Everyone's calling this lap perfect. Let's actually check."
- Script: React to a popular onboard clip (with attribution/permission per platform rules), point out one real technical detail the data lens would flag either way.
- Caption: "Perfect-looking and perfect-measured aren't always the same thing. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-82 — "Stitch this: post your Driver DNA radar shape"** (UGC Challenge, 15s)
- Hook: "Post your Driver DNA radar shape and stitch this."
- Script: Show your own radar shape, briefly react to what it says about you, invite others to do the same.
- Caption: "What does your radar shape say about you? Stitch/duet this. #TrackDeltaAI #DriverDNA"
- CTA: "Tag us in yours."

**SF-83 — "Duet this: what's your brake point pattern?"** (UGC Challenge, 20s)
- Hook: "Duet this with your own brake-point consistency screenshot."
- Script: Show your own stat, brief honest reaction, invite duets.
- Caption: "Show me yours. #TrackDeltaAI #DriverDNA"
- CTA: "Duet with your own data."

**SF-84 — "Reacting to a driver's honest debrief request"** (Reaction/Community, 30s)
- Hook: "A driver asked me to roast their session. Let's see."
- Script: Live-react to a submitted real session (with permission), keep it genuinely evidence-based, not mean-spirited — the brand never mocks, it coaches.
- Caption: "Not a roast. A real debrief, on camera. #TrackDeltaAI"
- CTA: "Submit your own — link in bio."

**SF-85 — "Answering the top comment from last video"** (Reaction/Community, 20s)
- Hook: "The top comment from last video asked this. Here's the real answer."
- Script: Read the actual comment, answer specifically and honestly, credit the commenter.
- Caption: "Your comments become the next video. #TrackDeltaAI"
- CTA: "Ask something in the comments."

**SF-86 — "Rating sim racing setups sent in by followers"** (UGC/Community, 30s)
- Hook: "Rating rig setups you sent in. Some of these are wild."
- Script: React genuinely to a few submitted rig photos, tie back lightly to "the data matters more than the rig, but this is fun anyway."
- Caption: "Send your rig — some of you are unhinged (affectionately). #SimRacing #TrackDeltaAI"
- CTA: "Submit your setup — link in bio."

**SF-87 — "Guessing a driver's DNA before revealing it"** (Reaction/Game format, 25s)
- Hook: "Watch this onboard for 10 seconds. I'll guess their Driver DNA before I show you the real one."
- Script: Predict style from onboard footage alone, then reveal the actual DNA data, compare.
- Caption: "Can you tell someone's driving style just from onboard? Let's test it. #TrackDeltaAI"
- CTA: "Guess in the comments before the reveal."

**SF-88 — "Community challenge: most improved DNA this month"** (UGC Challenge, 20s, recurring)
- Hook: "This driver's consistency score moved the most this month. Here's their story."
- Script: Spotlight a real user's improvement arc (with permission), invite others to submit their own progress.
- Caption: "Most-improved spotlight. Could be you next month. #TrackDeltaAI"
- CTA: "Tag us in your progress."

**SF-89 — "Reacting to sim racing Twitter/X hot takes"** (Reaction/Culture, 25s)
- Hook: "A hot take about telemetry tools is going around. Let's look at it honestly."
- Script: Engage a genuine debate/opinion in the space fairly, agree where it's fair, push back with data where it isn't.
- Caption: "Engaging honestly, even when it's not flattering. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-90 — "Submit your worst corner, I'll tell you what's probably happening"** (Community/UGC, 25s)
- Hook: "Tell me your worst corner in the comments. I'll guess what's going wrong before you upload anything."
- Script: Take a few real comments, give genuinely useful general diagnostic possibilities (without real data, framed honestly as "possible causes," not a diagnosis).
- Caption: "General patterns first. Your real data gives the specific answer. #TrackDeltaAI"
- CTA: "Comment your worst corner."

---

## Batch 10 (SF-91–100): "Ask Delta" Q&A + Founder Q&A

**SF-91 — "Ask Delta: why do I keep locking up at the same corner?"** (Q&A/Education, 25s)
- Hook: "A driver asked Delta this exact question. Here's the kind of answer it gives."
- Script: Walk through the general diagnostic logic (brake pressure trace + entry speed) Delta would actually apply, framed as illustrative since no specific data is shown.
- Caption: "This is the reasoning behind a real debrief line. #TrackDeltaAI #AskDelta"
- CTA: "Ask your own — link in bio."

**SF-92 — "Ask Delta: how many sessions until you actually know me?"** (Q&A/Trust, 20s)
- Hook: "How many sessions before Delta actually knows how I drive?"
- Script: Walk the confidence tier table honestly — very low at 1, low at 2-4, moderate at 5-10, etc.
- Caption: "Straight answer, no marketing spin. #TrackDeltaAI #AskDelta"
- CTA: "Link in bio."

**SF-93 — "Ask Delta: what if I only race one track?"** (Q&A/Product, 20s)
- Hook: "What happens if I only ever race one track — does the DNA still work?"
- Script: Explain track_profiles per-track overrides alongside the overall DNA, so single-track drivers still get a real, deepening model.
- Caption: "Works for specialists too, not just multi-track drivers. #TrackDeltaAI #AskDelta"
- CTA: "Link in bio."

**SF-94 — "Founder Q&A: why $29 and not $9.99?"** (Q&A/Building in Public, 25s)
- Hook: "Someone asked why Pro isn't $9.99 like every other app. Real answer."
- Script: Honest reasoning about sustainable pricing for a small team, per-session compute/LLM costs, and positioning relative to coaching alternatives (a real coach costs far more per hour).
- Caption: "Pricing, explained honestly, not defensively. #TrackDeltaAI #BuildInPublic"
- CTA: "Link in bio."

**SF-95 — "Founder Q&A: are you actually a fast driver yourself?"** (Q&A/Building in Public, 20s)
- Hook: "Am I actually fast? Honest answer."
- Script: Give a genuinely honest self-assessment — this product doesn't require the founder to be the fastest driver, it requires understanding what fast drivers and improving drivers both need.
- Caption: "You don't have to be the fastest to build the tool that helps you get faster. #BuildInPublic"
- CTA: "Link in bio."

**SF-96 — "Ask Delta: what if my session has almost no clean laps?"** (Q&A/Product, 25s)
- Hook: "What happens if most of my laps were messy? Does the debrief just... fail?"
- Script: Explain graceful handling of low-clean-lap sessions — reduced confidence, honest framing, still generates what it can.
- Caption: "No silent failures. Just an honest, smaller debrief. #TrackDeltaAI #AskDelta"
- CTA: "Link in bio."

**SF-97 — "Founder Q&A: what happens to my data if I cancel?"** (Q&A/Trust, 20s)
- Hook: "If I cancel Pro, do I lose my Driver DNA?"
- Script: Explain downgrade limits access, doesn't delete data; separately address what actual account deletion does.
- Caption: "Canceling isn't the same as deleting. Here's the real distinction. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-98 — "Ask Delta: can you tell me I'm wrong about my own driving?"** (Q&A/Trust, 25s)
- Hook: "Can Delta actually disagree with how I think I drive?"
- Script: Yes — that's the whole point; feel and data diverge often, and the debrief is built to reflect the data honestly, even when it contradicts self-perception.
- Caption: "It's not here to agree with you. It's here to be accurate. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-99 — "Founder Q&A: what's the actual North Star metric?"** (Q&A/Building in Public, 25s)
- Hook: "What number actually matters to this business? Not views, not sign-ups."
- Script: Explain the real North Star — percentage of drivers measurably faster after 4+ sessions — and why that discipline shapes every roadmap decision.
- Caption: "If this number doesn't move, nothing else matters. #TrackDeltaAI #BuildInPublic"
- CTA: "Link in bio."

**SF-100 — "Ask Delta: will you ever do real-time in-race coaching?"** (Q&A/Roadmap, 20s)
- Hook: "Will Delta ever talk to me live, mid-race?"
- Script: Honest roadmap answer — sequenced, not rejected; debrief-quality had to come first; real-time is a genuinely different architecture.
- Caption: "Roadmap honesty over hype. #TrackDeltaAI #AskDelta"
- CTA: "Link in bio."

---

## Batch 11 (SF-101–110): Data Storytelling

**SF-101 — "The lap that changed how I thought about this corner"** (Storytelling, 30s)
- Hook: "One single lap made this driver rethink an entire corner."
- Script: Narrate a specific (real or illustrative, labeled) lap where a driver tried a suggested change and felt the difference, tie to the actual data delta.
- Caption: "Sometimes one lap is all it takes to feel it click. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-102 — "From Very Low confidence to Very High — one driver's arc"** (Storytelling, 35s)
- Hook: "Watch this driver's confidence go from 'barely enough data' to 'well-established profile.'"
- Script: Sequential DNA snapshots across many sessions, confidence label visibly climbing.
- Caption: "This is what patience with the process actually looks like. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-103 — "The session where the practice plan actually worked"** (Storytelling, 30s)
- Hook: "Delta gave this driver one drill. Next session, here's what happened."
- Script: Show the practice plan item, then the next session's data showing measurable change in that exact metric.
- Caption: "One drill, one measurable result. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-104 — "A driver who disagreed with the debrief — and was wrong"** (Storytelling/Trust, 30s)
- Hook: "This driver didn't believe the debrief at first. Then they checked the replay."
- Script: Narrate genuine skepticism turning into agreement once cross-checked against onboard footage.
- Caption: "Data doesn't need you to believe it right away. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-105 — "A driver who disagreed with the debrief — and Delta updated"** (Storytelling/Trust, 30s)
- Hook: "This time, the driver was right, and the data needed one more session to catch up."
- Script: Honest story about confidence being appropriately low early, and how it should be OK to trust your feel more than a low-confidence read.
- Caption: "Low confidence means 'wait and see,' not 'ignore your feel.' #TrackDeltaAI"
- CTA: "Link in bio."

**SF-106 — "What a whole season of DNA snapshots looks like"** (Storytelling, 35s)
- Hook: "A whole season, compressed into one scrolling view of DNA snapshots."
- Script: Fast-scroll through many sequential DNA states, calling out the biggest single shift.
- Caption: "A season of small changes adds up to one big one. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-107 — "The corner nobody flagged until session 6"** (Storytelling, 25s)
- Hook: "This corner didn't show up as a problem until enough data existed to prove it."
- Script: Explain how a subtle, recurring issue only crosses the confidence/significance threshold after enough sessions.
- Caption: "Some patterns need enough laps to become undeniable. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-108 — "One note, one session, one real change"** (Storytelling, 25s)
- Hook: "A driver typed one sentence into the session note. It changed the whole debrief."
- Script: Show the note ("felt like I was overdriving entry") and how the debrief incorporated that context specifically.
- Caption: "Context you give it actually gets used. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-109 — "Two drivers, same track, same day, totally different DNA"** (Storytelling, 30s)
- Hook: "Same track. Same conditions. Two completely different driving fingerprints."
- Script: Side-by-side radar shapes for two different (illustrative) drivers, highlighting how personalized the model is.
- Caption: "No two Driver DNAs look the same. That's the whole point. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-110 — "The improvement that didn't show up in lap time yet"** (Storytelling/Trust, 25s)
- Hook: "This driver got measurably more consistent before their lap time actually dropped."
- Script: Show consistency score improving ahead of best-lap time improving, explain that's the expected, honest order of things.
- Caption: "Consistency usually improves before peak pace does. #TrackDeltaAI"
- CTA: "Link in bio."

---

## Batch 12 (SF-111–120): Honest Competitive Positioning

**SF-111 — "TrackDelta vs. a raw telemetry viewer"** (Positioning, 30s)
- Hook: "Same telemetry file. Two completely different experiences."
- Script: Side-by-side: raw MoTeC-style viewer (you have to interpret it yourself) vs. TrackDelta debrief (interpreted for you). No disparagement — just a fair, honest contrast of what each does.
- Caption: "Both read the same file. Only one tells you what it means. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-112 — "TrackDelta vs. a human coach — honestly"** (Positioning, 30s)
- Hook: "Is this a replacement for a real coach? Honest answer: sort of, not entirely."
- Script: Be candid — a human coach can watch race-craft/wheel-to-wheel nuance that pure telemetry can't fully capture yet; TrackDelta is consistent, always available, and far cheaper per session.
- Caption: "Not pretending to replace everything a great coach does. Just far more accessible. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-113 — "Why we don't do leaderboards or peer comparison"** (Positioning, 25s)
- Hook: "A lot of tools compare you to other drivers. We deliberately don't. Here's why."
- Script: Explain the philosophy — coaching based on *your own* improvement arc, not comparison-driven pressure; note it's a real, deliberate exclusion, not an oversight.
- Caption: "Compared to your past self, not a stranger's best lap. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-114 — "What generic AI chat tools miss that TrackDelta doesn't"** (Positioning, 30s)
- Hook: "You could paste your lap times into a generic AI chatbot. Here's what it can't do that this can."
- Script: Explain that a generic LLM has no access to your actual telemetry, no persistent evolving model of you, no engineered feature-extraction layer — it would have to guess.
- Caption: "A chatbot can't parse your .ibt file. This is built to. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-115 — "Why we're iRacing-only for now"** (Positioning/Roadmap, 20s)
- Hook: "Why not support every sim at once? Real answer: focus."
- Script: Explain that supporting multiple telemetry formats (e.g. ACC's `.ld`) doubles pipeline complexity; validating deeply on one sim first was the deliberate choice.
- Caption: "One sim, done right, before spreading thin. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-116 — "What a free tool can't sustain, and why that matters to you"** (Positioning, 25s)
- Hook: "Why isn't this entirely free forever? Genuine answer."
- Script: Explain the real infrastructure/LLM cost per debrief, and that a sustainable business is what keeps a tool like this maintained and improving instead of abandoned.
- Caption: "Free forever tools usually die. Sustainable ones don't. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-117 — "The honest limitations of the current product"** (Positioning/Trust, 30s)
- Hook: "Here's what TrackDelta genuinely can't do yet."
- Script: List real, current limitations honestly (e.g. no real-time coaching, limited track library still growing, no video analysis yet).
- Caption: "Confidence in what it does well starts with honesty about what it doesn't do yet. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-118 — "Why 'personalized' isn't just a marketing word here"** (Positioning, 25s)
- Hook: "Every coaching app says 'personalized.' Here's what that word has to actually mean to count."
- Script: Contrast generic ideal-lap-comparison coaching vs. Driver DNA's this-specific-driver baseline approach.
- Caption: "Personalized should mean built from your data, not just addressed to your name. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-119 — "What happens when the free tier limit is hit, exactly"** (Positioning/Trust, 20s)
- Hook: "Hit your free session limit? Here's exactly what happens — no dark patterns."
- Script: Show the real upload-blocked message and upgrade CTA, note it resets monthly, no forced downgrade of existing data.
- Caption: "A clear message, not a trick. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-120 — "Why we'll say 'this data doesn't support that' on camera"** (Positioning/Trust, 25s)
- Hook: "We'll tell you when the answer is 'no, the data doesn't back that up' — even about our own feature ideas."
- Script: Give a genuine example of an internal idea that got shelved because early data/feedback didn't support it.
- Caption: "Truth over confidence applies to us building this too. #TrackDeltaAI #BuildInPublic"
- CTA: "Link in bio."

---

## Batch 13 (SF-121–130): Fast Numbers & Formulas

**SF-121 — "60Hz, explained in one breath"** (Tech, 15s)
- Hook: "60 times a second. Here's what that actually buys you."
- Script: Explain 60Hz sampling means a data point roughly every 0.0167s — enough resolution to catch a brake stab a human eye would miss on a replay.
- Caption: "Resolution most drivers never think about. #TrackDeltaAI #HowItWorks"
- CTA: "Link in bio."

**SF-122 — "115% — the number that decides a 'clean lap'"** (Tech, 20s)
- Hook: "One threshold decides whether your lap counts as clean or gets thrown out."
- Script: Explain the 115%-of-best-candidate-lap tolerance rule for clean-lap filtering, and why outlier laps get excluded from analysis.
- Caption: "Not every lap should count the same. #TrackDeltaAI #HowItWorks"
- CTA: "Link in bio."

**SF-123 — "Why the first and last lap never count"** (Tech, 15s)
- Hook: "Your out-lap and in-lap never count toward your clean laps. Here's why that's correct."
- Script: Explain out-laps/in-laps are structurally different (cold tires, pitting in) and would skew the analysis if included.
- Caption: "Excluded on purpose, not by accident. #TrackDeltaAI #HowItWorks"
- CTA: "Link in bio."

**SF-124 — "0.3 — the number that controls how fast your DNA updates"** (Tech, 20s)
- Hook: "One number decides how much a single session can move your whole profile."
- Script: Explain the EWMA alpha value in plain terms — a middle-ground weighting so recent sessions matter without erasing history.
- Caption: "Not too reactive, not too stubborn. #TrackDeltaAI #HowItWorks"
- CTA: "Link in bio."

**SF-125 — "2 seconds — the telemetry gap threshold"** (Tech, 15s)
- Hook: "A 2-second gap in your data can throw out an entire lap. Here's why."
- Script: Explain telemetry gaps (disconnects, replay skips) longer than 2 seconds disqualify a lap from clean-lap analysis to avoid corrupted stats.
- Caption: "Data integrity checks you never see, working in the background. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-126 — "20 sessions — what 'well-established profile' actually requires"** (Tech, 20s)
- Hook: "Twenty sessions. That's roughly what it takes to reach a fully mature Driver DNA."
- Script: Walk the confidence tier table's higher end, explain why depth takes real time, on purpose.
- Caption: "Depth isn't instant, and it shouldn't be. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-127 — "Why 5 milliseconds is the minimum time-loss threshold"** (Tech, 20s)
- Hook: "An opportunity has to be worth at least this much time to even make your debrief."
- Script: Explain the minimum-time-loss filter that keeps trivial, noise-level findings out of the coaching output.
- Caption: "Not every fluctuation deserves your attention. #TrackDeltaAI #HowItWorks"
- CTA: "Link in bio."

**SF-128 — "Why the top 3 opportunities, not top 10"** (Tech/Product, 20s)
- Hook: "Why only three opportunities per debrief, when there could be more?"
- Script: Explain deliberate ranking + cap by estimated impact, tying to the "one clear objective" focus philosophy.
- Caption: "More isn't more useful. Focus is. #TrackDeltaAI"
- CTA: "Link in bio."

**SF-129 — "Why time-available estimates get discounted by confidence"** (Tech, 25s)
- Hook: "A 'moderate confidence' estimate isn't shown at full strength. Here's the actual adjustment."
- Script: Explain the confidence-based discounting applied to estimated time-available ranges (e.g., moderate confidence multiplies the estimate down).
- Caption: "Honest math, not an optimistic guess. #TrackDeltaAI #HowItWorks"
- CTA: "Link in bio."

**SF-130 — "20 messages — the Delta Conversations limit, explained"** (Tech/Product, 20s)
- Hook: "Why does a conversation with Delta cap out at 20 messages?"
- Script: Explain the limit exists to keep conversations focused on the session at hand rather than open-ended chat, and ties to sustainable cost per user.
- Caption: "A focused conversation, not an infinite chatbot. #TrackDeltaAI"
- CTA: "Link in bio."

---

## Batch 14 (SF-131–140): Multi-Part Cliffhanger Series

**SF-131 — "Part 1: The corner I've been getting wrong for months"** (Series, 25s)
- Hook: "I've been losing time in this exact corner for months and didn't know it. Part 1."
- Script: Set up the mystery — show the corner, the feeling of "this should be fine," end on a cliffhanger before the data reveal.
- Caption: "Part 1 of 3. The data reveal is next. #TrackDeltaAI"
- CTA: "Follow so you don't miss Part 2."

**SF-132 — "Part 2: what the data actually showed"** (Series, 25s)
- Hook: "Part 2. Here's what the debrief actually found."
- Script: Reveal the actual opportunity card and specific finding from Part 1's corner.
- Caption: "Part 2 of 3. #TrackDeltaAI"
- CTA: "Part 3 — the fix — coming next."

**SF-133 — "Part 3: did the fix actually work?"** (Series, 25s)
- Hook: "Part 3. I tried the fix. Here's the next session's data."
- Script: Show the follow-up session's data, honest result whether it worked fully, partially, or not yet.
- Caption: "The honest follow-up, not just the highlight. #TrackDeltaAI"
- CTA: "Link in bio to try your own arc."

**SF-134 — "Part 1: building the confidence system (why it's harder than it sounds)"** (Series/Building in Public, 30s)
- Hook: "Building an honest confidence system is way harder than building a hype-everything one. Part 1."
- Script: Set up the design challenge — how do you quantify "how sure are we" without it being arbitrary.
- Caption: "Part 1 of 2. #TrackDeltaAI #BuildInPublic"
- CTA: "Follow for Part 2."

**SF-135 — "Part 2: how confidence scoring actually works"** (Series/Building in Public, 30s)
- Hook: "Part 2. Here's the actual system that shipped."
- Script: Walk the real confidence tier system, tie back to Part 1's design challenge.
- Caption: "Part 2 of 2. #TrackDeltaAI #BuildInPublic"
- CTA: "Link in bio."

**SF-136 — "Part 1: a driver's first session, unedited"** (Series/Case Study, 25s)
- Hook: "Following one driver's real journey, starting today. Session 1."
- Script: Show the very first debrief for a real (permissioned) driver, low confidence and all.
- Caption: "Following this arc for real. Part 1. #TrackDeltaAI"
- CTA: "Follow to see where this goes."

**SF-137 — "Part 2: session 5, has anything actually changed?"** (Series/Case Study, 25s)
- Hook: "Same driver, 5 sessions later. Honest check-in."
- Script: Compare session 1 vs session 5 DNA, honestly — whether it's a clean improvement story or a mixed one.
- Caption: "The honest middle of the story, not just the ending. #TrackDeltaAI"
- CTA: "Follow for the next check-in."

**SF-138 — "Part 3: session 10, the real result"** (Series/Case Study, 30s)
- Hook: "10 sessions in. Here's the real before-and-after."
- Script: Full before/after comparison, real lap time delta if there is one, honest framing either way.
- Caption: "The real ending, not a cherry-picked one. #TrackDeltaAI"
- CTA: "Start your own arc — link in bio."

**SF-139 — "Part 1: why we almost built this feature wrong"** (Series/Building in Public, 25s)
- Hook: "We almost shipped a version of this feature that would've undermined the whole point. Part 1."
- Script: Set up a real internal design debate (e.g., an early idea that risked overstating confidence for engagement).
- Caption: "Part 1 of 2 — the almost-mistake. #TrackDeltaAI #BuildInPublic"
- CTA: "Follow for Part 2."

**SF-140 — "Part 2: what we shipped instead, and why"** (Series/Building in Public, 25s)
- Hook: "Part 2. Here's what actually shipped, and why it's different."
- Script: Reveal the actual shipped approach and the principle that steered the correction.
- Caption: "Part 2 of 2 — the fix before it ever reached anyone. #TrackDeltaAI"
- CTA: "Link in bio."

---

## Batch 15 (SF-141–150): Culture & Community Challenges

**SF-141 — "Every sim racer's group chat after a league race"** (Culture, 15s)
- Hook: "The group chat after every single league race, without fail."
- Script: Relatable, exaggerated-but-true montage of post-race chat energy (blaming setup, blaming traffic, one person quietly went a second faster than everyone).
- Caption: "Tag the person in your group who's always 'just gonna check the data real quick.' #SimRacing #TrackDeltaAI"
- CTA: "Follow for more."

**SF-142 — "POV: your teammate says 'just drive it, stop overthinking'"** (Culture, 15s)
- Hook: "POV: 'just drive it, stop overthinking it' — as someone who overthinks it, correctly."
- Script: Light, relatable bit contrasting feel-only advice with a quick cut to a specific, data-backed correction.
- Caption: "Overthinking it correctly is still correct. #SimRacing #TrackDeltaAI"
- CTA: "Follow for more."

**SF-143 — "The five stages of watching your own onboard back"** (Culture, 20s)
- Hook: "The five stages of grief, but it's watching your own onboard footage."
- Script: Quick comedic beats: denial ("that wasn't that bad"), anger, bargaining ("the car was different"), acceptance, actually fixing it.
- Caption: "We've all been through all five. #SimRacing #TrackDeltaAI"
- CTA: "Follow for more."

**SF-144 — "Challenge: guess your own consistency score before checking"** (UGC Challenge, 20s)
- Hook: "Guess your own consistency score before you check it. I'll bet you're wrong."
- Script: Founder guesses their own, reveals the real number, invites others to try and post their guess-vs-reality.
- Caption: "Bet you're wrong about your own number too. #TrackDeltaAI"
- CTA: "Post your guess vs. reality, tag us."

**SF-145 — "Things that sound fast but aren't, and vice versa"** (Culture/Education, 20s)
- Hook: "Things that feel fast but measure slow — and the reverse."
- Script: Quick contrast pairs: aggressive-feeling but slower entry vs. smooth-feeling but actually faster technique.
- Caption: "Feel and fast don't always agree. #SimRacingEducation #TrackDeltaAI"
- CTA: "Follow for more."

**SF-146 — "The universal sim racer excuse generator"** (Culture, 15s)
- Hook: "Pick your excuse: the wheel, the FFB settings, the internet, or actually you."
- Script: Comedic rapid list of classic excuses, punchline cutting to real data showing the actual (driver-side) pattern.
- Caption: "Sometimes it really is the FFB settings. Usually it's not. #SimRacing #TrackDeltaAI"
- CTA: "Follow for more."

**SF-147 — "Community challenge: most honest debrief reaction"** (UGC Challenge, 25s)
- Hook: "Post your most honest, unfiltered reaction to your own debrief."
- Script: Show a genuine (mildly humbling) reaction as the example, invite others to share theirs.
- Caption: "The realest reactions are the best ones. Tag us. #TrackDeltaAI"
- CTA: "Post yours, tag us."

**SF-148 — "What your car choice says about your driving style (playfully)"** (Culture, 20s)
- Hook: "What your favorite car class says about your Driver DNA (playfully, not scientifically)."
- Script: Light, fun generalizations by class (oval vs. road vs. open-wheel driver stereotypes), self-aware that it's for fun, not a real claim.
- Caption: "Purely for fun — the real answer is in your actual DNA. #SimRacing #TrackDeltaAI"
- CTA: "Comment your main class."

**SF-149 — "Rating iconic onboard reactions to bad laps"** (Culture, 20s)
- Hook: "Ranking the most iconic 'that was rough' onboard reactions."
- Script: Light compilation-style reactions to visible driver frustration moments (with permission/fair use awareness), self-aware and affectionate tone.
- Caption: "We've all made this exact sound. #SimRacing"
- CTA: "Follow for more."

**SF-150 — "The sim racing new year's resolution that never survives January"** (Culture, 20s)
- Hook: "'This year I'm going to actually review my telemetry after every session.' Sure you are."
- Script: Playful callout of the common resolution that quietly dies, pivot to "here's the tool that makes it actually happen automatically."
- Caption: "The resolution that actually sticks because it takes 2 minutes. #TrackDeltaAI"
- CTA: "Make it stick this time — link in bio."

---

## Notes on Using This Batch

- Batches 6–8 (myth-busting, tech explainers, track/car-specific) are the strongest SEO/discovery plays in this set — prioritize them when a week needs a video likely to be found by non-followers searching a specific term.
- Batches 9–10 (reaction/UGC, Ask Delta) require real community interaction to source — don't fabricate a "submitted question" or "viral clip reaction"; wait until there's real material, or these formats will read as hollow.
- Batch 14 (multi-part series) needs the parts actually scheduled close together (2-4 days apart max) or the cliffhanger loses its pull — don't start a "Part 1" without Part 2 already scripted and ready.
