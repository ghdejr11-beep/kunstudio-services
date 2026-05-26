"""
CRM Follow-up Bot — KunStudio
=============================

Finds stale deals in HubSpot, drafts personalized follow-ups, saves to Gmail Drafts.

Run:
    python main.py --once
    python main.py --serve     # hourly via APScheduler

Env:
    ANTHROPIC_API_KEY=
    HUBSPOT_TOKEN=               # private app token
    GOOGLE_CREDENTIALS_PATH=
    GOOGLE_TOKEN_PATH=
    USER_EMAIL=
    VOICE_SAMPLES_PATH=
    STALE_DAYS=4
    AUTO_SEND=false              # 'true' enables auto-send (warm segment)
"""
from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal

import requests
from anthropic import Anthropic

MODEL = "claude-opus-4-7"
HUBSPOT_BASE = "https://api.hubapi.com"

Angle = Literal["value_add", "case_study", "check_in", "re_engage"]


@dataclass
class Deal:
    id: str
    name: str
    stage: str
    amount: float
    company: str
    contact_email: str
    last_activity: datetime
    notes: str
    last_emails: list[str]


# ────────────────────────────  HubSpot fetch  ────────────────────────────
def hubspot_headers() -> dict:
    return {"Authorization": f"Bearer {os.environ['HUBSPOT_TOKEN']}",
            "Content-Type": "application/json"}


def fetch_stale_deals(stale_days: int = 4) -> list[Deal]:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=stale_days)).isoformat()
    body = {
        "filterGroups": [{"filters": [
            {"propertyName": "hs_lastmodifieddate", "operator": "LT", "value": cutoff},
            {"propertyName": "dealstage", "operator": "NOT_IN",
             "values": ["closedwon", "closedlost"]},
        ]}],
        "properties": ["dealname", "dealstage", "amount", "hs_lastmodifieddate",
                       "notes_last_contacted"],
        "limit": 50,
    }
    r = requests.post(f"{HUBSPOT_BASE}/crm/v3/objects/deals/search",
                      headers=hubspot_headers(), json=body, timeout=20)
    r.raise_for_status()
    out = []
    for d in r.json().get("results", []):
        p = d["properties"]
        out.append(Deal(
            id=d["id"],
            name=p.get("dealname", ""),
            stage=p.get("dealstage", ""),
            amount=float(p.get("amount") or 0),
            company="",
            contact_email="",
            last_activity=datetime.fromisoformat(
                p["hs_lastmodifieddate"].replace("Z", "+00:00")),
            notes=p.get("notes_last_contacted", "") or "",
            last_emails=[],
        ))
    return out


def enrich_deal(deal: Deal) -> Deal:
    """Pull associated contact + last 5 engagements."""
    r = requests.get(
        f"{HUBSPOT_BASE}/crm/v4/objects/deals/{deal.id}/associations/contacts",
        headers=hubspot_headers(), timeout=15)
    contacts = r.json().get("results", [])
    if contacts:
        cid = contacts[0]["toObjectId"]
        cr = requests.get(
            f"{HUBSPOT_BASE}/crm/v3/objects/contacts/{cid}",
            headers=hubspot_headers(),
            params={"properties": "email,company,firstname,lastname"},
            timeout=15)
        cp = cr.json().get("properties", {})
        deal.contact_email = cp.get("email", "")
        deal.company = cp.get("company", "")
    # Engagements (emails)
    eng = requests.get(
        f"{HUBSPOT_BASE}/crm/v3/objects/deals/{deal.id}/associations/emails",
        headers=hubspot_headers(), timeout=15)
    email_ids = [e["id"] for e in eng.json().get("results", [])[:5]]
    for eid in email_ids:
        er = requests.get(f"{HUBSPOT_BASE}/crm/v3/objects/emails/{eid}",
                          headers=hubspot_headers(),
                          params={"properties": "hs_email_text,hs_email_subject"},
                          timeout=15)
        ep = er.json().get("properties", {})
        deal.last_emails.append(
            f"Subj: {ep.get('hs_email_subject','')}\n{ep.get('hs_email_text','')[:1500]}")
    return deal


