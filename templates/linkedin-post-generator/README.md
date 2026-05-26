# LinkedIn Post Generator

5 ready-to-publish LinkedIn posts/week — in your voice, on your topics, from your raw notes.

> Built by [KunStudio](https://korlens.app) — the founder's own LinkedIn went from 0 to 30 1st-degree connections in 14 days using this engine.

---

## What it does

1. You drop **3-5 raw notes/week** into a Notion page or shared Google Doc (a sentence each — what you shipped, what surprised you, a customer quote).
2. The bot:
   - Studies your **last 30 LinkedIn posts** to extract your voice (hook style, length, emojis, line breaks, hashtag pattern).
   - Researches the topic (your blog, top 3 LinkedIn posts on the angle, latest news).
   - Generates **5 distinct posts/week** — different formats: founder-story / contrarian / how-I-did-it / micro-data / engagement question.
3. Saves them to a Buffer / Hypefury / LinkedIn-native scheduler queue, or to Notion for your review.

You skim & schedule. The bot generated. Audience grows weekly.

---

## Pricing

| Tier | Setup | Monthly | Output |
|---|---|---|---|
| **Solo** | **$500** | **$149/mo** | 5 posts/week, you review |
| **Growth** | **$900** | **$249/mo** | + carousel image generation, weekly best-post analytics |
| **Agency** | **from $1,500** | **from $399/mo** | + multi-client dashboard, white-label |

ROI math: A LinkedIn presence that pulls 1 inbound demo/month at $5K ACV = $60K/yr. Setup pays back in week 2.

---

## Setup time

- **Solo:** 1 day (we ingest your last 30 posts + 50 lines of voice).
- **Growth:** 2 days (+ image prompt tuning).
- **Agency:** 5 days.

---

## How it works

```
Notion / Google Doc (your raw notes)
   ↓
Voice extractor (Claude Opus 4.7 reads last 30 posts)
   ↓
Topic researcher (Brave / Tavily web search)
   ↓
Post generator → 5 variants/week
   ↓
Buffer / Hypefury API → scheduled
   (or Notion → human review queue)
```

---

## Tech stack

- Python 3.11
- `anthropic` (Claude SDK)
- `notion-client` (input)
- LinkedIn API (read-only, for voice samples — we use a 30-day token)
- Buffer API or LinkedIn native scheduling

See `main.py`.

---

## What you provide

1. URL of your LinkedIn profile (public).
2. Notion access (we set up the template).
3. 1× 20-min onboarding call to lock topic pillars (3-5 themes you want to own).

---

## Get started

Book: **https://cal.com/kunstudio/intro**
Or DM "linkedin bot" on LinkedIn → [Hong / KunStudio]
