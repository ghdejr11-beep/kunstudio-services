"""
Sales Q&A Bot — KunStudio
=========================

FastAPI server. Embed the included widget.html in your site.

Endpoints:
    POST /index     — re-index source docs (admin)
    POST /ask       — chat endpoint (called by widget)
    POST /capture   — capture email for out-of-scope questions
    GET  /stats     — top questions / gaps

Run:
    pip install fastapi uvicorn anthropic sentence-transformers faiss-cpu
    python server.py
"""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

import faiss
import numpy as np
import uvicorn
from anthropic import Anthropic
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

MODEL = "claude-sonnet-4-7"
EMBED_MODEL = "BAAI/bge-m3"
DB_PATH = Path("salesqa.db")
INDEX_PATH = Path("salesqa.faiss")
CHUNKS_PATH = Path("salesqa_chunks.json")

app = FastAPI(title="KunStudio Sales Q&A Bot")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_anthropic: Anthropic | None = None
_embedder: SentenceTransformer | None = None
_index: faiss.Index | None = None
_chunks: list[dict] = []


def init_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""CREATE TABLE IF NOT EXISTS questions
        (ts TEXT, question TEXT, answered INT, sources TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS captures
        (ts TEXT, email TEXT, question TEXT, transcript TEXT)""")
    con.commit()
    con.close()


def load():
    global _anthropic, _embedder, _index, _chunks
    _anthropic = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    _embedder = SentenceTransformer(EMBED_MODEL)
    if INDEX_PATH.exists():
        _index = faiss.read_index(str(INDEX_PATH))
        _chunks = json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))
    init_db()


# ────────────────────────────── indexer ──────────────────────────────
class IndexRequest(BaseModel):
    docs: list[dict]    # [{"id": str, "url": str, "title": str, "text": str}]


@app.post("/index")
def reindex(req: IndexRequest):
    global _index, _chunks
    chunks = []
    for d in req.docs:
        for i, chunk in enumerate(_chunk_text(d["text"], 800, 200)):
            chunks.append({
                "id": f"{d['id']}#c{i}",
                "url": d["url"],
                "title": d["title"],
                "text": chunk,
            })
    embeddings = _embedder.encode([c["text"] for c in chunks],
                                   convert_to_numpy=True, normalize_embeddings=True)
    idx = faiss.IndexFlatIP(embeddings.shape[1])
    idx.add(embeddings.astype("float32"))
    faiss.write_index(idx, str(INDEX_PATH))
    CHUNKS_PATH.write_text(json.dumps(chunks, ensure_ascii=False), encoding="utf-8")
    _index, _chunks = idx, chunks
    return {"indexed": len(chunks)}


def _chunk_text(text: str, size: int, overlap: int) -> list[str]:
    out = []
    i = 0
    while i < len(text):
        out.append(text[i : i + size])
        i += size - overlap
    return out


# ────────────────────────────── ask ──────────────────────────────
class AskRequest(BaseModel):
    question: str
    session_id: str = ""


@app.post("/ask")
def ask(req: AskRequest):
    q_emb = _embedder.encode([req.question], convert_to_numpy=True,
                              normalize_embeddings=True).astype("float32")
    scores, idxs = _index.search(q_emb, k=5)
    retrieved = [_chunks[i] for i in idxs[0] if i >= 0]
    top_score = float(scores[0][0]) if len(scores[0]) else 0.0

    # Threshold: refuse if no good source
    if top_score < 0.35:
        _log_question(req.question, answered=0, sources=[])
        return {
            "answer": "I don't have a confident answer for that in our docs — want me to "
                      "forward this question to our team and they'll reply by email?",
            "out_of_scope": True,
            "sources": [],
        }

    context = "\n\n---\n\n".join(
        f"[{c['title']}]({c['url']})\n{c['text']}" for c in retrieved)
    sys = (
        "You answer prospect questions about our product. Rules:\n"
        "- Use ONLY the provided sources. Never invent facts.\n"
        "- 1–3 sentences. Plain language.\n"
        "- End with one citation in this format: [title](url)\n"
        "- If the sources don't answer the question, say: \"I don't have that in our docs.\""
    )
    r = _anthropic.messages.create(
        model=MODEL, max_tokens=350, system=sys,
        messages=[{"role": "user",
                   "content": f"Question: {req.question}\n\nSources:\n{context}"}])
    answer = r.content[0].text.strip()
    _log_question(req.question, answered=1, sources=[c["url"] for c in retrieved])
    return {
        "answer": answer,
        "out_of_scope": "i don't have" in answer.lower(),
        "sources": [{"title": c["title"], "url": c["url"]} for c in retrieved[:3]],
    }


# ────────────────────────────── capture ──────────────────────────────
class CaptureRequest(BaseModel):
    email: str
    question: str
    transcript: str = ""


@app.post("/capture")
def capture(req: CaptureRequest):
    con = sqlite3.connect(DB_PATH)
    from datetime import datetime
    con.execute("INSERT INTO captures VALUES (?,?,?,?)",
                (datetime.utcnow().isoformat(), req.email, req.question, req.transcript))
    con.commit()
    con.close()
    # TODO: forward to Slack/email
    return {"ok": True}


@app.get("/stats")
def stats():
    con = sqlite3.connect(DB_PATH)
    rows = con.execute("""SELECT question, COUNT(*) c, SUM(answered) a
                          FROM questions GROUP BY question
                          ORDER BY c DESC LIMIT 20""").fetchall()
    con.close()
    return {"top_questions": [{"question": q, "count": c, "answered": a} for q, c, a in rows]}


def _log_question(q: str, answered: int, sources: list[str]):
    con = sqlite3.connect(DB_PATH)
    from datetime import datetime
    con.execute("INSERT INTO questions VALUES (?,?,?,?)",
                (datetime.utcnow().isoformat(), q, answered, ",".join(sources)))
    con.commit()
    con.close()


# ────────────────────────────── main ──────────────────────────────
if __name__ == "__main__":
    load()
    uvicorn.run(app, host="0.0.0.0", port=8080)
