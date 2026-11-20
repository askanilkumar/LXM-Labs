"""Offline stand-in for a language model ("offline-toy").

This is NOT an LLM. It is a small, deterministic, literal-minded program that reads the prompt it is given and
behaves like a careless-but-willing intern: it only uses facts that are in the prompt, it does not know your
output format unless you state it, and it follows explicit rules it can recognise. That makes the lab runnable
with no API key and lets the numbers move when (and only when) the prompt gets better.
With a real model the same prompts behave differently, usually better at the basics and still wrong in the ways
the missions teach. Treat offline scores as a rehearsal, not as a benchmark."""
import json
import re

from .data import LABELS, LABEL_HELP

# ----------------------------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------------------------
_STOP = set("""a an the and or but if so of to in on at for from with by is are was were be been it its this that these
those i me my we our you your they their he she him her as not no do does did have has had can could would should will
just very really also still now then than when where which who what how why please thanks thank hi hello team there
here again anymore any all some more most""".split())


def _stem(w):
    if len(w) > 5 and w.endswith("ing"):
        w = w[:-3]
    elif len(w) > 4 and w.endswith("ed"):
        w = w[:-2]
    elif len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
        w = w[:-1]
    if len(w) > 4 and w.endswith("e"):      # charge / charged / charges -> charg
        w = w[:-1]
    return w


def _tokens(text):
    ws = re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", (text or "").lower())
    return {_stem(w) for w in ws if w not in _STOP and len(w) > 1}


_DOMAIN = {_stem(w) for w in "lamp app orbit order monitor webcam dock desk chair product device item stand new time one two".split()}


def _words(text):
    return len(re.findall(r"\S+", text or ""))


# ----------------------------------------------------------------------------------------------
# Mission 1: reply
# ----------------------------------------------------------------------------------------------
_RESTRICT = re.compile(
    r"\b(only|just)\b[^.\n]{0,50}\b(facts?|policy|information|sheet|provided|given)\b"
    r"|\b(do not|don't|never|must not|mustn't|without)\b[^.\n]{0,40}\b(promise|invent|make up|offer|guarantee|extra|add)\b"
    r"|\bstick to\b|\bnothing (else|beyond|outside)\b", re.I)
_LIMIT = re.compile(
    r"(?:under|within|max(?:imum)?(?: of)?|at most|no more than|less than|up to|below|fewer than)\s*(\d{2,3})\s*words"
    r"|(\d{2,3})\s*words?\s*(?:or (?:less|fewer)|max(?:imum)?)|(\d{2,3})[- ]word", re.I)
_BRIEF = re.compile(r"\b(short|brief|concise|few sentences|succinct)\b", re.I)

_FILLER = [
    "We truly value your loyalty and want every Orbit experience to feel effortless.",
    "Our team takes product quality very seriously and we are always working to improve our packaging and carrier partners.",
    "Please accept our sincere apologies once again for any inconvenience this has caused you and your household.",
    "As a growing company we rely on feedback like yours to make our products and our service better for everyone.",
]


def toy_reply(prompt):
    p = prompt
    has_facts = bool(re.search(r"business days", p, re.I) and re.search(r"pick-?up", p, re.I))
    restricted = bool(_RESTRICT.search(p))
    m = _LIMIT.search(p)
    limit = int(next(g for g in m.groups() if g)) if m else (90 if _BRIEF.search(p) else None)

    core = ["Hi Priya,",
            "I am very sorry that your Orbit Desk Lamp Pro arrived with a cracked base.",
            "I have your order OC-48213 open in front of me."]
    if has_facts:
        core += ["You can choose a refund or a free replacement.",
                 "We will arrange a free pickup within 48 hours of you confirming.",
                 "Your refund will return to your original payment method within 5-7 business days after pickup.",
                 "Please reply to this email to confirm which option you would like."]
        if not restricted:
            core.insert(-1, "As a gesture of goodwill we are also adding a 10% discount voucher to your next order.")
    else:
        if restricted:
            core += ["Our team will look into this and get back to you shortly."]
        else:
            core += ["We will refund your money within 24 hours.",
                     "As a gesture of goodwill we are also adding a 10% discount voucher to your next order."]
    signoff = ["Warm regards,", "Orbit Customer Care"]

    sentences = core + signoff
    if limit is None:
        sentences = core + _FILLER + signoff
    else:
        while _words(" ".join(sentences)) > limit and len(core) > 3:
            core.pop(-1)
            sentences = core + signoff
    return "\n".join(sentences[:-2]) + "\n\n" + "\n".join(sentences[-2:])


# ----------------------------------------------------------------------------------------------
# Mission 2: extraction
# ----------------------------------------------------------------------------------------------
_PRODUCTS = ["desk lamp", "monitor stand", "usb-c dock", "webcam", "ergonomic chair", "standing desk"]
_NUMWORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
_ALT_KEYS = {"customer_name": "name", "order_id": "order", "item": "product", "quantity": "qty", "urgency": "priority"}


