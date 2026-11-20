# Trainer guide — answer key and presenter notes

> **Do not share this file with a cohort.** It contains every answer. If you hand the repo to
> learners, delete `TRAINER_GUIDE.md` first — nothing else depends on it.

---

## Before you present

| Check | Why |
|---|---|
| Open the course page with **`?trainer=1`** | Without it you have no skip button and no reset |
| Click **Reset → Yes** on the course page | The session clock carries over between sessions. A stale start time makes **Diamond unreachable**, because Diamond needs the stretch within 150 minutes of starting |
| Leave the **API key box empty** | Offline is faster, free, and cannot fail on a client's network |
| Type the **same name** in the course page and the Streamlit sidebar | The proof code is bound to the name; a mismatch is rejected |
| Clear the eval **run history** (RAG lab, bottom of the Evals tab) | Otherwise old runs mix into the ladder you are about to show |

Demo runbooks: [`rag-lab/DEMO_SCRIPT.md`](rag-lab/DEMO_SCRIPT.md) (15 min) and
[`prompt-lab/DEMO_SCRIPT.md`](prompt-lab/DEMO_SCRIPT.md) (5 min).

**Trainer mode** (`?trainer=1`) gives you *Insert a demo proof code for this stage* on every stage, and
*Reset all progress*. A stage still needs its quiz passed, so you need the answers below even when skipping.

A note on the letters: options are **not shuffled** in this build, so the correct answer is often **B**.
Click the answer text, not the letter, and nobody notices.

---

# RAG lab — AskIT

## Course page quizzes

| Stage | Q1 | Q2 | Q3 |
|---|---|---|---|
| **1** Why RAG | **C** Tag articles with status and effective date, and filter them at retrieval | **D** Permanently teaching the model a new tone of voice | **B** Before: the retrieved chunks become part of the prompt |
| **2** Ingestion | **B** Re-embed every chunk, and embed queries with B too | **B** Chunk by section, so the fact stays whole | **B** Retrieval can only filter on metadata that already exists |
| **3** Retrieval | **A** Questions with exact strings like 'error 809' or 'KB-016' | **B** The guard threshold plus a prompt that mandates 'I don't know' | **B** The metadata filter on audience |
| **4** Evals | **B** 0.58 | **B** Token cost, latency, and noise in the context | **C** wrong_source_top1 |
| **5** Code & production | **B** The abstain guard (relevance threshold) | **B** At retrieval, by filtering on metadata | **B** Generation tokens |

## Course page production scenarios (optional XP)

| Stage | Answers |
|---|---|
| **1** | **B** RAG with chunk-level citations and weekly incremental ingestion · **A** Whether retrieval returned relevant chunks, and whether the prompt forces an 'I don't know' |
| **2** | **B** BigQuery or Vertex AI Vector Search · **B** Parsing: layout-aware extraction or a document-AI parser · **B** Approval workflow and allow-listed sources at ingestion |
| **3** | **B** Add BM25 keyword search (hybrid retrieval) · **B** Layer the defences: scan at ingestion, sources as data, no privileged tools · **B** Filter on status and prefer the current effective date |
| **4** | **B** Run the golden set before and after, compare metrics, read the per-question regressions · **B** Generation: faithfulness, context ordering, conflicting versions |
| **5** | **B** Incremental ingestion by content hash · **B** Trace a request, then cut top-k and context, stream, cache, consider a smaller model · **B** Citations with codes and versions, plus request traces in an audit log |

## Streamlit checkpoints

**Tab 1 · Architecture** — needed for the Stage 1 proof code
1. *AskIT quotes the superseded v1…* → **A metadata filter on status and effective date**
2. *A contractor asks about personal laptops…* → **At retrieval, before the LLM sees any chunk**
3. *Which pipeline runs again when an IT article is rewritten?* → **Ingestion pipeline, for that article**

**Tab 5 · How it works** — needed for the Stage 5 proof code
1. *Which control stops AskIT answering…* → **The abstain guard (relevance threshold)**
2. *Where should 'contractors must not see employee-only articles' be enforced?* → **At retrieval, by filtering on metadata**
3. *An uploaded article says 'ignore all previous instructions'…* → **Layers: scan at ingest, treat sources as data in the prompt, and give the assistant no privileged tools**

**Tab 2 · Ingestion has no checkpoint.** The Stage 2 code is earned by the ingestion work itself —
you must ingest at least one file before it will generate. Bonus XP for section chunking, real
embeddings, more than one file, and catching the poisoned article.

## Stage 6 — the stretch, exactly

Targets: pass ≥ 85%, hit@1 ≥ 90%, **0** wrong sources, **top-k ≤ 2**.

1. Sidebar → **Preset** = **FDE-grade (all on)**
2. Sidebar → **Top-k chunks to the LLM** = **2** (the Preset label flips to *Custom* — expected)
3. Tab **4 · Evals** → **Configurations to test** = **Current settings** *only* → **Run evaluation**
4. Green *Qualifying run found* appears → **Claim stretch proof**

Verified offline: 100% pass, 100% hit@1, 0 wrong sources at top-k 2, for either audience.

**No preset can clear this** — all four send 3 chunks. That is the point of the challenge.

