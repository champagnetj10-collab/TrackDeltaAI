# TrackDelta AI — Complete Marketing System

A production-ready content and growth engine for TrackDelta AI across YouTube, TikTok, Instagram Reels, X, LinkedIn, Facebook, Reddit, and Discord. This folder is documentation and content planning only — it does not touch the application, and nothing here should be interpreted as changing product behavior. If a piece of marketing content describes a feature, verify against the actual current app before publishing; product claims must stay accurate as the app evolves. Several files here (referral program, A/B testing, email sequence) propose things that need real engineering work before they exist — each says so explicitly where that applies.

## Read First

**[01_Brand_Voice_and_Style_Guide.md](01_Brand_Voice_and_Style_Guide.md)** — the voice, tone, visual identity, and principles every other file assumes. Read this before writing or approving anything else in this folder.

## Planning

- **[02_90_Day_Content_Calendar.md](02_90_Day_Content_Calendar.md)** — content pillars, platform cadence, and the 13-week arc from launch to 90-day retrospective.
- **[22_Weekly_Marketing_Operating_Procedure.md](22_Weekly_Marketing_Operating_Procedure.md)** — the recurring weekly/monthly rhythm that actually runs this system day to day.

## Content Banks

- **[03_Short_Form_Video_Ideas.md](03_Short_Form_Video_Ideas.md)** — 50 short-form video ideas (SF-01–SF-50) with hooks, scripts, captions, and CTAs.
- **[11_Additional_Short_Form_Ideas.md](11_Additional_Short_Form_Ideas.md)** — 100 more, new formats (SF-51–SF-150): myth-busting, deep engineering explainers, track/car-specific, reaction/UGC, "Ask Delta" Q&A, data storytelling, honest competitive positioning, fast-numbers explainers, multi-part series, culture.
- **[04_Long_Form_YouTube_Outlines.md](04_Long_Form_YouTube_Outlines.md)** — 20 long-form YouTube video outlines (LF-01–LF-20).
- **[09_Educational_Content_Series.md](09_Educational_Content_Series.md)** — the underlying teaching content (telemetry, braking, throttle, racing lines, racecraft, consistency) that feeds the content banks above.
- **[24_One_Session_Every_Platform_Scripts.md](24_One_Session_Every_Platform_Scripts.md)** — the process for turning one real debrief into a full week of platform-native content without repeating yourself.

## Production

- **[05_CapCut_Editing_Template.md](05_CapCut_Editing_Template.md)** — the reusable 5-scene storyboard, text presets, color grade, and audio template for every short-form video.
- **[06_Thumbnail_Templates_and_Titles.md](06_Thumbnail_Templates_and_Titles.md)** — 4 reusable thumbnail templates + a title bank matched to every long-form outline.
- **[23_AI_Video_Generation_Prompts.md](23_AI_Video_Generation_Prompts.md)** — ready-to-use LLM prompts for turning a real (permissioned) Driver DNA report or debrief into a script, visual brief, or multi-platform post set.

## Platform & Distribution Strategy

- **[12_Platform_Specific_Strategies.md](12_Platform_Specific_Strategies.md)** — deep, tactical, per-platform guidance (algorithm behavior, format specs, timing) for TikTok, Instagram, YouTube, X, LinkedIn, Facebook, and Reddit.
- **[16_SEO_Content_Strategy.md](16_SEO_Content_Strategy.md)** — YouTube search and marketing-site SEO, keyword targets, on-page/on-video checklists.
- **[10_Creator_Community_Hashtag_List.md](10_Creator_Community_Hashtag_List.md)** — creators/communities to research for collabs, plus the working hashtag bank. **Verify before outreach — see the caveat at the top of that file.**
- **[13_Influencer_Outreach_Playbook.md](13_Influencer_Outreach_Playbook.md)** — the actual outreach process: tiering, message templates, tracking sheet, what never to do.
- **[14_Discord_Community_Growth_Plan.md](14_Discord_Community_Growth_Plan.md)** — growing TrackDelta's own Discord server (distinct from engaging *other* communities in file 10).

## Execution Playbooks

- **[07_Launch_Week_Content.md](07_Launch_Week_Content.md)** — fully detailed day-by-day social launch plan for week 1.
- **[19_Product_Hunt_Launch_Plan.md](19_Product_Hunt_Launch_Plan.md)** — a separate, PH-specific launch plan (recommended for week 2-4, not day 1 — see the file for why).
- **[20_Beta_Launch_Checklist.md](20_Beta_Launch_Checklist.md)** — the marketing/GTM-side checklist for closed beta, cross-referencing the engineering-side gate in `ROADMAP.md`.
- **[08_Building_In_Public_Templates.md](08_Building_In_Public_Templates.md)** — 8 fill-in-the-blank templates for documenting real development progress honestly.

## Growth & Lifecycle

- **[15_Referral_Program_Strategy.md](15_Referral_Program_Strategy.md)** — proposed mechanic + marketing motion (strategy only — not built).
- **[18_Email_Onboarding_Sequence.md](18_Email_Onboarding_Sequence.md)** — 7-email lifecycle sequence, full copy, with engineering trigger notes.
- **[17_Landing_Page_AB_Testing.md](17_Landing_Page_AB_Testing.md)** — test ideas grounded in the actual current landing/pricing pages (proposal only — needs experimentation infrastructure).

## Measurement

- **[21_Analytics_Dashboard_KPIs.md](21_Analytics_Dashboard_KPIs.md)** — what to measure, how to organize it, and how it all ties back to the product's North Star metric.

## How These Fit Together

```
01 Brand Voice ─────────────────────────────────────────────────────┐
                                                                       ▼
22 Weekly Operating Procedure  ──►  runs the whole system week to week
        │
        ├──► 02 Content Calendar ──► which pillar, platform, week
        │        │
        │        ├──► 03 / 11 Short-Form Ideas ──► 05 CapCut Template ──► 06 Thumbnails/Titles
        │        ├──► 04 Long-Form Outlines ──────► 06 Thumbnails/Titles
        │        ├──► 09 Educational Series (source material for both banks)
        │        ├──► 24 One-Session-Every-Platform (derives a week of content from one real debrief)
        │        ├──► 23 AI Prompts (accelerates scripting from real data)
        │        ├──► 07 Launch Week / 19 Product Hunt / 20 Beta Checklist (execution playbooks)
        │        └──► 08 Building in Public (recurring templates)
        │
        ├──► 12 Platform Strategies + 16 SEO ──► how each piece actually gets distributed
        ├──► 10 Creators/Communities/Hashtags ──► 13 Outreach Playbook ──► 14 Discord Growth
        ├──► 15 Referral + 18 Email + 17 A/B Testing ──► lifecycle/growth layer
        └──► 21 Analytics/KPIs ──► feeds back into 22's weekly review, closing the loop
```

## Operating Principle

Every file in this folder is downstream of one rule, stated in the brand voice guide and repeated throughout: **don't publish a claim the product can't back up.** When a file here and the live product ever disagree, the product is correct and this content needs updating — not the other way around. Where a file proposes something not yet built (referral mechanics, A/B infrastructure, email automation, analytics wiring), it says so explicitly — treat those as engineering-ready specs, not as things already live.
