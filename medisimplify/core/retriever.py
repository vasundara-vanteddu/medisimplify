"""Chunking + BM25 retrieval (no embeddings, no vector DB)."""
import re

from rank_bm25 import BM25Plus


def chunk_text(text: str, size: int = 600, overlap: int = 120):
    text = re.sub(r"\n{2,}", "\n", text).strip()
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return chunks


def _tokens(s: str):
    return re.findall(r"\w+", s.lower())


def top_chunks(question: str, chunks, k: int = 4):
    if not chunks:
        return []
    bm25 = BM25Plus([_tokens(c) for c in chunks])
    scores = bm25.get_scores(_tokens(question))
    ranked = sorted(range(len(chunks)), key=lambda i: scores[i], reverse=True)[:k]
    return [chunks[i] for i in sorted(ranked)]
