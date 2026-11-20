# AskIT Advanced RAG Lab

Six stages on retrieval-augmented generation, built around an IT helpdesk assistant that fails an
audit three different ways. Full philosophy, setup and walkthrough: see the [root README](../README.md).
Answer key for trainers: [TRAINER_GUIDE.md](../TRAINER_GUIDE.md).

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py          # then open rag_lab.html in a browser
```

Leave the OpenAI key box empty to run **fully offline** — hashed embeddings and extractive answers.
Every stage still completes; the numbers are just weaker. No key means no cost and nothing to fail
on a locked-down network.

## The scenario

**AskIT** answers from 23 knowledge-base articles belonging to **Orbit Corp** (fictional). Three
failures are planted in that knowledge base on purpose:

| Problem | How it is planted | Fixed in |
|---|---|---|
| Stale answer | `KB-001` and `KB-004` each have a superseded v1 that contradicts v2 | Stage 3 — metadata filter |
| Wrong audience | `KB-005` is contractor-only, `KB-021` is employee-only | Stage 3 — audience filter |
| Prompt injection | `sample_uploads/KB-099_..._POISONED.md` hides instructions aimed at the model | Stage 2 — ingest scan, Stage 3 — prompt rule 6 |

The sidebar **Preset** switches the controls on one at a time: Baseline (naive RAG) → + Metadata
filter → + Section chunks + hybrid → FDE-grade. Running all four in the Evals tab is the central
exercise — it turns "this feels better" into a table.

## Layout

```
app.py              five tabs and the proof-code generator
rag/ingest.py       front-matter parsing, chunking, injection scan, uploads (md/txt/pdf/docx)
rag/pipeline.py     metadata filter, BM25/vector/hybrid+RRF, rerank, abstain guard, grounded generation
rag/evals.py        golden set (15 questions), metrics, optional LLM-as-judge, run history
rag/llm.py          OpenAI or offline, with a disk cache and a token/cost/latency log
rag/diagram.py      the architecture SVG, drawn live from your sidebar settings
rag/config.py       model names and prices — edit when pricing changes
data/kb/            the 23 Orbit Corp articles, markdown with front-matter metadata
sample_uploads/     one clean new article, one poisoned one
rag_lab.html        the course page
dashboard/          cohort dashboard (sample data)
DEMO_SCRIPT.md      15-minute client demo runbook
```

Add your own golden questions in `MY_QUESTIONS` at the top of `rag/evals.py`, then restart the app.
