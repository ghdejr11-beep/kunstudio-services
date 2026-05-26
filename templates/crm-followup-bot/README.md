# CRM Follow-up Bot

Stops deals from going cold. Sends the right follow-up at the right time, in your voice — using your HubSpot or Pipedrive data.

> Built by [KunStudio](https://korlens.app) — recovers deals worth 5-15× the monthly retainer in the first 30 days, typical.

---

## The problem

You/your AE log a deal, send 2 emails, hear nothing, move on. Deal goes to "Lost — no response". You just left $5K-$50K on the table.

The real failure mode: **follow-up #3, #5, #7**. Most reps stop at #2. Stats: ~50% of closed deals took 5+ touches.

## What it does

1. Polls HubSpot/Pipedrive every hour.
2. Finds deals where:
   - Last activity > 4 days ago, AND
   - Stage is **not** Closed Won / Closed Lost, AND
   - Last touch wasn't outbound from you in last 48h.
3. For each, Claude:
   - Reads the deal notes + last 5 emails in the thread.
   - Picks a follow-up angle (value-add, case study, soft check-in, hard re-engage).
   - Drafts a personalized email referencing **specifics** from the thread (not generic "circling back").
4. Saves to your Outbox (Gmail Drafts) OR auto-sends if you've enabled it for that segment.
5. Logs the touch back to CRM.

---

## Pricing

| Tier | Setup | Monthly | What's included |
|---|---|---|---|
| **Solo** | **$700** | **$199/mo** | 1 user, HubSpot or Pipedrive, drafts only |
| **Team** | **$1,200** | **$349/mo** | up to 3 reps, auto-send rules, Slack alerts |
| **Sales-Org** | **from $1,500** | **from $499/mo** | 5+ reps, Salesforce, custom playbooks, weekly performance report |

ROI math: 1 recovered $5K deal = 25× the setup. Average client recovers 2-4 deals in month 1.

---

## Setup time

- **Solo:** 2 business days.
- **Team / Sales-Org:** 5-7 days (rule mapping, segment definitions).

---

## How it works

```
HubSpot / Pipedrive API
   ↓ poll every 1h
   ↓
Stale-deal filter (4+ days, not closed, no recent outbound)
   ↓
Context loader (notes + last 5 emails per deal)
   ↓
Angle picker (Claude — value-add | case-study | check-in | re-engage)
   ↓
Personalized draft (Claude Opus 4.7, your voice)
   ↓
Gmail Drafts (or auto-send for warm segment)
   ↓
CRM log activity
```

---

## Tech stack

- Python 3.11
- `hubspot-api-client` or `pipedrive-api-client`
- `anthropic`
- Gmail API for send
- APScheduler for hourly run

See `main.py`.

---

## Get started

Book: **https://cal.com/kunstudio/intro**
