"""Runs one prompt against one mission and scores the result. Pure functions plus a thread pool: no Streamlit here,
so the whole lab is testable from a terminal (see tests/smoke_test.py)."""
from concurrent.futures import ThreadPoolExecutor

from . import data, scoring


def render(template, **values):
    """Plain placeholder replacement. Not str.format, so JSON braces in a prompt are safe."""
    out = template
    for k, v in values.items():
        out = out.replace("{" + k + "}", v)
    return out


def format_examples(ids):
    pool = {p[0]: p for p in data.M3_POOL}
    return "\n\n".join(f"Ticket: {pool[i][1]}\nCategory: {pool[i][2]}" for i in ids if i in pool)


def _ensure_input(template, name, label):
    """The input is always supplied: if the learner forgot the {placeholder}, it is appended."""
    return template if ("{" + name + "}") in template else template.rstrip() + f"\n\n{label}:\n{{{name}}}"


def _ensure_examples(template, ids):
    if not ids or "{examples}" in template:
        return template
    lines = template.split("\n")
    for i, ln in enumerate(lines):          # put the examples just before the line that holds the ticket
        if "{ticket}" in ln:
            lines.insert(i, "Examples:\n{examples}\n")
            return "\n".join(lines)
    return template.rstrip() + "\n\nExamples:\n{examples}"


# ------------------------------------------------------------------ Mission 1
def m1_prompt(template, email=None, facts=None):
    t = _ensure_input(template, "email", "Customer email")
    return render(t, email=data.M1_EMAIL if email is None else email, facts=data.M1_FACTS if facts is None else facts)


def m1_instruction_tokens(template):
    t = _ensure_input(template, "email", "Customer email")
    return scoring.est_tokens(render(t, email="", facts=data.M1_FACTS))


def run_m1(llm, template, temperature=0.2, op="mission1"):
    prompt = m1_prompt(template)
    text, row = llm.complete(prompt, op=op, task="reply", payload={}, temperature=temperature, max_tokens=400)
    res = scoring.score_reply(text)
    return dict(prompt=prompt, output=text, row=row, tokens=m1_instruction_tokens(template),
                uses_facts="{facts}" in template, **res)


# ------------------------------------------------------------------ Mission 2
def m2_prompt(template, message):
    return render(_ensure_input(template, "message", "Message"), message=message)


def run_m2(llm, template, temperature=0.0, op="mission2", workers=5):
    items = data.M2_MESSAGES

    def one(m):
        prompt = m2_prompt(template, m["text"])
        text, row = llm.complete(prompt, op=op, task="extract", payload={"message": m["text"]},
                                 temperature=temperature, max_tokens=300)
        s = scoring.score_extraction(text, m["expected"])
        return dict(id=m["id"], message=m["text"], expected=m["expected"], prompt=prompt, output=text, row=row, **s)

    rows = _map(one, items, workers if llm.live else 1)
    n = len(rows)
    return dict(items=rows, score=round(100 * sum(r["score"] for r in rows) / n, 1),
                valid_rate=sum(r["valid"] for r in rows) / n,
                null_ok=sum(1 for r in rows if r["expected"]["order_id"] is None and r["fields"]["order_id"]),
                tokens=scoring.est_tokens(render(_ensure_input(template, "message", "Message"), message="")),
                **_totals(rows))


# ------------------------------------------------------------------ Mission 3
def m3_template(template, ids):
    t = _ensure_input(template, "ticket", "Ticket")
    return _ensure_examples(t, ids)


def m3_prompt(template, ids, ticket):
    return render(m3_template(template, ids), examples=format_examples(ids), ticket=ticket)


def m3_instruction_tokens(template, ids):
    return scoring.est_tokens(m3_prompt(template, ids, ""))


def run_m3(llm, template, ids, dataset=None, temperature=0.0, op="mission3", workers=6):
    dataset = dataset or data.M3_DEV

    def one(item):
        tid, text, expected = item
        prompt = m3_prompt(template, ids, text)
        out, row = llm.complete(prompt, op=op, task="classify", payload={"ticket": text},
                                temperature=temperature, max_tokens=60)
        s = scoring.score_ticket(out, expected)
        return dict(id=tid, ticket=text, expected=expected, output=out, row=row, **s)

    rows = _map(one, dataset, workers if llm.live else 1)
    n = len(rows)
    inj = [r for r in rows if "ignore" in r["ticket"].lower() or "disregard" in r["ticket"].lower()]
    return dict(items=rows, acc=sum(r["correct"] for r in rows) / n, n=n,
                amb=sum(r["ambiguous"] for r in rows),
                inj_ok=bool(inj) and all(r["correct"] for r in inj),
                tokens=m3_instruction_tokens(template, ids), n_examples=len(ids),
                sample_prompt=m3_prompt(template, ids, dataset[0][1]), **_totals(rows))


# ------------------------------------------------------------------ helpers
def _map(fn, items, workers):
    if workers <= 1:
        return [fn(i) for i in items]
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(fn, items))


def _totals(rows):
    return dict(tin=sum(r["row"]["input_tokens"] for r in rows), tout=sum(r["row"]["output_tokens"] for r in rows),
                cost=sum(r["row"]["cost_usd"] for r in rows),
                latency_ms=int(sum(r["row"]["latency_ms"] for r in rows) / max(1, len(rows))))
