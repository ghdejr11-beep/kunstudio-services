# KunStudio AI Services

> 1-person studio shipping production Claude/GPT bots for B2B founders & teams.
> $500-$1,500 setup, $99-299/mo retainer, live in 1-5 business days.

**Live site:** to be deployed (`landing/index.html`)
**Founder:** Hong Deokhun · Gyeongju, South Korea · `ghdejr11@gmail.com`
**Status:** Launched 2026-05-26.

---

## Repo layout

```
kunstudio-services/
├── README.md                              ← you are here
├── MANUAL_TODO.md                         ← what only sajangnim can do (auth/payment links)
├── templates/                             ← 5 productized bot templates
│   ├── email-triage-bot/                  $500 + $99/mo
│   ├── linkedin-post-generator/           $500 + $149/mo
│   ├── crm-followup-bot/                  $700 + $199/mo
│   ├── sales-qa-bot/                      $500 + $129/mo
│   └── cold-email-personalizer/           $500 + $129/mo
├── landing/
│   └── index.html                         ← public-facing site
├── outreach/
│   ├── 01_linkedin_comment_first.md
│   ├── 02_linkedin_dm_warm_1stdegree.md
│   ├── 03_cold_email_smb_founder.md
│   ├── 04_indie_hacker_x_dm.md
│   └── 05_loom_demo_script.md
└── docs/
    └── (case studies, security one-pager, MSA — add post-launch)
```

Each `templates/<bot>/` contains:
- `README.md` — pitch, pricing, setup time, tech stack
- `main.py` (or `server.py`) — working code skeleton, runs end-to-end
- `sample_output.md` — realistic demo output to show prospects

---

## The 5 bots (at a glance)

| # | Bot | Setup | /mo | Who it's for | Live in |
|---|---|---|---|---|---|
| 1 | Email Triage | $500 | $99 | Founders drowning in inbox | 2 days |
| 2 | LinkedIn Posts | $500 | $149 | Founders/marketers building audience | 1 day |
| 3 | CRM Follow-up | $700 | $199 | Sales teams losing deals to silence | 3 days |
| 4 | Sales Q&A Widget | $500 | $129 | SaaS sites with traffic + FAQ | 1 day |
| 5 | Cold Email Personalizer | $500 | $129 | Anyone running outbound | Same-day |

Custom scopes start at $1,500 setup.

---

## Tech stack (shared)

- **LLMs:** Claude Opus 4.7 (drafting) + Sonnet 4.7 (triage/classification). Easy swap to GPT/Gemini via `call_llm()` abstraction.
- **Languages:** Python 3.11 (4 of 5 bots). FastAPI for Sales Q&A.
- **Infra:** Hetzner CPX22 (EU, GDPR-friendly) or client's own infra.
- **Storage:** SQLite + FAISS. No managed DB needed.
- **Frontend:** Vanilla JS widget for Sales Q&A (~8KB). No React dep.

---

## Sales process

1. Inbound from landing page / LinkedIn / cold outreach
2. 20-min intro call (Cal.com) OR Loom-first flow (see `outreach/05_loom_demo_script.md`)
3. $250 refundable deposit → kicks off build
4. Ship in 1-5 days → other half of setup invoiced → monthly retainer starts
5. Monthly: tune, ship 1-2 small upgrades, monitor errors

---

## Branch policy

- `main` is protected; PR-only.
- Module isolation: this repo NEVER touches `D:/cheonmyeongdang`, `D:/kunstudio-apps`, etc.
- All secrets (Anthropic keys, OAuth tokens) live in client-specific `.env` files we never commit.

---

## ROI cheat-sheet

| Bot | Time saved | Replacement cost | Payback |
|---|---|---|---|
| Email Triage | 30 min/day × $150/hr = $1,650/mo | VA at $1,200/mo | week 1 |
| LinkedIn Posts | 4 hr/wk × $150 = $2,400/mo | Ghostwriter $1,500/mo | month 1 |
| CRM Follow-up | 2-4 recovered deals × $5K avg | SDR $4K/mo + tools | month 1 |
| Sales Q&A | +12% demo bookings (typical) | Live chat agent $3K/mo | month 1 |
| Cold Email Personalizer | 5-10× reply rate vs templates | $4K/mo SDR | month 1 |

Sales pitch: "this pays for itself in week 1, and after that it's pure margin."
