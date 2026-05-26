"""
Cold Email Personalizer — KunStudio
====================================

Input  : leads.csv  (first_name,last_name,email,company,role,linkedin_url,website)
Output : out.csv    (+ subject,body,hook_used,quality_flags)

Run:
    python main.py --in leads.csv --out out.csv --offer offer.txt --voice voice.txt
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

import httpx
from anthropic import Anthropic
from selectolax.parser import HTMLParser

MODEL = "claude-opus-4-7"
USER_AGENT = "KunStudio-CEP/1.0 (+https://korlens.app/bot)"
TIMEOUT = httpx.Timeout(15.0)


@dataclass
class Lead:
    first_name: str
    last_name: str
    email: str
    company: str
    role: str
    linkedin_url: str
    website: str


@dataclass
class Hook:
    type: str           # "company_news" | "linkedin_post" | "career_milestone" | "blog_topic"
    text: str
    source_url: str


# ─────────────────────────── scraping ──────────────────────────────
async def fetch_text(client: httpx.AsyncClient, url: str, max_chars: int = 4000) -> str:
    if not url or not url.startswith(("http://", "https://")):
        return ""
    try:
        r = await client.get(url, timeout=TIMEOUT, follow_redirects=True,
                              headers={"User-Agent": USER_AGENT})
        if r.status_code != 200:
            return ""
        html = HTMLParser(r.text)
        for tag in ["script", "style", "nav", "footer"]:
            for n in html.css(tag):
                n.decompose()
            # selectolax: use .strip_tags or fallback
        text = html.body.text(separator=" ", strip=True) if html.body else ""
        text = re.sub(r"\s+", " ", text)
        return text[:max_chars]
    except Exception:
        return ""


async def research_lead(client: httpx.AsyncClient, lead: Lead) -> dict:
    tasks = []
    if lead.website:
        tasks.append(fetch_text(client, lead.website))
        tasks.append(fetch_text(client, lead.website.rstrip("/") + "/blog"))
    else:
        tasks += ["", ""]
    # LinkedIn: requires Playwright or a paid API. Skipped here — placeholder.
    homepage, blog = await asyncio.gather(*tasks) if tasks else ("", "")
    return {"homepage": homepage, "blog": blog, "linkedin": ""}


# ─────────────────────────── Claude calls ──────────────────────────
def pick_hook(client: Anthropic, lead: Lead, research: dict) -> Hook:
    sys = (
        "You read research about a person and their company and pick the SINGLE BEST hook "
        "for a cold email: most specific, most recent, most relevant. "
        "Return JSON: {type, text, source_url}. type in "
        '["company_news","linkedin_post","career_milestone","blog_topic"]. '
        "If nothing specific is found, return {type:'blog_topic', text:'<best guess about their focus>', source_url:''}."
    )
    user = (
        f"Lead: {lead.first_name} {lead.last_name}, {lead.role} at {lead.company}\n"
        f"LinkedIn: {lead.linkedin_url}\nWebsite: {lead.website}\n\n"
        f"Homepage text:\n{research['homepage'][:2500]}\n\n"
        f"Blog text:\n{research['blog'][:2500]}\n\n"
        f"LinkedIn snippet:\n{research['linkedin'][:1000]}\n"
    )
    r = client.messages.create(
        model=MODEL, max_tokens=250, system=sys,
        messages=[{"role": "user", "content": user}],
    )
    text = r.content[0].text.strip()
    text = text[text.find("{") : text.rfind("}") + 1]
    data = json.loads(text)
    return Hook(data.get("type", "blog_topic"),
                data.get("text", ""),
                data.get("source_url", ""))


def generate_email(client: Anthropic, lead: Lead, hook: Hook, offer: str, voice: str) -> dict:
    sys = (
        "You write cold emails. Rules:\n"
        "- EXACTLY 3 sentences in the body.\n"
        "- Sentence 1: reference the hook with a SPECIFIC fact. No 'I noticed that...'.\n"
        "- Sentence 2: connect to the offer in plain language.\n"
        "- Sentence 3: low-friction ask — invite a reply, not a meeting.\n"
        "- Subject: ≤ 7 words, lowercase OK, curious not pitchy.\n"
        "- Banned: 'just', 'wanted to', '!', 'I hope this finds you', 'circling back', "
        "'quick question' (overused), 'reach out'.\n"
        f"Voice samples to match:\n{voice[:4000]}\n\n"
        "Return JSON: {subject, body}."
    )
    user = (
        f"Lead: {lead.first_name} {lead.last_name}, {lead.role} at {lead.company}\n"
        f"Hook ({hook.type}): {hook.text}\nSource: {hook.source_url}\n\n"
        f"Offer:\n{offer}"
    )
    r = client.messages.create(
        model=MODEL, max_tokens=400, system=sys,
        messages=[{"role": "user", "content": user}],
    )
    text = r.content[0].text.strip()
    text = text[text.find("{") : text.rfind("}") + 1]
    return json.loads(text)


# ─────────────────────────── quality gates ─────────────────────────
BANNED = ["just ", "wanted to", "I hope this", "circling back", "quick question",
          "reach out", "!"]


def quality_flags(body: str) -> list[str]:
    flags = []
    for b in BANNED:
        if b.lower() in body.lower():
            flags.append(f"banned:{b.strip()}")
    sentences = re.split(r"(?<=[.?])\s+", body.strip())
    if len(sentences) > 5:
        flags.append("too_long")
    if len(body) > 600:
        flags.append("over_600_chars")
    return flags


# ─────────────────────────────── main ──────────────────────────────
async def run(in_csv: str, out_csv: str, offer: str, voice: str):
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    leads = []
    with open(in_csv, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            leads.append(Lead(
                first_name=row.get("first_name", ""),
                last_name=row.get("last_name", ""),
                email=row.get("email", ""),
                company=row.get("company", ""),
                role=row.get("role", ""),
                linkedin_url=row.get("linkedin_url", ""),
                website=row.get("website", ""),
            ))

    async with httpx.AsyncClient(http2=True) as http:
        results = []
        for i, lead in enumerate(leads):
            try:
                research = await research_lead(http, lead)
                hook = pick_hook(client, lead, research)
                em = generate_email(client, lead, hook, offer, voice)
                flags = quality_flags(em["body"])
                results.append({
                    **asdict(lead),
                    "subject": em["subject"],
                    "body": em["body"],
                    "hook_type": hook.type,
                    "hook_text": hook.text,
                    "quality_flags": ";".join(flags),
                })
                print(f"[{i+1}/{len(leads)}] {lead.email} — {hook.type} — "
                      f"{'OK' if not flags else 'FLAGS: ' + ','.join(flags)}")
            except Exception as e:
                print(f"[{i+1}/{len(leads)}] {lead.email} — ERROR: {e}",
                      file=sys.stderr)

    if results:
        keys = list(results[0].keys())
        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(results)
        print(f"\nWrote {len(results)} rows → {out_csv}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_csv", required=True)
    ap.add_argument("--out", dest="out_csv", default="out.csv")
    ap.add_argument("--offer", required=True)
    ap.add_argument("--voice", required=True)
    args = ap.parse_args()
    offer = Path(args.offer).read_text(encoding="utf-8")
    voice = Path(args.voice).read_text(encoding="utf-8")
    asyncio.run(run(args.in_csv, args.out_csv, offer, voice))


if __name__ == "__main__":
    main()
