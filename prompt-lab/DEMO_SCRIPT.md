# Orbi Prompt Lab - 5-minute demo for client calls

Goal: the client sees that anyone can try it, the score moves in front of them, and every learner leaves proof.

**Setup (before the call):** run `streamlit run app.py` with your real key, open `prompt_lab.html?trainer=1` and
`dashboard/index.html` in other tabs. Run Mission 1's baseline once so you know the number.

## 0:00 Hook (30 s)
"Everyone has used ChatGPT. Almost nobody can say whether their prompt is good. Here, the prompt gets a score."
Show the course page: one stage, one quiz question, the lab step list.

## 0:30 Mission 1: the angry customer (2 min)
- Show Priya's email and the policy sheet. "Orbi must reply without inventing policy."
- Run the **baseline**. Point at the red crosses: invented promise, too long.
- Click **Insert policy facts**, add "Use only the policy. Under 100 words." Run.
- The score jumps. "Each red cross became one sentence. The learner sees cause and effect."

## 2:30 Mission 3: break the bot (1.5 min)
- Open the 12 tickets. Point at the one that says "Ignore all previous instructions".
- Run the baseline, then click **+ Injection guard** and run again. The ticket stops fooling Orbi.
- "Same idea as a security awareness exercise, but hands-on."

## 4:00 Proof and dashboard (1 min)
- Click **Generate proof code**, paste it in the course page (trainer shortcut: "Insert a demo proof code").
- Switch to the dashboard: tiers, stage funnel, who is stuck. "The trainer sees the whole cohort without marking anything."

## 5:00 Close
"Same model works for RAG, prompt engineering, agents and evals. Pick a topic your team needs, and we build the lab on your own use case."

## If something goes wrong
- No internet: switch the sidebar to **Offline demo**. Say so plainly: a toy model, same lab, rehearsal numbers.
- A live score looks odd: re-run once. Missions 2 and 3 run at temperature 0; Mission 1 uses the temperature slider.
