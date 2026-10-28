"""Minimal hybrid RAG: BM25 + dense embeddings, RRF fusion, optional rerank,
abstention when evidence is weak, and answers with citations.

Usage:
    python rag.py "Why does a hot module produce less power?"
    python rag.py "Who won the 2010 World Cup?"      # should abstain

Optional LLM (any OpenAI-compatible endpoint). Without it, the script returns the
retrieved passages with citations (extractive answer):
    export LLM_BASE_URL=https://api.openai.com/v1  LLM_API_KEY=...  LLM_MODEL=...
"""
import math
import os
import re
import sys
from collections import Counter

import numpy as np

EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")
RERANK_MODEL = os.getenv("RERANK_MODEL", "")  # e.g. BAAI/bge-reranker-base; empty = skip
ABSTAIN_BELOW = float(os.getenv("ABSTAIN_BELOW", "0.57"))  # min cosine of best chunk
RRF_K = 60


# ---------- 1. chunking: one chunk per "## " section ----------
def load_chunks(path="corpus.md"):
    text = open(path, encoding="utf-8").read()
    chunks = []
    for block in re.split(r"\n(?=## )", text):
        if block.startswith("## "):
            title, _, body = block.partition("\n")
            chunks.append({"id": len(chunks), "title": title[3:].strip(), "text": body.strip()})
    return chunks


# ---------- 2. sparse side: small BM25 ----------
def tokenize(s):
    return re.findall(r"[a-z0-9]+", s.lower())


class BM25:
    def __init__(self, docs, k1=1.5, b=0.75):
        self.k1, self.b = k1, b
        self.tf = [Counter(tokenize(d)) for d in docs]
        self.len = np.array([sum(t.values()) for t in self.tf], dtype=float)
        self.avg = self.len.mean()
        df = Counter(w for t in self.tf for w in t)
        n = len(docs)
        self.idf = {w: math.log(1 + (n - c + 0.5) / (c + 0.5)) for w, c in df.items()}

    def scores(self, query):
        out = np.zeros(len(self.tf))
        for w in tokenize(query):
            if w not in self.idf:
                continue
            for i, t in enumerate(self.tf):
                f = t.get(w, 0)
                if f:
                    norm = f + self.k1 * (1 - self.b + self.b * self.len[i] / self.avg)
                    out[i] += self.idf[w] * f * (self.k1 + 1) / norm
        return out


# ---------- 3. dense side ----------
def default_embedder():
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(EMBED_MODEL)
    return lambda texts: model.encode(texts, normalize_embeddings=True)


# ---------- 4. index + search ----------
class Index:
    def __init__(self, chunks, embed_fn=None):
        self.chunks = chunks
        self.embed = embed_fn or default_embedder()
        docs = [f"{c['title']}. {c['text']}" for c in chunks]
        self.bm25 = BM25(docs)
        self.vecs = np.asarray(self.embed(docs), dtype=float)
        self.reranker = None
        if RERANK_MODEL:
            from sentence_transformers import CrossEncoder

            self.reranker = CrossEncoder(RERANK_MODEL)

    def search(self, query, k=3):
        """Return (hits, best_cosine). Each hit is a chunk dict."""
        q = np.asarray(self.embed([query]), dtype=float)[0]
        cos = self.vecs @ q
        sparse = self.bm25.scores(query)

        # Reciprocal Rank Fusion of the two rankings
        fused = Counter()
        for scores in (cos, sparse):
            for rank, i in enumerate(np.argsort(-scores)):
                fused[int(i)] += 1.0 / (RRF_K + rank + 1)
        order = [i for i, _ in fused.most_common(max(k * 3, 10))]

        if self.reranker:
            pairs = [(query, self.chunks[i]["text"]) for i in order]
            order = [i for _, i in sorted(zip(self.reranker.predict(pairs), order), reverse=True)]
        return [self.chunks[i] for i in order[:k]], float(cos.max())


# ---------- 5. answer with citations, or abstain ----------
def answer(index, question, k=3):
    hits, best = index.search(question, k)
    if os.getenv("DEBUG"):
        print(f"best cosine: {best:.2f}")
    if best < ABSTAIN_BELOW:
        return "I could not find this in the documents.", []

    cites = [f"[{n}] {h['title']}" for n, h in enumerate(hits, 1)]
    if not os.getenv("LLM_API_KEY"):  # extractive fallback
        body = "\n\n".join(f"[{n}] {h['text']}" for n, h in enumerate(hits, 1))
        return body, cites

    import requests

    context = "\n\n".join(f"[{n}] {h['title']}\n{h['text']}" for n, h in enumerate(hits, 1))
    prompt = (
        "Answer using only the numbered sources. Cite them like [1]. "
        "If the sources do not contain the answer, say so.\n\n"
        f"Sources:\n{context}\n\nQuestion: {question}"
    )
    r = requests.post(
        os.getenv("LLM_BASE_URL", "https://api.openai.com/v1") + "/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['LLM_API_KEY']}"},
        json={"model": os.environ["LLM_MODEL"], "temperature": 0,
              "messages": [{"role": "user", "content": prompt}]},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"], cites


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    idx = Index(load_chunks())
    text, sources = answer(idx, " ".join(sys.argv[1:]))
    print(text)
    if sources:
        print("\nSources:\n" + "\n".join(sources))