def _extract_message(msg):
    m = (msg or "").strip()
    name = None
    for pat in (r"\b(?:it'?s|its|this is|i am|i'm)\s+([A-Z][a-z]+(?: [A-Z][a-z]+)?)",
                r"([A-Z][a-z]+(?: [A-Z][a-z]+)?) here\b",
                r"^Hi team,?\s*([A-Z][a-z]+)\.",
                r"^([A-Z][a-z]+(?: [A-Z][a-z]+)?)\.\s"):
        mm = re.search(pat, m)
        if mm:
            name = mm.group(1)
            break
    oid = re.search(r"\bOC-\d+\b", m)
    low = m.lower()
    item = next((p for p in _PRODUCTS if re.search(re.escape(p) + r"s?\b", low)), "item")
    qty_raw = None
    qm = re.search(r"\b(\d+|one|two|three|four|five|six|a pair)\s+(?:of\s+)?(?:" + "|".join(re.escape(p) for p in _PRODUCTS) + r")", low)
    if not qm:
        qm = re.search(r"\b(\d+|one|two|three|four|five|six|a pair)\b(?:\s+\w+){0,2}?\s+(?:" + "|".join(re.escape(p) for p in _PRODUCTS) + r")", low)
    if qm:
        qty_raw = qm.group(1)
    qty_int = int(qty_raw) if qty_raw and qty_raw.isdigit() else (_NUMWORDS.get(qty_raw) or (2 if qty_raw == "a pair" else 1))
    if re.search(r"asap|urgent|tomorrow|today", low):
        urg_true, urg_raw = "high", ("asap" if re.search(r"asap|urgent", low) else "needed today")
    elif re.search(r"next week|within 5 days|within a week", low):
        urg_true, urg_raw = "medium", ("next week is fine" if "next week" in low else "within 5 days")
    elif re.search(r"no rush|whenever", low):
        urg_true, urg_raw = "low", "no rush"
    else:
        urg_true, urg_raw = "low", "not specified"
    crude = "high" if re.search(r"asap|urgent|tomorrow|today", low) else "low"
    return dict(name=name or "Unknown", oid=oid.group(0) if oid else None, item=item, qty_raw=qty_raw or "1",
                qty_int=qty_int, urg_true=urg_true, urg_raw=urg_raw, urg_crude=crude)


def toy_extract(prompt, message):
    p = prompt.lower()
    e = _extract_message(message)
    if "json" not in p:
        order = f"Their order number is {e['oid']}." if e["oid"] else "No order number was given."
        return f"The customer, {e['name']}, wants {e['qty_raw']} {e['item']}. {order} It sounds like \"{e['urg_raw']}\"."
    key = lambda f: f if f in p else _ALT_KEYS[f]
    qty = e["qty_int"] if re.search(r"integer|number|numeric|digit", p) else e["qty_raw"]
    if all(w in p for w in ("low", "medium", "high")):
        precise = "week" in p and re.search(r"2 days|two days|48", p)
        urgency = e["urg_true"] if precise else e["urg_crude"]
    else:
        urgency = e["urg_raw"]
    order = e["oid"] if e["oid"] else (None if re.search(r"\bnull\b", p) else "N/A")
    item = e["item"] if re.search(r"singular|lowercase|lower case|lower-case", p) else e["item"].title() + "s"
    obj = {key("customer_name"): e["name"], key("order_id"): order, key("item"): item,
           key("quantity"): qty, key("urgency"): urgency}
    body = json.dumps(obj, indent=2)
    pure = re.search(r"\b(only|nothing else|no explanation|no extra|without any|no other text|just the json|just json)\b", p)
    return body if pure else f"Sure! Here is the JSON you asked for:\n```json\n{body}\n```"


# ----------------------------------------------------------------------------------------------
# Mission 3: ticket classification
# ----------------------------------------------------------------------------------------------
_LEXICON = {
    "Billing": "charge charged refund invoice payment paid price coupon discount bill billed card amount",
    "Delivery": "parcel package courier tracking shipping delivered delivery arrive arrived transit box shipment",
    "Technical Issue": "wifi wi-fi app crash freeze firmware bluetooth connect flicker error offline dock disconnect pair",
    "Account Access": "login log sign password locked otp verification suspended account",
    "Product Feedback": "love loved great add feature suggest suggestion option fantastic feedback useful",
}
_LEX = {lab: {_stem(w) for w in ws.split()} for lab, ws in _LEXICON.items()}
_INJECT = re.compile(r"(ignore|disregard)\s+(all\s+)?(the\s+)?(previous|above|your|prior)?\s*instructions", re.I)
_DEFENCE = re.compile(r"<ticket>|</ticket>|\"\"\"|###|^---|\bdelimit|\buntrusted\b|treat\b[^.\n]{0,60}\bas (data|text|content)"
                      r"|(do not|don't|never)\s+follow\b[^.\n]{0,40}(instruction|command)|ignore any instruction", re.I | re.M)