# ────────────────────────────  Claude angle + draft  ─────────────────────
def pick_angle(client: Anthropic, deal: Deal) -> Angle:
    sys = (
        "Pick the best follow-up angle for a stale sales deal. Options:\n"
        "value_add  = share resource/insight, no ask\n"
        "case_study = relevant customer success\n"
        "check_in   = soft, no-pressure ping\n"
        "re_engage  = clear 'should we kill this?' ask\n"
        "Return ONLY one of those tokens, nothing else."
    )
    context = (
        f"Deal: {deal.name} | Stage: {deal.stage} | ${deal.amount:,.0f}\n"
        f"Days since last activity: {(datetime.now(timezone.utc) - deal.last_activity).days}\n"
        f"Notes: {deal.notes[:1000]}\n"
        f"Last emails:\n" + "\n---\n".join(deal.last_emails[:3])[:3000]
    )
    r = client.messages.create(
        model=MODEL, max_tokens=10, system=sys,
        messages=[{"role": "user", "content": context}],
    )
    token = r.content[0].text.strip().lower()
    return token if token in ("value_add", "case_study", "check_in", "re_engage") else "check_in"


def draft_followup(client: Anthropic, deal: Deal, angle: Angle, voice: str) -> str:
    sys = (
        f"You write follow-up sales emails in this person's voice. Voice samples:\n\n{voice[:6000]}\n\n"
        "Rules:\n"
        "- ≤90 words.\n"
        "- Reference at least one SPECIFIC fact from the deal thread (not generic 'circling back').\n"
        "- Match the chosen angle exactly.\n"
        "- No '!' in subject or body. No 'just'. No 'wanted to'. No 'I hope this finds you well'.\n"
        "- Subject ≤ 8 words, lowercase optional, curiosity > formality."
    )
    user = (
        f"Angle: {angle}\nDeal: {deal.name}, ${deal.amount:,.0f}, stage {deal.stage}\n"
        f"Contact: {deal.contact_email} @ {deal.company}\n"
        f"Days stale: {(datetime.now(timezone.utc) - deal.last_activity).days}\n"
        f"Notes: {deal.notes[:1200]}\n"
        f"Recent thread:\n{chr(10).join(deal.last_emails[:3])[:4000]}\n\n"
        "Output:\nSubject: <subject>\n\n<body>"
    )
    r = client.messages.create(model=MODEL, max_tokens=500, system=sys,
                               messages=[{"role": "user", "content": user}])
    return r.content[0].text.strip()


# ─────────────────────────────────  main  ───────────────────────────────
def run_once():
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    voice_path = Path(os.environ.get("VOICE_SAMPLES_PATH", "voice_samples.txt"))
    voice = voice_path.read_text(encoding="utf-8") if voice_path.exists() else ""
    stale_days = int(os.environ.get("STALE_DAYS", "4"))

    deals = fetch_stale_deals(stale_days)
    print(f"Found {len(deals)} stale deals")
    for d in deals:
        if d.amount < 500:    # skip tiny deals
            continue
        try:
            d = enrich_deal(d)
            if not d.contact_email:
                continue
            angle = pick_angle(client, d)
            draft = draft_followup(client, d, angle, voice)
            print(f"\n=== {d.name} (${d.amount:,.0f}) — {angle} ===")
            print(draft)
            # TODO: save to Gmail Drafts (see email-triage-bot/main.py save_draft())
            # TODO: log to HubSpot engagements
        except Exception as e:
            print(f"[error] {d.name}: {e}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--serve", action="store_true")
    args = ap.parse_args()
    if args.serve:
        from apscheduler.schedulers.blocking import BlockingScheduler
        sched = BlockingScheduler()
        sched.add_job(run_once, "interval", hours=1)
        sched.start()
    else:
        run_once()


if __name__ == "__main__":
    main()
