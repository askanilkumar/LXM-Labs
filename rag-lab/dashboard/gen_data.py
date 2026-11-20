"""Generates synthetic cohort data and injects it into index.html (also writes data.json)."""
import json, random, re, os
from datetime import datetime, timedelta

random.seed(26)
ASOF = datetime(2026, 10, 26, 10, 30)
FAST = 150
# name, stages_done, stretch_minutes (None = not done), in-progress stage xp, days since last activity, start offset (days ago)
SPEC = [
    ("Aarav Menon", 5, 118, 0, 0, 3), ("Ananya Iyer", 5, 131, 0, 0, 3), ("Vaishnavi Gowda", 5, 142, 0, 1, 3),
    ("Divya Nair", 5, None, 35, 0, 3), ("Harish Kumar", 5, 205, 0, 1, 3), ("Kavya Shetty", 5, None, 0, 1, 3),
    ("Rohit Agarwal", 5, None, 0, 2, 3), ("Meera Krishnan", 5, None, 22, 0, 3),
    ("Bhavya Reddy", 4, None, 45, 0, 3), ("Jayanth Raghavan", 3, None, 60, 0, 3), ("Priya Venkatesh", 3, None, 20, 1, 3),
    ("Naveen Prasad", 3, None, 0, 1, 3), ("Sneha Kulkarni", 4, None, 30, 1, 3), ("Tarun Mehta", 3, None, 55, 0, 3),
    ("Chaitanya Rao", 2, None, 40, 1, 3), ("Farhan Sheikh", 1, None, 50, 2, 3), ("Gayathri Subramanian", 2, None, 10, 3, 3),
    ("Ishita Banerjee", 1, None, 25, 3, 3), ("Lokesh Varma", 0, None, 0, 6, 3), ("Omkar Patil", 0, None, 0, 6, 3),
]


def tier(n, stretch_min):
    if n == 5 and stretch_min is not None and stretch_min <= FAST:
        return "Diamond"
    if n == 5:
        return "Gold"
    if n >= 3:
        return "Silver"
    if n >= 1:
        return "Bronze"
    return "Not started"


people = []
for name, n, sm, part, last, start in SPEC:
    xp = []
    for i in range(5):
        if i < n:
            xp.append(random.randint(82, 100))
        elif i == n and part:
            xp.append(part)
        else:
            xp.append(0)
    stretch_xp = 100 if sm is not None else 0
    started = ASOF - timedelta(days=start, hours=random.randint(0, 3))
    last_active = ASOF - timedelta(days=last, hours=random.randint(0, 6) if last else random.randint(0, 2), minutes=random.randint(0, 50))
    people.append({
        "name": name, "stagesCompleted": n, "stageXp": xp, "stretchXp": stretch_xp, "minutesToStretch": sm,
        "xp": sum(xp) + stretch_xp, "tier": tier(n, sm), "startedAt": started.isoformat(), "lastActive": last_active.isoformat(),
        "activeMinutes": (n * 28 + (part // 2) + random.randint(0, 25)) if (n or part) else 0,
    })
data = {"cohort": "UNext · RAG Foundations pilot", "asOf": ASOF.isoformat(), "fastMinutes": FAST, "synthetic": True, "participants": people}
here = os.path.dirname(os.path.abspath(__file__))
json.dump(data, open(os.path.join(here, "data.json"), "w"), indent=2)
html_path = os.path.join(here, "index.html")
if os.path.exists(html_path):
    html = open(html_path).read()
    blob = json.dumps(data)
    html = re.sub(r'(<script id="embedded" type="application/json">).*?(</script>)', lambda m: m.group(1) + blob + m.group(2), html, flags=re.S)
    open(html_path, "w").write(html)
from collections import Counter
print(Counter(p["tier"] for p in people))
