# SEO Content Strategy

Expands the brief "SEO / Discovery Note" at the end of [09_Educational_Content_Series.md](09_Educational_Content_Series.md) into a full strategy. Covers both YouTube search (the biggest search surface this content system touches) and the marketing site itself (`trackdeltaai.com` — the landing/pricing pages built in the frontend redesign).

---

## 1. Two Distinct SEO Surfaces

| Surface | What ranks here | Owned by |
|---|---|---|
| YouTube search | Long-form educational videos (file 04, file 09) | Content team |
| Google / web search | The marketing site's landing and pricing pages, plus any future blog/docs content | Product + content, jointly |

---

## 2. YouTube SEO

**Keyword research approach:** prioritize real search terms a competitive-but-not-expert iRacing driver would type, not brand terms. Use YouTube's own autocomplete/suggested-search as the primary free research tool (type "how to trail brake" etc. and note what YouTube suggests completing it to).

**High-value target terms (starting list, expand via autocomplete research over time):**
- "how to trail brake iRacing"
- "iRacing telemetry explained"
- "why am I not consistent sim racing"
- "how to read a brake trace"
- "iRacing braking tips"
- "how to get faster at iRacing"
- "sim racing consistency"
- "iRacing setup vs driving"
- "[specific track name] iRacing line"

**On-video SEO checklist (apply to every long-form upload):**
- [ ] Target keyword appears naturally in the title (searchable term first per file 06's title bank guidance for education-pillar content)
- [ ] Target keyword appears in the first sentence of the description
- [ ] Description includes a 2-3 sentence real summary (not just a link dump) — YouTube's search indexing weighs description content
- [ ] Chapters/timestamps included (also surfaces as rich results in search)
- [ ] Closed captions uploaded/verified for accuracy (auto-captions have real error rates that hurt both accessibility and indexing quality)
- [ ] Relevant, specific tags (avoid generic single-word tags like "racing" — favor "iracing telemetry," "sim racing coaching," etc.)

**Playlist strategy:** group long-form videos into topic playlists (e.g., "Braking," "Consistency," "Building TrackDelta") — playlists both help session time (YouTube autoplays the next video) and give a secondary ranking surface.

**Thumbnail/CTR note:** search ranking is influenced by click-through rate on the search results page, not just the algorithm's initial placement — this is another reason file 06's thumbnail discipline matters for SEO, not just discovery-feed performance.

---

## 3. Marketing Site SEO

**Current state:** the landing page (`/`) and pricing page (`/pricing`) exist and are built (see the frontend redesign). Neither currently has dedicated blog/article content — this section defines what to add without touching the existing app code; any implementation is a separate frontend content-page addition, not something this document builds.

**Priority pages to eventually add (proposal for a `/blog` or `/learn` section, not yet built):**
- Long-form written companions to the strongest educational YouTube videos (e.g., a full "How to Read Telemetry" article mirroring LF-14) — written content ranks on Google search terms differently than video content ranks on YouTube search, so the two aren't redundant
- A comparison-style page addressing genuine, honest positioning questions (mirrors SF-111 through SF-115's honest-positioning short-form content, expanded to a real page) — e.g., "TrackDelta vs. raw telemetry tools" as an actual landing page, since "iRacing telemetry tool comparison"-style searches have real intent behind them
- Track-specific pages if/when corner-level content becomes rich enough per track (ties to the engineering roadmap's track-data-seeding work) — e.g., a "Watkins Glen iRacing Guide" page

**On-page technical basics (apply to any new page):**
- One clear H1 matching search intent
- Meta description written for humans (accurately describing the page, not keyword-stuffed) — the existing landing page's metadata (`app/layout.tsx`) already follows this discipline; extend the same standard to any new page
- Internal linking between the marketing site and relevant YouTube content (and vice versa in video descriptions) so both surfaces reinforce each other

**Backlink strategy (organic, no paid link schemes):**
- Genuine participation in Reddit/forums (file 12's Reddit section) naturally generates some organic backlinks when the content is good enough to be referenced
- Creator collabs (file 13) — ask collaborating creators to link the tool in their video description, a natural, honest ask given they're already covering it
- Community mentions (file 10) accumulate over time as a natural byproduct of genuine participation, not a link-building campaign to run separately

---

## 4. Content Calendar Integration

SEO-priority videos (myth-busting batch 6 and deep-education batches from file 11, plus file 09's core topics) should be flagged specifically in the weekly planning process (file 22) as "search-intent" content — when deciding what to publish long-form in a given week, weight search-intent topics slightly higher than pure trend-following, since their value compounds over months rather than decaying after the first 48 hours like most social content.

## 5. Measurement

Track (feeds file 21):
- YouTube: search traffic source percentage (YouTube Studio breaks down traffic by source, including "YouTube search")
- Which specific search terms are driving traffic (YouTube Studio's search terms report)
- Marketing site: organic search sessions and top landing pages (once analytics is wired up — see file 21)
- Keyword rank tracking for the priority term list above, checked monthly, not obsessively — SEO is a slow-compounding channel, not a weekly-optimization one