_CONCISE = re.compile(r"\b(only|just|exactly|single)\b[^.\n]{0,50}\b(label|category|name|word|answer)\b|one word|nothing else|"
                      r"no explanation|without (any )?explanation|no extra|reply with the (label|category)|output the (label|category)|"
                      r"answer with|respond with the (label|category)", re.I)
_MONEY = {"refund", "billed", "reverse", "money", "payment"}
_DOUBLE = {"twice", "extra", "wrong", "duplicate", "double", "again", "identical", "two"}


def _parse_examples(prompt):
    out = []
    for m in re.finditer(r"Ticket:\s*(.+?)\s*\n\s*Category:\s*([A-Za-z ]+?)\s*(?:\n|$)", prompt):
        lab = next((l for l in LABELS if l.lower() == m.group(2).strip().lower()), None)
        if lab:
            out.append((_tokens(m.group(1)), lab))
    return out


def _parse_descriptions(prompt):
    descs = {}
    for lab in LABELS:
        m = re.search(r"^[\s>*\-\d.)]*" + re.escape(lab) + r"\s*(?:[:=–—-])\s*(.+)$", prompt, re.I | re.M)
        if m:
            descs[lab] = _tokens(m.group(1))
    return descs


def _split_ticket(prompt, ticket):
    """Everything before the ticket text = the instructions the 'model' reads for rules; the ticket is data."""
    i = prompt.rfind(ticket) if ticket else -1
    return (prompt[:i] + prompt[i + len(ticket):]) if i >= 0 else prompt


def toy_classify(prompt, ticket):
    instr = _split_ticket(prompt, ticket)
    injected = bool(_INJECT.search(ticket))
    defended = bool(_DEFENCE.search(instr))
    if injected and defended:        # the prompt marks the ticket as data: the injected sentence has no power
        ticket_clean = re.sub(r"[^.!?]*(ignore|disregard)[^.!?]*[.!?]?", " ", ticket, flags=re.I)
    else:
        ticket_clean = ticket
    names_given = [l for l in LABELS if l.lower() in instr.lower()]
    labels = names_given if len(names_given) == len(LABELS) else list(LABELS)
    toks = _tokens(ticket_clean)
    scores = {l: 0.0 for l in labels}

    # 1. weak built-in knowledge
    for l in labels:
        hits = len(toks & _LEX[l])
        scores[l] += 0.35 * min(hits, 3)
    # 2. label names / descriptions written in the prompt
    descs = _parse_descriptions(instr)
    for l in labels:
        scores[l] += 2.0 * len(toks & _tokens(l))
        if l in descs:
            scores[l] += 0.9 * len(toks & descs[l])
    # 3. few-shot examples written in the prompt: nearest neighbours vote
    sims = []
    ktoks = toks - _DOMAIN                    # "lamp", "app", "order" appear in every label: they carry no signal
    for etoks, lab in _parse_examples(instr):
        etoks = etoks - _DOMAIN
        if lab in scores and etoks and ktoks:
            sims.append((len(etoks & ktoks) / ((len(etoks) * len(ktoks)) ** 0.5), lab))
    for sim, lab in sorted(sims, reverse=True)[:3]:
        scores[lab] += 10.0 * sim
    # 4. an explicit tie-break rule written in the prompt
    moneyish = bool(toks & {_stem(w) for w in _MONEY}) or (_stem("charged") in toks and bool(toks & {_stem(w) for w in _DOUBLE}))
    if re.search(r"(charged|refund|money)[^.\n]{0,90}billing", instr, re.I | re.S) and "Billing" in scores and moneyish:
        scores["Billing"] += 3.5

    salt = sum(ord(c) for c in ticket) % len(labels)
    ordered = sorted(labels, key=lambda l: (-round(scores[l], 6), (labels.index(l) + salt) % len(labels)))
    top, second = ordered[0], ordered[1]

    # 5. prompt injection: obeys instructions inside the ticket unless the prompt marks the ticket as data
    if injected and not defended:
        for l in labels:
            if re.search(r"\b" + re.escape(l.lower()) + r"\b", ticket.lower()):
                top = l
                break

    if _CONCISE.search(instr):
        return top
    close = scores[second] > 0 and scores[second] >= 0.6 * scores[top]
    if close:
        return f"This could be {top} or {second}, depending on what the customer wants first."
    return f"This looks like a {top} ticket."


# ----------------------------------------------------------------------------------------------
def respond(task, prompt, payload):
    if task == "reply":
        return toy_reply(prompt)
    if task == "extract":
        return toy_extract(prompt, payload.get("message", ""))
    if task == "classify":
        return toy_classify(prompt, payload.get("ticket", ""))
    return "(offline demo model: no stand-in for this task)"
