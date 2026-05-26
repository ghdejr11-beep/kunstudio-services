# Cold Email Personalizer

Upload a lead list. Get a CSV of cold emails personalized **per lead** — referencing their last LinkedIn post, recent company news, or a real fact about their company. 3-10× higher reply rates than templates.

> Built by [KunStudio](https://korlens.app) — our test campaign of 100 cold emails got 11 replies and 1 closed $14K deal in 14 days.

---

## The problem

You buy a 500-lead list. You write a great template. You blast. 0.5% reply. Why? Because everyone else is blasting the same template at the same leads.

Personalization works — but doing it by hand is 5 min/lead × 500 = 41 hours. No one does it.

## What it does

1. You upload a CSV: `first_name, last_name, email, company, role, linkedin_url, website`
2. For each lead, the bot:
   - Scrapes their last LinkedIn post (public).
   - Pulls their company About / Careers / latest blog (top result).
   - Looks for a hook: shipped feature, raised round, hiring spike, recent talk.
3. Generates a 3-sentence cold email:
   - **L1**: specific reference to that hook.
   - **L2**: connect to your offer in 1 line.
   - **L3**: low-friction ask (reply, not meeting).
4. Outputs a CSV ready to dump into Instantly, Smartlead, lemlist, Apollo, or your own SMTP.

Each email is **different**. No template loop. Compliant — we use only public sources, throttle scrapes, and respect robots.txt.

---

## Pricing

| Tier | Setup | Monthly | Volume |
|---|---|---|---|
| **Starter** | **$500** | **$129/mo** | up to 500 leads/mo, you provide list |
| **Pro** | **$900** | **$249/mo** | up to 2,000/mo, + lead enrichment (we find LinkedIn URLs), + A/B test variants |
| **Custom** | **from $1,500** | **from $399/mo** | 5,000+, full done-for-you (we research ICPs, build list, run sends) |

ROI: 1 closed deal at $5K from a 500-lead campaign = 8× payback in month 1.

---

## Setup time

- **Starter:** Same day. Send us the list, get the CSV back in 2-6 hours depending on volume.
- **Pro / Custom:** 2-3 days for ICP definition + enrichment workflow.

---

## How it works

```
Lead CSV (your list)
   ↓
LinkedIn scraper (public, throttled, last 3 posts)
   ↓
Company researcher (homepage + careers + first blog post)
   ↓
Hook picker (Claude — what's the most specific, recent angle?)
   ↓
3-sentence email generator (Claude Opus 4.7)
   ↓
Quality filter (regex: no '!', no 'just', no "I hope this finds you")
   ↓
Output CSV (lead + subject + body)
```

---

## Tech stack

- Python 3.11
- `anthropic`
- `httpx` + `selectolax` for static scraping
- (For LinkedIn) Playwright headless w/ throttle — or BYO Proxycurl/PhantomBuster API key
- `pandas` for CSV in/out

See `main.py`.

---

## What you provide

1. CSV of leads with at minimum `email` + `linkedin_url` OR `company website`.
2. Your offer summary (~5 sentences — who you help, with what, how).
3. 5 past cold emails you've sent (for voice).

We never use scraped data for anything except generating *your* outbound. No reselling, no list-building for other clients.

---

## Get started

Book: **https://cal.com/kunstudio/intro**
