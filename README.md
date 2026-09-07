# Borrower Copilot

Self-check before walking into a lender: should you borrow, how much is safe, fair rate, EMI ceiling, plus a one-page Negotiation Card. No login, no bureau pull, nothing stored.

## Steps to Run locally

Requires conda env `lokta` with Python 3.11 (or any Python 3.10+).

```bash
conda activate lokta
pip install -r requirements.txt   # flask + pytest, one time
python flask_app.py               # opens http://127.0.0.1:5000
```
## Test

```bash
conda activate lokta
python -m pytest tests/ -v   # 10 tests: structure + Priya/Ravi/Anita golden + easy/medium/hard blanks
```

## Structure

- `flask_app.py` + `templates/` — Flask flow only (questions → branch → results + card). No numbers here.
- `rules/config.py` — single source of truth, mirrors RULES.md. Only file to edit live.
- `rules/` — one file per calculation: questions, flow, income, emi, amount, fair_rate, apr, verdict, confidence, card, explain, engine.
- `QUESTIONS.md` — exact on-screen text, in flow order.
- `RULES.md` — what/value/why/source table.
 `RULES_BY_FILE.md` — what each `rules/` file does and which questions feed it. `persona_runthrough.md` — Priya/Ravi/Anita wlakthrough over the engine.

## The 3 borrowers

Priya (salaried, 780 score, wedding 8L) → Borrow, ceiling 46.5k, fair 11.5–13.5%.
Ravi (kirana, ITR gap, shop 45L, LAP route) → Conditional Borrow, fair 9.5–11%.
Anita (informal, bounce, 30%+ loans) → Don't borrow, ceiling 4.4k.
Full traces in `persona_runthrough.md` — brief-only details, no filled-in blanks.
