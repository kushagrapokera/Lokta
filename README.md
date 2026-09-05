# Borrower Copilot

Self-check before walking into a lender: should you borrow, how much is safe, fair rate, EMI ceiling, plus a one-page Negotiation Card. No login, no bureau pull, nothing stored.

## Run locally in under 5 minutes

Requires conda env `lokta` with Python 3.11 (or any Python 3.10+).

```bash
conda activate lokta
pip install -r requirements.txt   # flask + pytest, one time
python flask_app.py               # opens http://127.0.0.1:5000
```

Offline after install. No backend, no API key.

## Test

```bash
conda activate lokta
python -m pytest tests/ -v   # 10 tests: structure + Priya/Ravi/Anita golden + easy/medium/hard blanks
```

## Structure

- `flask_app.py` + `templates/` — Flask flow only (questions → branch → results + card). No numbers here.
- `rules/config.py` — single source of truth, mirrors RULES.md. Only file to edit live.
- `rules/` — one file per calculation: questions, flow, income, emi, amount, fair_rate, apr, verdict, confidence, card, explain, engine.
- `QUESTIONS.md` — locked v1.1 question list. `THRESHOLDS_SEPT2026.md` — Sept 2026 bands + locked thresholds.
- `RULES.md` — what/value/why/source table. `docs/RUNTHROUGHS.md` — 3 borrowers traced. `docs/WALKTHROUGH.md` — 5-min script.

## The 3 borrowers

Priya (salaried, 780 score, wedding 8L) → Borrow, ceiling 46.5k, fair 11.5–13.5%.
Ravi (kirana, ITR gap, shop 45L, LAP route) → Conditional Borrow, fair 9.5–11%.
Anita (informal, bounce, 30%+ loans) → Don't borrow, ceiling 4.4k.
Full traces in `docs/RUNTHROUGHS.md`.
