# Analytics Dashboard & KPIs

Defines what to measure and how to organize it into a dashboard. **This document specifies the dashboard; it doesn't build it.** Implementation requires wiring analytics tooling (e.g., a product analytics tool for in-app events, plus native platform analytics for social) — a separate engineering/ops task.

---

## 1. The One Metric Above All Others

Per the PRD and [ROADMAP.md](../ROADMAP.md): **percentage of active drivers showing measurable lap-time improvement after 4+ sessions.** Every KPI below exists to explain movement in this number or to serve as an earlier, faster-moving proxy for it while sample size is still small. If a marketing activity doesn't plausibly connect to this number eventually, deprioritize it regardless of how good its vanity metrics look.

---

## 2. Dashboard Structure (proposed sections)

### Section A — North Star & Core Funnel
| KPI | Definition | Source |
|---|---|---|
| North Star % | Drivers with measurable lap-time improvement after 4+ sessions | Product database (session/lap time history) |
| Sign-ups | New registrations | Supabase auth |
| Activation rate | % of sign-ups completing a first debrief | Product database (`sessions.processing_status`) |
| Session 2 return rate | % of activated users who upload a 2nd session | Product database |
| Free → Pro conversion rate | % of active free users upgrading | Product database (`subscription_tier` changes) |
| D7 / D30 retention | % returning to upload a session within 7/30 days | Product database |

### Section B — Content Performance (per platform)
| KPI | Why it matters |
|---|---|
| Views / reach | Top-of-funnel awareness, least important number here but still tracked |
| Completion rate / average watch time | Best proxy for hook + content quality (see file 12's per-platform algorithm notes) |
| Shares / saves | Best proxy for genuine value delivered, especially on TikTok/IG |
| Click-through to link-in-bio | Direct funnel-entry signal |
| Comments (qualitative tag: positive / question / negative / spam) | Content resonance and objection-handling signal |

### Section C — Acquisition Channel Attribution
| KPI | Why it matters |
|---|---|
| Sign-ups by UTM source/platform | Which platform/content actually drives registrations, not just views |
| Sign-ups by referral code (once file 15 ships) | Referral program effectiveness |
| Sign-ups by creator code (once file 13's collabs produce attribution links) | Influencer ROI |

### Section D — Community Health
| KPI | Why it matters |
|---|---|
| Discord weekly active members (once file 14's server exists) | Community engagement depth, not just size |
| Reddit/forum genuine engagement (qualitative log, not a hard number) | Longer-term trust-building signal, resistant to easy quantification — track examples, not just counts |

### Section E — Business/Cost Sanity Check
| KPI | Why it matters |
|---|---|
| Cost per activated user (marketing spend + time / activations) | Basic efficiency check once any paid effort exists |
| LLM/infra cost per debrief vs. Pro revenue per user | Ties to ROADMAP.md's M6 unit-economics validation — marketing shouldn't scale acquisition faster than the business model supports |

---

## 3. Reporting Cadence

| Cadence | What gets reviewed |
|---|---|
| Weekly | Section B (content performance) — feeds the weekly operating procedure (file 22) |
| Bi-weekly/Monthly | Section A (funnel/North Star) and Section C (attribution) — matches the 30/60/90-day checkpoint logic already defined in file 02 §7 |
| Monthly | Section D (community health) |
| Quarterly / at major milestones | Section E (cost sanity check) — ties to ROADMAP.md's M5/M6 milestones |

---

## 4. Build Priority (if building incrementally rather than all at once)

1. **First:** basic funnel tracking (sign-up → activation → session 2) — this is the minimum needed to know if content is doing anything real at all
2. **Second:** UTM/source attribution — otherwise Section A's movement can't be tied back to which platform/content caused it
3. **Third:** content performance dashboards (native platform analytics are usually sufficient starting out — a unified dashboard pulling from all platforms is a nice-to-have, not a launch requirement)
4. **Later:** referral/creator attribution codes (depends on file 15/13 actually shipping), community health tracking (depends on file 14's server existing)

---

## 5. Honesty Principle Applied to Metrics

Per the brand's core standard: internal reporting should be exactly as honest as external content. If a number looks bad, the response is understanding why and fixing the underlying thing, not picking a flattering alternate metric to report instead. The building-in-public "Honest Metric Post" template (file 08, template 2) exists specifically so this internal discipline has an external outlet too — say the real number publicly, not just internally.
