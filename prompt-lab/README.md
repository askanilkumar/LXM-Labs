# Orbi Prompt Lab - demo kit (UNext LXM)

Same proof-based learning model as the RAG lab: a course page the learner reads, a Streamlit app where the work
happens, and a cohort dashboard. The app issues a **signed proof code** for each stage; the course page checks it
before unlocking the next stage.

## Run it

1. `pip install -r requirements.txt` then `streamlit run app.py`
2. In the sidebar pick a **Model provider**:
   - **OpenAI**: paste a key (or set `OPENAI_API_KEY`), pick a chat model.
   - **Azure AI Foundry**: endpoint (`https://<resource>.openai.azure.com/`), key, and the **deployment name**
     (on Azure the "model" is the name you gave the deployment). Also set "Price this deployment like" so the cost
     columns work. Environment variables: `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`,
     `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_API_VERSION`. Edit the API version if your deployment needs another.
   - **Offline demo** (or no key): a small deterministic toy model, so the whole lab runs with no internet.
3. Open `prompt_lab.html` in a browser. Add `?trainer=1` for presenter shortcuts (insert a demo proof code, reset).
4. Open `dashboard/index.html` (synthetic data; `python dashboard/gen_data.py` regenerates `data.json`).

**Before a client call, run it once with your real key.** Offline scores are a rehearsal: the toy model is not an LLM.
A real model starts higher on the basics, so baselines will differ and the improvement gaps the proofs ask for
(15 / 20 points) are worth checking against your model of choice. Change them in `app.py` and `prompt_lab.html` if needed.

## The scenario

**Orbi** is the AI assistant of **Orbit Corp**'s customer-care team (fictional online store for smart-office gadgets).
It does three jobs badly out of the box, and each mission fixes one by changing the prompt and measuring the result.

| Mission | Job | The failure | The levers |
|---|---|---|---|
| 1 | Reply to an angry customer | Invents policy (24-hour refund, voucher), rambles | Context (`{facts}`), constraints, length limit |
| 2 | Messy message to JSON | Chatty text, wrong keys, wrong types | Output format, exact keys, types, null, a written rule |
| 3 | Sort support tickets | Two-category answers, false-friend words, two-problem tickets, an injected order | Answer-only, definitions, house rule, delimiters, few-shot examples |

All scoring is plain Python (`lab/scoring.py`), not an LLM judge: the same output always gets the same score.

## The stages

| Stage | Course page | Streamlit tab | Proof requires |
|---|---|---|---|
| 1 | Anatomy of a prompt | 1 · Anatomy | 3/3 checkpoint |
| 2 | Mission 1: clarity, context, constraints | 2 · Mission 1 | baseline run, best score ≥ 70, beats baseline by ≥ 15, ≥ 2 runs |
| 3 | Mission 2: structured output | 3 · Mission 2 | baseline run, best score ≥ 70, beats baseline by ≥ 20, ≥ 2 runs |
| 4 | Mission 3: examples, rules, injection | 4 · Mission 3 | baseline run, accuracy ≥ 75%, beats baseline by ≥ 20 pts, ≥ 2 examples |
| 5 | Evals, cost, production readiness | 5 · Evals & cost | 3/3 checkpoint and ≥ 4 scored runs (bonus: live model face-off) |
| 6 | Stretch (Diamond) | 4 · Mission 3, bottom | hidden-test accuracy ≥ 90%, prompt ≤ 240 est. tokens, 0 ambiguous outputs |

The stretch cannot be cleared by piling everything into the prompt: the token budget forces the learner to choose
which definitions, rules and examples earn their place. Tiers: Bronze (1 stage), Silver (3), Gold (5), Diamond
(Gold + stretch within 150 minutes).

## Layout

```
app.py                  the five tabs and the proof-code generator
lab/data.py             the scenario: email, policy, 5 messages, label set, 20 example pool, 12 dev + 12 hidden tickets
lab/scoring.py          rubric (Mission 1), JSON field scoring (Mission 2), one-label scoring (Mission 3), token estimate
lab/missions.py         renders a prompt, runs it on a mission (thread pool for live calls), scores it
lab/llm.py              OpenAI / Azure AI Foundry / offline, with a token, cost and latency log
lab/offline.py          the deterministic toy model (reads the prompt literally; NOT an LLM)
lab/config.py           providers, model names, prices (edit when pricing changes)
prompt_lab.html         the course page: learn, quiz, scenarios, proof validation, XP and tiers
dashboard/              cohort dashboard (synthetic data)
tests/                  smoke_test.py (scoring + fake OpenAI/Azure clients), journey.py (full run through the app)
```

Add your own tickets in `lab/data.py` (`M3_POOL`, `M3_DEV`, `M3_HIDDEN`). Restart the app after editing.

## Notes

- Proof codes are SHA-256 signed with a shared salt: **tamper-evident, not tamper-proof**, and bound to the learner's
  name, the stage and the unlock time. The hidden tickets are in `lab/data.py`, so a determined learner can read them.
  For production, sign server-side and keep the hidden set on the server.
- Prompt size is an estimate (characters ÷ 4); the cost columns use the real token counts the API returns.
- The offline toy model ignores prompt wording it does not recognise. That is the point: it only improves when the
  prompt gets better in the ways the missions teach.
