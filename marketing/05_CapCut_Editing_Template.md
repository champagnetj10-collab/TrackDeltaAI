# Reusable CapCut Editing Template — Short-Form Videos

One consistent scene structure so every Short/TikTok/Reel feels like the same show, no matter who edits it. Designed to be rebuilt as an actual CapCut **Template** (saved project you duplicate per video) — steps to do that are at the bottom.

---

## 1. Canvas & Project Settings

| Setting | Value |
|---|---|
| Aspect ratio | 9:16 (1080×1920) |
| Frame rate | 30fps (60fps only if source footage is 60fps) |
| Duration target | 15–45s (hard cap 60s) |
| Safe zone | Keep all text inside the center 1080×1500 area — top ~120px and bottom ~300px get covered by platform UI (captions, profile info, buttons) |

---

## 2. The 5-Scene Storyboard (used for every SF-## script in file 03)

```
┌───────────────┬───────────────┬────────────────┬───────────────┬───────────────┐
│   SCENE 1     │   SCENE 2     │    SCENE 3     │   SCENE 4     │   SCENE 5     │
│    HOOK       │   PROBLEM     │    REVEAL      │   PAYOFF      │     CTA       │
│  0:00–0:02    │  0:02–0:06    │  0:06–0:XX     │  varies       │  last 2–3s    │
└───────────────┴───────────────┴────────────────┴───────────────┴───────────────┘
```

### Scene 1 — Hook (0:00–0:02, non-negotiable)
- **Visual:** either a talking-head direct-to-camera line, OR the most visually confusing/striking frame available (raw telemetry graph, before-state).
- **Text overlay:** the hook line, top-third safe zone, appears at frame 1 — do not fade in, cut in hard.
- **Audio:** hook line spoken immediately; trending audio (if used) starts under it at low volume, never over the voice.
- **Rule:** if you can't tell what the video is about within these 2 seconds, rewrite the hook, don't fix it with editing.

### Scene 2 — Problem (0:02–0:06)
- **Visual:** establish what's confusing/frustrating/wrong (the raw graph, the vague advice, the repeated mistake).
- **Text overlay:** one supporting line max, lower-third.
- **Transition in from Scene 1:** hard cut or quick zoom-punch (2–3 frame scale bump), never a slow fade.

### Scene 3 — Reveal (the longest scene, most of the runtime)
- **Visual:** the actual TrackDelta screen recording / data visual / explanation. This is where the specific content from the script lives.
- **Text overlay:** key numbers/labels as animated text call-outs, timed to when they're spoken, not before.
- **On-screen graphics:** must match the app's real visual language — Delta Blue accents, correct color coding (green = time gained, orange/red = time lost). See brand voice guide §6.
- **Pacing:** cut every 2–4 seconds even within this scene — no static shot longer than ~4s without a zoom/pan/text-punch to hold attention.

### Scene 4 — Payoff (varies, 3–8s)
- **Visual:** the "so what" — the result, the number, the recommendation, the reaction.
- **Text overlay:** the single most important stat, largest text size in the video.
- **Audio:** slight pause/beat before this line lands — let it breathe for half a second.

### Scene 5 — CTA (last 2–3 seconds)
- **Visual:** brand watermark corner logo already present throughout (see §4); CTA text takes over the full lower third.
- **Text overlay:** pick one line from the CTA bank (file 03, bottom).
- **Audio:** voiceover CTA line, or on-screen text only if the hook already used the voice budget.

---

## 3. Text Style Presets (save as CapCut text presets, reuse every time)

| Preset name | Font | Size | Color | Use |
|---|---|---|---|---|
| `TD-Hook` | Space Grotesk Bold (or closest CapCut match: "Poppins Bold" / "Montserrat Bold") | 72px | White `#FFFFFF`, Delta Blue `#0D6EFD` stroke/shadow | Scene 1 hook line |
| `TD-Support` | Space Grotesk Medium | 48px | Steel `#E5E7EB` | Scene 2/3 supporting text |
| `TD-Callout` | Space Grotesk Bold | 56px | Delta Blue `#0D6EFD` on dark chip background `#111317` at 85% opacity | Scene 3 data call-outs |
| `TD-Stat` | Space Grotesk Bold | 88px | White, Delta Blue glow/shadow | Scene 4 payoff number |
| `TD-CTA` | Space Grotesk SemiBold | 44px | White on Delta Blue `#0D6EFD` rounded-rect background | Scene 5 CTA |

**Animation defaults:** "Pop" or "Bounce In" for callouts/stats (fast, 0.2s in), simple "Fade" only for supporting text. Avoid CapCut's flashier/gimmicky text animations (typewriter-per-letter, rainbow) — they read as low-effort meme content, not premium product content.

---

## 4. Watermark / Brand Bug

- Logo mark (triangle + speed trail, white version) in the **top-right corner**, ~64×64px, 70% opacity, present for the entire video duration.
- Add once to the template project as a locked/pinned overlay layer so it's never forgotten on a new video.

---

## 5. Audio Template

| Layer | Guidance |
|---|---|
| Voiceover / talking head audio | Normalize to -14 LUFS, light compression, de-ess if needed |
| Trending/background audio | Max -24dB under voice, muted entirely during the Reveal scene if a specific data callout needs full clarity |
| SFX | One soft "whoosh" on Scene 1→2 cut, one "positive chime" on the Scene 4 payoff reveal, one subtle "click" on any on-screen tap/button press shown. Keep the SFX library to these 3 sounds max — consistency over variety. |
| Captions | Auto-caption every video (CapCut auto-captions or platform native) — many viewers watch muted. Caption style should roughly match `TD-Support` but can use CapCut's native caption tool for speed. |

---

## 6. Color Grade (applied as a saved CapCut adjustment preset: "TD-Grade")

- Slight contrast boost (+8)
- Slight shadow lift toward Carbon Black rather than true black (keeps dark app-screen-recordings from crushing to pure black)
- Slight blue tint in shadows (+4 blue, midtones/shadows only) to tie footage color to the Delta Blue brand without over-color-grading talking-head skin tones
- No heavy LUTs, no warm/orange grades — the brand is cool-toned

---

## 7. Screen-Recording Specs (for any clip capturing the actual app)

- Record at native resolution, crop/reframe to 9:16 in post rather than recording in a squeezed aspect ratio
- Always record with a real or realistic account state — no obviously-fake placeholder text ("Lorem ipsum," "Test User 123") ever visible on screen
- Cursor highlighting on: use CapCut's cursor-highlight/click-ripple effect so viewers can follow interactions on a small phone screen
- Slow down fast multi-step flows (e.g. the upload → processing → debrief sequence) with a quick jump-cut through the waiting states rather than showing real-time loading

---

## 8. Building This as an Actual Reusable CapCut Template

1. Build one video end-to-end using every element above (5 scenes, all 5 text presets, watermark, color grade, audio layers).
2. In CapCut: **Export → Save as Template** (or, on desktop, keep the project file and duplicate it per new video rather than starting from a blank project).
3. Name it `TrackDelta_ShortForm_Master`.
4. For each new video: duplicate the master project, replace the Scene 3 (Reveal) footage and Scene 1 hook text/line, keep everything else (fonts, watermark, grade, SFX, CTA styling) untouched.
5. Re-save the master any time a brand element changes (e.g. tagline update) so all future duplicates inherit it — don't hand-edit old exported videos retroactively.

This is the single biggest lever for looking "premium" on a small team: nobody notices five individually excellent videos as much as they notice one *consistent* channel.
