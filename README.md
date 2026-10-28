# solar-rag

A small, readable reference implementation of a retrieval-augmented generation (RAG) pipeline, in about 150 lines of Python. It answers questions about a short photovoltaic demo corpus, cites its sources, and says "I could not find this" when the documents do not cover the question.

This is a learning and demonstration project. It is not a production system.

## How it works

```
corpus.md --> chunks (one per section)
                 |
   question --> BM25 (sparse) ----\
            \-> embeddings (dense) --> RRF fusion --> optional reranker
                                                         |
                          best cosine < threshold? --> abstain
                                                         |
                                  top chunks --> LLM (or extractive) --> answer + citations
```

| Step | What it does |
|---|---|
| Chunking | One chunk per `##` section of a Markdown file |
| Sparse search | BM25, written in 20 lines, no extra dependency |
| Dense search | Sentence-transformers embeddings (`BAAI/bge-small-en-v1.5` by default) |
| Fusion | Reciprocal Rank Fusion of the two rankings |
| Rerank | Optional cross-encoder, set `RERANK_MODEL` |
| Abstention | If the best cosine similarity is below `ABSTAIN_BELOW`, no answer is generated |
| Generation | Any OpenAI-compatible endpoint; without a key it returns the retrieved passages |

## Run

```bash
pip install -r requirements.txt
python rag.py "Why does a hot module produce less power?"
python rag.py "Who won the 2010 World Cup?"     # abstains
python eval.py                                   # hit rate, MRR, abstention
```

To generate written answers, set `LLM_BASE_URL`, `LLM_API_KEY` and `LLM_MODEL`.

## Evaluation

`eval.py` holds 9 hand-written questions: 7 with a known source section and 2 out of scope. It reports hit rate@3, MRR and how many out-of-scope questions were refused. The set is tiny on purpose; it shows the method, not a benchmark.

Result with `BAAI/bge-small-en-v1.5` and `ABSTAIN_BELOW=0.57`:

| Metric | Value |
|---|---|
| hit@3 | 7/7 |
| MRR | 1.00 |
| Out-of-scope refused | 2/2 |

The threshold sits between the highest cosine of an off-topic question (0.45) and the lowest of an answerable one (0.69), measured on 8 sample questions. Recalibrate it for your own corpus and model.

## Limits

- The corpus is eight short notes written for this demo. Results on it say little about real document collections.
- Chunking by section works for clean Markdown. PDFs, tables and figures need a real conversion step.
- It answers only what the corpus defines. A term that is merely mentioned in passing, without a definition, gives weak answers.
- The abstention threshold depends on the embedding model and must be calibrated on your own questions. The default is a starting point.
- The index lives in memory and is rebuilt on every start. For large collections use a vector database.
- No access control, no caching, no logging.

## Ideas to extend

Vector store with named dense and sparse vectors, PDF conversion, a structured metadata filter, a larger labelled question set, LLM answer grading.

## License

MIT
