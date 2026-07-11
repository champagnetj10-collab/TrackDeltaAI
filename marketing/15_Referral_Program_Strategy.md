# Referral Program Strategy

**Status: strategy/proposal only.** Nothing described here exists in the product yet — implementing referral codes, tracking, and reward crediting is backend/product engineering work, out of scope for this marketing-content deliverable. This document defines what *should* be built and the marketing motion around it, for engineering to scope separately.

---

## 1. Why a Referral Program Fits This Product Specifically

Sim racing is a social hobby — leagues, Discord servers, teammates. A driver who gets real value from a debrief is naturally inclined to tell their teammates, and teammates racing the same series/track are a high-intent audience already (see file 01's audience notes: this crowd trusts other drivers over ads). A referral program converts word-of-mouth that's already happening informally into something trackable and slightly incentivized.

---

## 2. Proposed Mechanic (for engineering to evaluate/scope)

| Element | Proposal |
|---|---|
| Referral trigger | Existing user shares a unique referral link/code |
| New user reward | Extra free session(s) in their first month (e.g., +2 on top of the standard 3), or a discounted first month of Pro |
| Referring user reward | A free month of Pro, or additional sessions credited, once the referred friend completes their first real debrief (not just signs up — reward the moment of actual product value delivered, to avoid incentivizing empty sign-ups) |
| Cap | Reasonable cap per user per month (e.g., max 3-5 rewarded referrals/month) to avoid abuse vectors |
| Attribution | Unique code per user, also reusable as the creator-attribution mechanism referenced in file 13's tracking sheet |

**Reward-timing principle:** reward on real activation (first completed debrief), not on raw sign-up — this avoids incentivizing someone to spam a referral link to people who never actually use the product, which would pollute both the free-tier cost base and the data quality of "who's an engaged user."

---

## 3. Marketing Motion Around the Program

1. **In-product surfaces** (proposal for product to place, not built here): a "refer a teammate" prompt on the dashboard after a driver's 2nd-3rd completed debrief — timed to when someone has enough real value to want to share it, not on day one before they've seen anything.
2. **Content tie-ins:**
   - A dedicated short-form video announcing the program once it exists (add to the SF backlog when it ships)
   - Mention in the weekly ship log (file 08 template 1) at launch
   - A pinned post in the Discord server (file 14) once both exist
3. **League/team framing:** market this specifically toward league organizers and team captains — "get your whole team's Driver DNA building at once" is a stronger pitch than a generic 1:1 referral ask, and matches how this audience actually operates (they already coordinate as teams/leagues).
4. **Creator tie-in:** a creator's unique code (from file 13's outreach) can double as both an attribution mechanism and a referral reward for their audience — "use [creator]'s link, you both get a bonus" — this is a stronger collab offer than exposure alone.

---

## 4. What to Track (feeds file 21)

- Referral links generated vs. referral links actually used (activation rate of the mechanic itself)
- Referred sign-ups vs. referred *activations* (someone completing a first debrief) — the second number is what matters
- Cost of rewards issued vs. revenue attributable to referred users over time (basic unit economics sanity check)
- Which channel/context drives the most referral shares (in-product prompt vs. Discord vs. a specific creator's code)

---

## 5. Guardrails

- Never let the referral reward structure create pressure to inflate free-tier costs unsustainably — this needs a real look from whoever owns unit economics before it ships, not just a marketing decision
- Disclose the mechanic honestly — no dark-pattern framing ("your friend is SO CLOSE to a reward, hurry!") — keep language consistent with the brand voice guide's plain, honest tone
- If abuse patterns show up (fake accounts referring each other), address at the product/fraud-prevention level, not by shutting down the whole program reactively

---

## 6. Sequencing

This is explicitly a **post-launch, post-traction** initiative — per [ROADMAP.md](../ROADMAP.md)'s M5 (First 100 Paying Customers) framing, referral mechanics are a growth-phase lever, not a pre-launch requirement. Don't let building this delay the actual product/launch priorities in the engineering roadmap.
