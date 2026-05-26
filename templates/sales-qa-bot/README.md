# Sales Q&A Bot

A chat widget on your landing page that answers prospect questions instantly — with your real pricing, integrations, security, and edge-cases. Backed by a curated knowledge base, not a hallucinating chatbot.

> Built by [KunStudio](https://korlens.app) — adds ~12-18% to demo bookings and cuts "what about X?" emails by 60%.

---

## What it does

1. You give us your: pricing page, docs, FAQ, top 30 sales objections, security one-pager.
2. We index it (vector store + structured rules) and ship a chat widget for your site.
3. Visitors ask anything. The bot answers in 1-3 sentences with **citations** to your source pages.
4. If the question is out-of-scope, it captures the email and routes to your inbox/Slack with the conversation transcript.
5. Dashboard shows: top 20 questions/week, gaps in your docs, conversion lift vs. baseline.

**Not** a generic GPT-on-your-site. The system refuses to answer when sources don't cover the question — protects you from confidently-wrong answers about pricing or security.

---

## Pricing

| Tier | Setup | Monthly | What's included |
|---|---|---|---|
| **Lite** | **$500** | **$129/mo** | 1 site, up to 50 source docs, 2K conversations/mo |
| **Pro** | **$1,000** | **$249/mo** | + multi-language (we already support 9), Slack/HubSpot routing, A/B test variants |
| **Custom** | **from $1,500** | **from $399/mo** | + auth'd customer support (logged-in user context), Salesforce/Intercom merge |

ROI: 100 visitors/day on your pricing page × 12% lift in demo bookings × $200 LTV/demo = ~$24K/yr extra pipeline. Pays back in 1 month for most B2B SaaS.

---

## Setup time

- **Lite:** 1 business day (you give docs, we ship).
- **Pro / Custom:** 3-5 days.

---

## How it works

```
Your docs / FAQ / pricing
   ↓
Indexer (chunk + embed + structured rules for $$ and security)
   ↓
Chat widget on site (vanilla JS, no React required)
   ↓
Q from visitor
   ↓
Retriever → top 5 chunks
   ↓
Claude Sonnet 4.7 → 1-3 sentence answer + citations
   ↓
If out-of-scope → capture email → route to Slack
   ↓
Weekly dashboard: top questions, gaps, conversion
```

Anti-hallucination: prompt forbids answers without a retrieved source. Pricing/security questions hit hard-coded rules first, RAG second.

---

## Tech stack

- Python 3.11 FastAPI backend
- `anthropic` (Claude SDK)
- `sentence-transformers` for embeddings (BGE-M3 — multilingual)
- SQLite + FAISS (no managed DB needed)
- Vanilla JS widget (~8KB minified, no React/Vue dep)

See `server.py` and `widget.html`.

---

## Get started

Book: **https://cal.com/kunstudio/intro**
