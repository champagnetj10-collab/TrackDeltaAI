# AI Prompts: Turning Real Driver DNA Reports Into Video Content

Ready-to-use prompts for an LLM (Claude, GPT, etc.) to turn a real debrief/Driver DNA report into scripts, captions, and visual-generation briefs. **Privacy rule, non-negotiable:** never run a real user's debrief through any of these prompts without their explicit permission, matching the same standard the product itself holds (file 01 §6, "Data disclosure rule"). Always ask before creating content from someone's real session, and always label real vs. illustrative data on screen per the brand guide.

---

## 1. Prompt: Debrief → Short-Form Script

Use this when you have a real (permissioned) debrief JSON/text and want a SF-##-style script out of it.

```
You are writing a short-form video script (15-45 seconds) for TrackDelta AI's social channels, following the brand voice guide's rules exactly:
- Calm, specific, evidence-based tone. Never hype, never vague, never falsely precise.
- Structure: Hook (first 2 seconds) → Problem → Reveal → Payoff → CTA, matching the 5-scene storyboard.
- The hook must be a single punchy line that could stand alone.
- Use only what's actually in the debrief below — do not invent any detail, number, or corner name not present in the source data.
- If the source data includes a confidence label, respect it in the script's framing (do not state a low-confidence finding as if it were certain).

Here is the real debrief content (permission has been obtained to use this driver's data):
[PASTE DEBRIEF JSON / TEXT HERE]

Output format:
HOOK: [one line]
SCRIPT: [3-5 numbered beats]
CAPTION: [one paragraph, include 2-3 relevant hashtags from the approved list]
CTA: [one line, pulled from the standard CTA bank if it fits, or a natural variant]
```

---

## 2. Prompt: Driver DNA Radar → Visual Generation Brief

Use this to generate a brief for a designer/motion-graphics tool (or an AI image/video generation tool) to visualize a specific real DNA snapshot.

```
Generate a visual design brief for animating a Driver DNA radar chart, based on this real data:
[PASTE DNA JSON: braking/throttle/steering/consistency/risk values and confidence scores]

Requirements:
- Match TrackDelta AI's exact brand palette: Delta Blue #0D6EFD, Carbon Black #0B0D10, Graphite #111317, Steel #E5E7EB. Apex Orange #FF6800 only if a value needs a warning/contrast callout.
- Radar chart with 5-7 axes matching the attributes in the data provided (do not add axes not present in the source).
- Describe an entrance animation: shape animates in from center outward, breathing glow behind it (per the CapCut template's `glow-pulse` treatment).
- Font: Space Grotesk for all labels.
- Output: a written brief a motion designer (or an AI video tool prompt) could execute directly, not the visual itself.
```

---

## 3. Prompt: Corner-by-Corner Opportunity → "Data Reveal" Video Brief

```
Based on this real opportunity-card data from a TrackDelta debrief:
[PASTE: corner name, category, delta_commentary, data_evidence, estimated_gain_ms, confidence]

Write a "Data Reveal" video brief (Template A style, see file 06) including:
1. The single most important number to display largest on screen (the estimated time gain, formatted to one decimal place in seconds)
2. A one-sentence plain-language explanation of what's happening at this corner, using only the data_evidence provided
3. The confidence label, displayed honestly (do not round up a "Moderate" confidence finding to sound like a certainty)
4. A suggested on-screen chip/callout treatment matching brand colors, with the estimated gain formatted like the app itself does (e.g. "~0.3s")
```

---

## 4. Prompt: Delta's Voice — Debrief Headline → Spoken Voiceover Line

```
Rewrite this debrief headline/session overview as a spoken voiceover line for a video, in Delta's exact character:

Delta is: honest, specific, calm, evidence-based.
Delta is never: enthusiastic filler ("Great session!"), vague, overconfident, or chatbot-like ("As an AI...").

Source text:
[PASTE session_overview OR headline FIELD FROM THE DEBRIEF]

Output: one spoken-voiceover-ready version, under 15 seconds when read aloud at a natural pace, preserving every factual claim exactly as given (no added specifics, no softened or exaggerated confidence).
```

---

## 5. Prompt: Building-in-Public Post → Multi-Platform Variant Set

```
Take this single real update about TrackDelta AI's development:
[PASTE: what happened, honestly, in plain language]

Generate platform-specific variants using the correct template from file 08 and the tone guidance from file 12:
1. X: apply Template 1 (Weekly Ship Log) or Template 3 (Bug/Mistake) format, whichever fits, under 280 characters if a single post, or a short thread if it needs more room
2. LinkedIn: same content, first-person founder voice, slightly more reflective/context-rich, 150-250 words
3. Short-form video script: hook + 3 beats + caption, following the SF-## script format
4. Discord `#building-in-public` post: casual, direct, as if talking to engaged community members who already know context (can be shorter and more informal than the public-facing versions)

Do not add any claim, number, or detail not present in the source update.
```

---

## 6. Guardrails for All AI-Generated Content (apply regardless of which prompt above is used)

- **Always human-review before publishing.** An LLM can still occasionally soften/round a number in a way that overstates confidence, or add a plausible-sounding but unverified detail — the founder/editor is the final check against the brand voice guide's Truth Over Confidence standard, every time.
- **Never let an AI tool invent a driver quote, testimonial, or statistic.** Every prompt above is scoped to transform *real, provided* data — none of them should ever be used to generate a fictional example presented as real.
- **Label AI-assisted content internally if it matters for your own recordkeeping** — no requirement to disclose AI-drafting to the audience (this is normal production tooling, like using a teleprompter), but the content's *claims* must be exactly as true as if written entirely by hand.
- **Re-run the brand voice guide's "Do / Don't" table (file 01 §4) as a final check** on any AI output before it ships — it's the fastest sanity check available.