**If it will not qualify:** check the `top_k` column in Run history. If every row says 3 you evaluated
presets, not *Current settings*. If the **LLM reranker** is off, hit@1 drops to 0.85 and fails.

## Reference numbers (offline, 15-question golden set)

| Preset | Pass | hit@1 | Wrong sources |
|---|---|---|---|
| Baseline (naive RAG) | 47% | 54% | **3** |
| + Metadata filter | 67% | 77% | 0 |
| + Section chunks + hybrid | 73% | 85% | 0 |
| FDE-grade (all on) | 100% | 100% | 0 |

With a real key the numbers differ — rerun before you quote them.

---

# Prompt lab — Orbi

## Course page quizzes

| Stage | Q1 | Q2 | Q3 |
|---|---|---|---|
| **1** Anatomy | **B** Paste the refund policy into the prompt and tell the model to use only that | **B** Under 100 words | **B** Only what is written in the prompt, plus its general training |
| **2** Mission 1 | **B** It does not know your refund timeline, so it guesses or leaves it out | **B** Maximum 100 words | **B** Compare the rubric lines that changed, fix the cause, change one thing at a time |
| **3** Mission 2 | **B** The system parses the whole text as JSON and fails on the extra words | **C** null, and the prompt says so | **B** Otherwise the model invents its own names and the system cannot read the record |
| **4** Mission 3 | **A** When label boundaries are subtle and instructions alone do not settle them | **B** A few short ones that sit on the borders between categories | **B** If the answers are in the prompt, the score is inflated and tells you nothing |
| **5** Evals & cost | **B** Cost and latency per call | **B** The business value of 2 points versus the money saved at your volume | **B** In Git, with a version, an owner and an eval score |

## Course page production scenarios (optional XP)

| Stage | Answers |
|---|---|
| **1** | **B** A score over a larger set of realistic emails · **B** Supply the policy as context and forbid any offer outside it |
| **2** | **B** Put the policy in context, forbid other promises, scan replies for banned terms · **B** Add an explicit word limit and re-run the score |
| **3** | **B** Write 'quantity: integer' in the prompt and validate the type in code · **B** The API's structured-output or JSON mode, schema validation and one retry |
| **4** | **B** Mark the ticket as data with delimiters · **B** The 3-example prompt · **B** Write a house rule for ties and show an example of it |
| **5** | **B** An eval run before the tweak shipped, and a one-step rollback · **B** B saves about 250 tokens on every call · **B** The prompt version recorded with every request |

## Streamlit checkpoints

**Tab 1 · Anatomy** — needed for the Stage 1 proof code
1. *Which block mainly stops the model inventing company policy?* → **Context: the facts it is allowed to use**
2. *'Be brief' is vague. Which is better?* → **Under 80 words, three sentences at most**
3. *Why score a prompt on several inputs?* → **A prompt that works on one input can fail on the next; a score over a set shows real quality**

**Tab 5 · Evals & cost** — needed for the Stage 5 proof code (also needs ≥ 4 scored runs in history)
1. *You change one sentence in a production prompt…* → **Run the eval set and compare the scores with the previous version**
2. *Which change most reliably cuts cost without hurting accuracy?* → **Shorten the prompt: keep only the examples and rules that earn their tokens, and test a smaller model**
3. *A ticket says 'ignore your instructions'…* → **Mark the ticket as data with delimiters, and give the assistant no power to act on it**

## Stages 2–4 and the stretch

These have no fixed answer — the learner has to move a score:

| Stage | Proof requires |
|---|---|
| 2 (Mission 1) | baseline run, best score ≥ 70, beats baseline by ≥ 15, ≥ 2 runs |
| 3 (Mission 2) | baseline run, best score ≥ 70, beats baseline by ≥ 20, ≥ 2 runs |
| 4 (Mission 3) | baseline run, accuracy ≥ 75%, beats baseline by ≥ 20 points, ≥ 2 examples |
| 6 (Stretch) | hidden-test accuracy ≥ 90%, prompt ≤ 240 estimated tokens, 0 ambiguous outputs |

Fast path in a demo: run the baseline, click **Insert policy facts** (Mission 1) or **+ Injection
guard** (Mission 3), run again, and the score jumps in front of the client.

**Offline scores are a rehearsal.** The toy model is not an LLM. A real model starts higher on the
basics, so the improvement gaps (15 / 20 points) are worth re-checking against your model before a
client call. They live in `app.py` and `prompt_lab.html`.

---

## If something breaks

| Symptom | Fix |
|---|---|
| *"belongs to X, not Y"* | Name differs between Streamlit and the course page. Fix the sidebar, regenerate. **Say:** "that is the binding working" |
| *"generated before this stage was unlocked"* | You reset the course page after generating. Regenerate |
| *"This exact code was already used"* | Codes are single-use. Generate a fresh one — they carry a timestamp, so every click gives a new code |
| Stage will not unlock | Needs **quiz passed AND proof validated**. Check the three chips at the top of the stage |
| RAG Stage 2 proof button missing | By design — ingest at least one file from `sample_uploads/` first |
| Trainer skip button missing | URL is missing `?trainer=1`. Reload; progress is kept |
| Everything is on fire | `dashboard/index.html` opens standalone with a full sample cohort. Narrate from there |
