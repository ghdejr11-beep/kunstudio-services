# Sample run — Email Triage Bot

```
$ python main.py --once

[draft-saved] P0 Issue with checkout — refund? → r-7732119
[draft-saved] P1 Partnership idea / Acme x your tool → r-7732120
[draft-saved] P1 Re: intro from Sarah → r-7732121

=== Daily digest ===
P0: 1
  · sarah@bigcorp.io — Issue with checkout — refund?
P1: 4
  · john@acme.com   — Partnership idea / Acme x your tool
  · ben@y-c.com     — Re: intro from Sarah
  · liz@stripe.com  — Quick question on your usage
  · max@a16z.com    — 15 min next week?
P2: 12
  · Substack        — The Diff: $1B AI rounds
  · GitHub          — Security alert: dependabot
  · ...
P3: 23
  (auto-archived — review weekly digest if needed)
```

## Sample draft (P1 — Partnership)

> Hi John,
>
> Thanks for reaching out. Happy to chat — what specifically are you thinking
> about? If it's the API integration side, I have a 20-min slot Thursday 3pm PT
> (https://cal.com/me/intro). Otherwise reply with your top 2 questions and I
> can answer here.
>
> — Hong

(Voice-matched from 50 past sent emails: short, hedge-free, time-boxed, signature.)
