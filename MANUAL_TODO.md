# Manual To-Do — Sajangnim Only (본인인증 / 결제 / OAuth Required)

Items only sajangnim can do (the AI cannot do these in your stead — they need your face, 2FA device, or a card).

Sorted by **revenue impact** (highest first) — do the top 3 today.

---

## TIER 1 — Do today (unblocks paying customers)

### ☐ 1. Cal.com — Set up `cal.com/kunstudio/intro` (5 min, free)

- Go to https://cal.com → "Sign up" → use `ghdejr11@gmail.com`.
- Set username: `kunstudio` (locks the URL `cal.com/kunstudio`).
- Create event type: **"Intro call — 20 min"**.
  - Available: Mon-Fri, 09:00-17:00 KST (or your preference).
  - Buffer: 15 min between calls.
  - Auto-connect to Google Calendar.
- Save. Copy the link `https://cal.com/kunstudio/intro` — the landing page already points here.

**Why now:** every outreach script ends with this URL. Without it, you lose 50%+ of warm leads.

---

### ☐ 2. Stripe Payment Link — $250 refundable deposit (10 min)

- Stripe dashboard → https://dashboard.stripe.com/payment-links
- Click "+ New" → "Payment link"
  - **Product**: "KunStudio bot — refundable build deposit"
  - **Price**: $250 USD (one-time)
  - **Description**: "Refundable deposit to lock a build slot. Refunded in full if we can't ship the agreed scope."
- After save, click "..." → "Customize page" → set business name "KunStudio", upload logo from `D:/kunstudio-promo/` if available.
- Copy the link (looks like `https://buy.stripe.com/XXXXXX`).
- **Replace in:** `landing/index.html` (search for `Stripe Payment Link (set up after launch)`) — paste the real URL.

**Why now:** Stripe Payment Link is the lowest-friction "yes" mechanism in the funnel. No invoicing back-and-forth.

If Stripe Korea is blocked for you (per memory `feedback_stripe_korea_unavailable.md`) → use **PayPal Business invoice link** instead:
- PayPal Business → Pay & Get Paid → Invoicing → "Create" → save as template ($250 deposit) → use the link.

---

### ☐ 3. LinkedIn Outreach — Warm DMs to 30+ launch-post engagers (30-60 min)

- Open your 5/26 launch post on LinkedIn.
- Click "X reactions" → list of everyone who liked.
- Click into each profile → use **Variant A** from `outreach/02_linkedin_dm_warm_1stdegree.md`.
- Send **8/day max** (LinkedIn flags faster sends).
- Track in a Google Sheet:
  ```
  name | role | company | sent (date) | replied | loom sent | call booked | closed
  ```

**Target:** 30 warm DMs in 4 days → 6-9 replies → 2 Looms → 1 close (= $599-$1,799 first month).

---

## TIER 2 — Do this week (compounds revenue)

### ☐ 4. Deploy landing page to Vercel

- `cd D:/kunstudio-services/landing` → drag `index.html` into Vercel dashboard, or:
- `vercel --prod` (you have CLI already per memory).
- Set custom domain: `services.kunstudio.com` or `kunstudio-ai.com` (purchase if needed — $14/yr on Cloudflare).
- After deploy, replace `https://kunstudio-services-link` placeholder in `outreach/03_cold_email_smb_founder.md` with the real URL.

### ☐ 5. Record 5 base Looms

Per `outreach/05_loom_demo_script.md`:
- ~3 hours total for all 5
- Loom free tier = unlimited <5 min Looms (perfect)
- Use sajuapp.app or a dummy inbox for the demo data
- Save Loom URLs in `docs/loom_urls.md` (create on demand)

### ☐ 6. PayPal Subscriptions for monthly retainer

You already have **PayPal Plans v4** active (per memory `project_paypal_plans_v4_active.md` — Monthly $7.99 / Annual $49.99 / Family $79.99). Those are for Cheonmyeongdang.

For KunStudio Services, you need **new** plans:
- $99/mo (Email Triage)
- $129/mo (Sales Q&A, Cold Email)
- $149/mo (LinkedIn Posts)
- $199/mo (CRM Follow-up)
- $249/mo (CRM Team / etc)
- $299/mo (Premium)

Steps:
- PayPal Developer → Products & Plans → "Create product" "KunStudio Services Retainer"
- Create the 6 plans above. Save each Plan ID.
- Generate hosted approval URL for each via API or PayPal Subscription button.

Or simpler: just invoice monthly manually until you hit 10 customers — automation pays back after that.

### ☐ 7. Onboarding doc

Create `docs/onboarding.md` covering:
- What you need from the client (OAuth scopes for Gmail, sample data, voice samples).
- Timeline: kickoff call → day 1 setup → day 2 prompt tuning → day 3 deploy → day 5 review.
- Security one-pager (where data lives, retention, how to delete).

---

## TIER 3 — Nice to have

### ☐ 8. Domain for kunstudio-services
- `kunstudio.services`, `kunstudio.ai`, or subdomain on `korlens.app/services`.
- Cloudflare Registrar: ~$14/yr.

### ☐ 9. Case study posts
After first 2 paying customers → write 1 LinkedIn post + 1 short blog per bot type. Compounds inbound.

### ☐ 10. Affiliate referral
20% rev-share for 6 months for anyone who refers a paying client. Best leverage of warm network.

---

## What the AI is doing in parallel (no action needed)

- Building & maintaining all 5 bot templates (READMEs, code, sample outputs).
- Writing & maintaining the 5 outreach scripts.
- Building the landing page HTML.
- Tracking PRs and code reviews.

What the AI **cannot** do without you:
- Sign up for Cal.com / Stripe / PayPal (need your phone for 2FA, your face for ID verification).
- Send LinkedIn DMs (LinkedIn auth is yours alone, sending from a bot risks account ban).
- Record Looms with your face/voice (the personal touch IS the product).
- Take the intro call.

---

## Day-1 success criteria

By end of 2026-05-27:
- [ ] Cal.com link live
- [ ] Stripe (or PayPal) deposit link live, embedded in landing page
- [ ] 8-15 LinkedIn warm DMs sent to launch-post engagers
- [ ] Landing page deployed and reachable on a URL

By end of 2026-06-02:
- [ ] First Loom recorded
- [ ] First "go" reply from a warm DM
- [ ] First $250 deposit received
- [ ] First bot built & shipped → first $500-1500 in setup + first monthly retainer activated
