"""
Email Triage Bot — KunStudio
============================

Polls a Gmail inbox, classifies unread threads (P0/P1/P2/P3),
drafts replies in the user's voice, and saves them as Gmail Drafts.
Never auto-sends.

Run:
    python main.py --once          # single pass (cron)
    python main.py --serve         # APScheduler daemon

Env vars (.env):
    ANTHROPIC_API_KEY=sk-ant-...
    GOOGLE_CREDENTIALS_PATH=./credentials.json
    GOOGLE_TOKEN_PATH=./token.json
    USER_EMAIL=client@example.com
    VOICE_SAMPLES_PATH=./voice_samples.txt   # ~50 past sent emails, concatenated
    DIGEST_SLACK_WEBHOOK=                    # optional
"""
from __future__ import annotations

import argparse
import base64
import json
import os
from dataclasses import dataclass
from email.mime.text import MIMEText
from pathlib import Path
from typing import Literal

from anthropic import Anthropic
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]
Priority = Literal["P0", "P1", "P2", "P3"]
TRIAGE_MODEL = "claude-sonnet-4-7"
DRAFT_MODEL = "claude-opus-4-7"


# ─────────────────────────────  Gmail helpers  ─────────────────────────────
def gmail_service():
    token_path = Path(os.environ["GOOGLE_TOKEN_PATH"])
    creds_path = Path(os.environ["GOOGLE_CREDENTIALS_PATH"])
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def fetch_unread(svc, max_results: int = 25) -> list[dict]:
    res = svc.users().messages().list(
        userId="me", q="is:unread -category:promotions", maxResults=max_results
    ).execute()
    out = []
    for m in res.get("messages", []):
        msg = svc.users().messages().get(userId="me", id=m["id"], format="full").execute()
        out.append(msg)
    return out


def extract(msg: dict) -> dict:
    headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
    body = ""
    payload = msg["payload"]
    if "parts" in payload:
        for p in payload["parts"]:
            if p["mimeType"] == "text/plain" and p["body"].get("data"):
                body += base64.urlsafe_b64decode(p["body"]["data"]).decode("utf-8", "ignore")
    elif payload["body"].get("data"):
        body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", "ignore")
    return {
        "id": msg["id"],
        "thread_id": msg["threadId"],
        "from": headers.get("From", ""),
        "subject": headers.get("Subject", ""),
        "snippet": msg.get("snippet", ""),
        "body": body[:4000],
    }


# ──────────────────────────  Claude triage + draft  ─────────────────────────
@dataclass
class Triage:
    priority: Priority
    reason: str
    needs_reply: bool


def classify(client: Anthropic, mail: dict) -> Triage:
    sys = (
        "You triage inbound email for a busy founder. Classify into:\n"
        "P0 = money/customer-blocking/legal/security — escalate now\n"
        "P1 = sales/partnership/warm intro — reply today\n"
        "P2 = newsletter/FYI/notification — archive or summarize\n"
        "P3 = cold/spam/promotional — auto-archive\n"
        "Return strict JSON: {priority, reason, needs_reply}."
    )
    user = f"From: {mail['from']}\nSubject: {mail['subject']}\n\n{mail['body'][:1500]}"
    r = client.messages.create(
        model=TRIAGE_MODEL,
        max_tokens=200,
        system=sys,
        messages=[{"role": "user", "content": user}],
    )
    text = r.content[0].text.strip()
    text = text[text.find("{") : text.rfind("}") + 1]
    data = json.loads(text)
    return Triage(data["priority"], data["reason"], bool(data["needs_reply"]))


def draft_reply(client: Anthropic, mail: dict, voice_samples: str) -> str:
    sys = (
        "You draft email replies that match the user's voice exactly. "
        "Study these past sent emails to match tone, signature, hedging, length:\n\n"
        f"{voice_samples[:8000]}\n\n"
        "Keep replies short (≤120 words). Never invent facts. If unsure, ask."
    )
    user = (
        f"Draft a reply to:\n\nFrom: {mail['from']}\nSubject: {mail['subject']}\n\n"
        f"{mail['body'][:2000]}"
    )
    r = client.messages.create(
        model=DRAFT_MODEL,
        max_tokens=600,
        system=sys,
        messages=[{"role": "user", "content": user}],
    )
    return r.content[0].text.strip()


def save_draft(svc, mail: dict, body: str) -> str:
    msg = MIMEText(body)
    msg["to"] = mail["from"]
    msg["subject"] = "Re: " + mail["subject"].lstrip("Re: ")
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    draft = svc.users().drafts().create(
        userId="me",
        body={"message": {"raw": raw, "threadId": mail["thread_id"]}},
    ).execute()
    return draft["id"]


# ─────────────────────────────────  main  ──────────────────────────────────
def run_once():
    svc = gmail_service()
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    voice = Path(os.environ.get("VOICE_SAMPLES_PATH", "voice_samples.txt"))
    voice_samples = voice.read_text(encoding="utf-8") if voice.exists() else ""

    digest = {"P0": [], "P1": [], "P2": [], "P3": []}
    for msg in fetch_unread(svc):
        mail = extract(msg)
        try:
            t = classify(client, mail)
        except Exception as e:
            print(f"[classify-error] {mail['subject'][:60]}: {e}")
            continue
        digest[t.priority].append({"subject": mail["subject"], "from": mail["from"]})
        if t.needs_reply and t.priority in ("P0", "P1"):
            try:
                body = draft_reply(client, mail, voice_samples)
                draft_id = save_draft(svc, mail, body)
                print(f"[draft-saved] {t.priority} {mail['subject'][:60]} → {draft_id}")
            except Exception as e:
                print(f"[draft-error] {mail['subject'][:60]}: {e}")

    print("\n=== Daily digest ===")
    for p in ("P0", "P1", "P2", "P3"):
        print(f"{p}: {len(digest[p])}")
        for item in digest[p][:5]:
            print(f"  · {item['from'][:40]} — {item['subject'][:70]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--serve", action="store_true")
    args = ap.parse_args()
    if args.serve:
        from apscheduler.schedulers.blocking import BlockingScheduler
        sched = BlockingScheduler()
        sched.add_job(run_once, "interval", minutes=5)
        sched.start()
    else:
        run_once()


if __name__ == "__main__":
    main()
