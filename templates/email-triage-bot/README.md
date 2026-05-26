# Email Triage Bot

Auto-classify your Gmail inbox and draft replies — so you stop drowning in email.

> Built by [KunStudio](https://korlens.app) — same engine that runs the founder's own inbox (1,200+ msgs/wk, 0 missed).

---

## What it does

1. Polls Gmail every 5 minutes (read-only by default).
2. Classifies each unread thread into:
   - **P0 — Money / Customer / Legal** (escalate now)
   - **P1 — Sales / Partnership** (reply today)
   - **P2 — Newsletter / FYI** (archive or summarize)
   - **P3 — Spam / Cold** (auto-archive)
3. For P0–P1, drafts a reply in your voice (Claude 4.7) and saves it to Gmail Drafts.
4. Sends you a 1-line daily digest at 09:00 local.

You hit Send. The bot does the rest.

---

## Pricing

| Tier | Setup (one-time) | Monthly retainer | What's included |
|---|---|---|---|
| **Starter** | **$500** | **$99/mo** | 1 inbox, classification + drafts, daily digest |
| **Pro** | **$900** | **$199/mo** | + custom labels, Slack alerts, calendar auto-decline, 2 inboxes |
| **Custom** | **from $1,500** | **from $299/mo** | + CRM sync (HubSpot/Pipedrive), team rules, SLA monitoring |

ROI math: 1 founder hour = $150+. Saving 30 min/day = **$3,300+/mo**. Pays back in week 1.

---

## Setup time

- **Starter:** 2 business days from kick-off (we handle Google OAuth, classifier tuning, draft style).
- **Pro / Custom:** 3–5 days depending on integrations.

---

## How it works (technical)

```
Gmail API (read-only)
   ↓ poll every 5 min
   ↓
Triage prompt (Claude Sonnet 4.7 — cheap pass)
   ↓ classify P0/P1/P2/P3
   ↓
Draft prompt (Claude Opus 4.7 — voice match from 50 sample threads)
   ↓
Gmail Drafts API → saved, never auto-sent
   ↓
Daily digest → email or Slack
```

- Hosted on KunStudio infra (Hetzner) — your data never leaves EU/US-controlled servers.
- BYO-key option available (you provide Anthropic API key, bill direct).

---

## Tech stack

- Python 3.11
- `google-api-python-client` (Gmail)
- `anthropic` (Claude SDK)
- APScheduler for polling
- Optional: Slack SDK, HubSpot SDK

See `main.py` for the working skeleton.

---

## What you provide

1. Google Workspace or Gmail account (we'll send OAuth consent flow).
2. ~50 past sent emails so we can match your tone.
3. Stripe / PayPal for setup + monthly billing.

---

## Get started

Book a 20-min call: **https://cal.com/kunstudio/intro** *(or DM on LinkedIn)*

Or pay setup deposit ($250 refundable if we can't deliver): **[Stripe Payment Link — placeholder]**

— Hong, founder of KunStudio
