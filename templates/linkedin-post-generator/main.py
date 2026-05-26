"""
LinkedIn Post Generator — KunStudio
===================================

Generates 5 voice-matched LinkedIn posts/week from raw notes.

Run:
    python main.py --notes notes.txt --voice voice_samples.txt
        --topics topics.json --out posts.json --count 5

notes.txt        : your raw notes (one bullet per line)
voice_samples.txt: paste of your last 30 LinkedIn posts (one per double-newline)
topics.json      : ["topic A", "topic B", ...] — your content pillars
out posts.json   : generated posts
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Literal

from anthropic import Anthropic

MODEL = "claude-opus-4-7"

PostFormat = Literal[
    "founder_story",        # "I shipped X. Here's what I learned."
    "contrarian",           # "Everyone says X. I disagree, here's why."
    "how_i_did_it",         # Step-by-step playbook.
    "micro_data",           # "I ran 100 cold emails. 7 replies. Here's the pattern."
    "engagement_question",  # "What's the 1 metric you obsess over?"
]
DEFAULT_MIX: list[PostFormat] = [
    "founder_story",
    "contrarian",
    "how_i_did_it",
    "micro_data",
    "engagement_question",
]


def extract_voice(client: Anthropic, samples: str) -> str:
    sys = (
        "You are a copy analyst. Read the user's past LinkedIn posts and produce a "
        "concise voice card (≤300 words) covering: opening hook style, average length, "
        "use of line breaks, emojis (which / where / how often), hashtag pattern, "
        "characteristic phrases, things they NEVER do. Be specific with examples."
    )
    r = client.messages.create(
        model=MODEL,
        max_tokens=600,
        system=sys,
        messages=[{"role": "user", "content": samples[:18000]}],
    )
    return r.content[0].text.strip()


def generate_post(
    client: Anthropic,
    note: str,
    fmt: PostFormat,
    voice_card: str,
    topic_pillars: list[str],
) -> str:
    sys = (
        "You write LinkedIn posts in the user's exact voice. Voice card:\n\n"
        f"{voice_card}\n\n"
        f"Topic pillars (stay inside these): {', '.join(topic_pillars)}\n\n"
        "Rules:\n"
        "- 100-220 words.\n"
        "- Hook in line 1 (≤8 words ideally).\n"
        "- Plain language. No corporate-speak. No 'In today's world'.\n"
        "- Never invent stats. If a number is needed and absent, omit it.\n"
        "- End with engagement (question OR clear takeaway), not a CTA to DM."
    )
    user = f"Source note:\n{note}\n\nFormat: {fmt}\n\nWrite the post."
    r = client.messages.create(
        model=MODEL,
        max_tokens=800,
        system=sys,
        messages=[{"role": "user", "content": user}],
    )
    return r.content[0].text.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--notes", required=True)
    ap.add_argument("--voice", required=True)
    ap.add_argument("--topics", required=True)
    ap.add_argument("--out", default="posts.json")
    ap.add_argument("--count", type=int, default=5)
    args = ap.parse_args()

    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    notes = [ln.strip() for ln in Path(args.notes).read_text(encoding="utf-8").splitlines() if ln.strip()]
    voice_samples = Path(args.voice).read_text(encoding="utf-8")
    topics = json.loads(Path(args.topics).read_text(encoding="utf-8"))

    print("[1/3] Extracting voice ...")
    voice_card = extract_voice(client, voice_samples)

    print("[2/3] Generating posts ...")
    posts = []
    for i in range(args.count):
        note = notes[i % len(notes)] if notes else "Reflect on this week's shipping."
        fmt = DEFAULT_MIX[i % len(DEFAULT_MIX)]
        body = generate_post(client, note, fmt, voice_card, topics)
        posts.append({"format": fmt, "source_note": note, "body": body})
        print(f"  · {i+1}/{args.count} {fmt}")

    Path(args.out).write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[3/3] Wrote {len(posts)} posts → {args.out}")


if __name__ == "__main__":
    main()
