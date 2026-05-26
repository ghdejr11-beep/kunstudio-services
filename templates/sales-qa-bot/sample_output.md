# Sample chat — Sales Q&A Bot

**Site:** acme-saas.com (B2B observability tool, $99-$499/mo)

---

**Visitor:** Do you have a free trial?

**Bot:** Yes — 14 days, no credit card required, full Pro features. After day 14 you can keep using the free tier (1 service, 7-day retention) or upgrade.
Source: [Pricing — Acme](https://acme-saas.com/pricing) · [Free tier limits](https://acme-saas.com/docs/free-tier)

---

**Visitor:** Are you SOC2 compliant?

**Bot:** SOC2 Type II as of March 2026. We can share the report under NDA — message our team and we'll send it.
Source: [Security & Compliance](https://acme-saas.com/security)

---

**Visitor:** Do you integrate with Datadog?

**Bot:** Yes — we ship metrics to Datadog via OTLP. Set it up in Settings → Integrations → Datadog, paste your API key, done in ~3 minutes.
Source: [Datadog integration](https://acme-saas.com/docs/integrations/datadog)

---

**Visitor:** How does your pricing compare to New Relic?

**Bot:** I don't have a confident answer for that in our docs — want me to forward this question to our team and they'll reply by email?

*Visitor enters email → captured → routed to sales Slack with transcript.*

---

**Visitor:** Can I export data if I cancel?

**Bot:** Yes — full export (JSON or Parquet) for any time range, free for 30 days after cancellation. After that, paid customers can request export anytime by email.
Source: [Cancellation & data export](https://acme-saas.com/docs/billing/cancellation)

---

## Why this works

- **Refusal threshold**: cosine similarity < 0.35 → bot says "I don't have that" instead of inventing.
- **Citations always**: every answer carries a source link. Builds trust.
- **Email capture**: out-of-scope = sales lead. Top of funnel.
- **Top questions dashboard** reveals doc gaps (e.g. "compare to competitor X" appears 8x/wk → write a comparison page).
