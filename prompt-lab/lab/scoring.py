"""Scoring for the three missions. All checks are plain Python (no LLM judge), so the same output always
gets the same score, whichever model produced it."""
import json
import re

from .data import (LABELS, LABEL_ALIASES, M1_MAX_WORDS, M1_RUBRIC, M2_FIELDS)


def est_tokens(text):
    """Rough token estimate (chars / 4). Good enough to compare prompts; the API reports the real count."""
    return max(1, round(len(text or "") / 4))


def word_count(text):
    return len(re.findall(r"\S+", text or ""))


# ------------------------------------------------------------------ Mission 1
_NEGATORS = re.compile(r"(cannot|can't|can not|unable|not able|don't|do not|won't|no |not |without|unfortunately)", re.I)
_FORBIDDEN = ["24 hours", "24 hrs", "same day", "same-day", "right away", "immediately", "instantly", "compensation",
              "discount", "voucher", "coupon", "gift", "store credit", "extra credit", "free upgrade", "refund today",
              "today refund", "refunded today", "by tomorrow", "tomorrow", "within the hour", "% off", "bonus"]


def _invented_promises(text):
    t = (text or "").lower()
    found = []
    for term in _FORBIDDEN:
        for m in re.finditer(re.escape(term), t):
            before = t[max(0, m.start() - 45):m.start()]
            if not _NEGATORS.search(before):          # "we cannot offer compensation" is fine
                found.append(term)
                break
    return found


def score_reply(text):
    t = text or ""
    low = t.lower()
    results = {
        "apology": bool(re.search(r"\b(sorry|apolog|regret)|understand (how|your|that).{0,30}frustrat", low)),
        "name": "priya" in low,
        "order": "oc-48213" in low,
        "timeline": bool(re.search(r"\b5\s*(?:-|–|—|to)\s*7\s*(?:business|working)?\s*days", low)),
        "options": bool(re.search(r"replacement|replace", low)) and bool(re.search(r"pick[\s-]?up|collect", low)),
        "nopromise": not _invented_promises(t),
        "length": 0 < word_count(t) <= M1_MAX_WORDS,
    }
    checks = [dict(key=k, label=lbl, points=pts, passed=bool(results[k])) for k, lbl, pts in M1_RUBRIC]
    score = sum(c["points"] for c in checks if c["passed"])
    return dict(score=score, checks=checks, words=word_count(t), promises=_invented_promises(t))


# ------------------------------------------------------------------ Mission 2
def parse_json_output(text):
    """Accepts bare JSON or JSON inside a ```json fence. Any chatter around it makes it invalid on purpose:
    a downstream system cannot parse 'Sure! Here is your JSON'."""
    t = (text or "").strip()
    m = re.fullmatch(r"```(?:json|JSON)?\s*(.*?)\s*```", t, re.S)
    if m:
        t = m.group(1).strip()
    try:
        obj = json.loads(t)
    except ValueError:
        return None
    return obj if isinstance(obj, dict) else None


def _norm_item(s):
    s = re.sub(r"[^a-z0-9\- ]", "", str(s or "").lower()).strip()
    s = re.sub(r"^orbit\s+", "", s)
    words = [re.sub(r"s$", "", w) if len(w) > 3 else w for w in s.split()]
    return " ".join(words)


def _field_ok(field, got, want):
    if field == "order_id":
        if want is None:
            return got is None
        return isinstance(got, str) and got.strip().upper() == want
    if field == "quantity":
        if isinstance(got, bool):
            return False
        if isinstance(got, (int, float)):
            return int(got) == want and float(got).is_integer()
        return isinstance(got, str) and got.strip().isdigit() and int(got.strip()) == want
    if field == "item":
        return _norm_item(got) == _norm_item(want)
    if field == "urgency":
        return isinstance(got, str) and got.strip().lower() == want
    return isinstance(got, str) and got.strip().lower() == str(want).lower()    # customer_name


def score_extraction(text, expected):
    obj = parse_json_output(text)
    if obj is None:
        return dict(valid=False, score=0.0, fields={f: False for f in M2_FIELDS}, got=None)
    fields = {f: _field_ok(f, obj.get(f), expected[f]) if f in obj else False for f in M2_FIELDS}
    return dict(valid=True, score=sum(fields.values()) / len(M2_FIELDS), fields=fields, got=obj)


# ------------------------------------------------------------------ Mission 3
def labels_in(text):
    low = (text or "").lower()
    found = []
    for label in LABELS:
        if any(re.search(r"\b" + re.escape(a) + r"\b", low) for a in LABEL_ALIASES[label]):
            found.append(label)
    return found


def score_ticket(text, expected):
    found = labels_in(text)
    if len(found) == 1:
        return dict(pred=found[0], correct=found[0] == expected, ambiguous=False)
    return dict(pred=" / ".join(found) if found else "(no label)", correct=False, ambiguous=True)
