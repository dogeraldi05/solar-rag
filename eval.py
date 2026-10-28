"""Tiny evaluation: retrieval hit-rate@k, MRR, and abstention on out-of-scope questions.

    python eval.py
"""
from rag import Index, answer, load_chunks

# (question, expected section title). None = out of scope, system should abstain.
CASES = [
    ("Why does a hot module produce less power?", "Temperature effect"),
    ("What does a performance ratio of 80 percent mean?", "Performance ratio"),
    ("How can dust on panels be detected in the data?", "Soiling"),
    ("Why would a designer use a DC to AC ratio above 1?", "Inverter clipping"),
    ("How much power does a module lose per year?", "Degradation"),
    ("Do I get credit for energy I send to the grid?", "Net metering and distributed generation"),
    ("What happens to the inverter when the grid goes down?", "Grid connection and protection"),
    ("Who won the football world cup in 2010?", None),
    ("What is the best recipe for chocolate cake?", None),
]


def run(k=3, embed_fn=None):
    idx = Index(load_chunks(), embed_fn)
    in_scope = [(q, t) for q, t in CASES if t]
    out_scope = [q for q, t in CASES if not t]

    hits = rr = 0
    for q, title in in_scope:
        titles = [h["title"] for h in idx.search(q, k)[0]]
        if title in titles:
            hits += 1
            rr += 1 / (titles.index(title) + 1)
    abstained = sum(answer(idx, q, k)[1] == [] for q in out_scope)

    print(f"hit@{k}:    {hits}/{len(in_scope)}")
    print(f"MRR:       {rr / len(in_scope):.2f}")
    print(f"abstained: {abstained}/{len(out_scope)} out-of-scope questions")
    return hits, len(in_scope), abstained, len(out_scope)


if __name__ == "__main__":
    run()
