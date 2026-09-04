# Borrower Copilot — Build Plan (multi-phase, SWE-clean, Python)

Goal: working web app + RULES.md + 3 run-throughs + walkthrough. Runs locally <5 min. Python + Streamlit, no backend, no API key, offline after install.
Specs locked in: QUESTIONS.md v1.1, THRESHOLDS_SEPT2026.md (FOIR 55/45/30, 1.5x, stress -20%/+2%, APR search method).

Stack: Python 3.10+, Streamlit (UI only). Rules are pure Python functions with type hints. Tests with pytest.

## File structure (separate file per thing being calculated)

```
/app.py                — Streamlit flow only (screens, progress, render). No numbers here. Imports rules/*.
/requirements.txt      — streamlit only (pin version). `pip install -r requirements.txt`
/rules/
  __init__.py
  config.py            — SINGLE SOURCE OF TRUTH. All thresholds/bands/fees/FOIR caps. Mirrors RULES.md. Only file edited in live follow-up.
  questions.py         — question defs from QUESTIONS.md v1.1 (M1-M9, S1, A-S/A-B/A-C), branching on a/b/c, skip/unknown handling.
  income.py            — normalize M4a/M4b: Income_safe (LOW + active co-earner only) vs Income_lender (ITR for self-employed).
  emi.py               — EMI formula, tenure cap (65-age), ceiling O4, tenure table, stress test.
  amount.py            — O2 lender vs safe + LTV cap + min() recommend + 1.5x Borrow Less check.
  fair_rate.py         — O3 base band by product (Sept 2026 table) + adjustments (score/vintage/bounce/collateral). Band only, never point.
  apr.py               — APR: EMI on P, solve same EMI on (P-fee) by binary search 0-50%. Fair APR vs offer APR.
  verdict.py           — O1 hierarchy (surplus, FOIR, danger combo, 1.5x, stress+productive). Returns verdict + reason + flip condition.
  confidence.py        — High/Med/Low + widen rules (O2 +/-20%, O3 +2%). Unknown never zero.
  card.py              — Negotiation Card builder (fair vs quote, 3 whys, ceiling, warning).
  explain.py           — one-sentence why per number. Every number traceable.
/docs/
  RULES.md             — generated from config.py: what | value | why | source or my judgement.
  RUNTHROUGHS.md       — Priya/Ravi/Anita: Qs asked, 4 outputs, card each.
  WALKTHROUGH.md       — 5-min script: what built, what next, what cut.
/tests/
  test_rules.py        — pytest, pure-function tests: Priya/Ravi/Anita golden outputs + edge (unknown score, 0 buffer, bounce).
README.md              — run in <5 min: `pip install -r requirements.txt && streamlit run app.py`. No build, no key, offline.
```

SWE rules:
1. No numbers outside config.py. UI and calculators import from config.
2. Rules are pure functions: answers dict in, outputs out. No Streamlit calls inside rules/, no fetch, no AI/API, deterministic. Type hints + docstrings.
3. Unknown/Skip flows through every calculator as None/"unknown", widens band, lowers confidence. Never 0, never 300.
4. Each calculator owns one file above. Cross-imports only via explicit args, no hidden globals.
5. Every output carries `value + why + confidence` together (explain.py).
6. Streamlit session_state holds answers only; all math lives in rules/.

## Phase 0 — Setup (0.5 hr)
- Init repo, venv, requirements.txt (streamlit), add PLAN.md, copy QUESTIONS/THRESHOLDS as reference. Verify `streamlit run app.py` opens with stub screen offline.
- Done when: folder matches structure above (empty stubs ok), install + run <5 min.

## Phase 1 — Rules engine, no UI (4-5 hrs)
1. rules/config.py from THRESHOLDS Sec 0-4 (base bands, FOIR 55/45/30, fees, slabs, 1.5x, stress).
2. rules/questions.py + income.py + emi.py. Test: ceiling math for Priya 46.5k, Anita 4.4k.
3. rules/amount.py + fair_rate.py + apr.py. Test: Ravi LAP 10-11.5% vs personal 16%+, APR examples (8L 11.5%+2% 5yr ~12.3%).
4. rules/verdict.py + confidence.py + card.py + explain.py. Test O1 hierarchy hits Don't for Anita, Conditional for Ravi.
- Done when: `pytest tests/test_rules.py` passes 3 golden personas + 4 edge cases. No UI needed.

## Phase 2 — App flow UI with Streamlit (3-4 hrs)
- Steps in app.py with st.form/radio/number_input: M1 (purpose+product combo) -> M2 -> M3a/M3b -> M4a/M4b -> M5a/M5b -> M6 -> M7 -> M8 -> M9 -> S1 -> branch (max 5) -> Results + Card.
- One Q per screen via session_state step, chips via radio horizontal, Why-we-ask as st.caption, Skip/Don't Know always, confirm for Other purpose.
- app.py only calls rules/*, never computes. Progress: Must 9 -> Shared 1 -> Branch -> Results. Use st.progress + mobile-friendly narrow layout.
- Done when: all 3 personas completable on phone width, skip path works with wide bands.

## Phase 3 — Results + Card (2 hrs)
- Results with st.metric + tables: O1 verdict + reason + flip, O2 two numbers + use-this-one, O3 band + APR + offer compare, O4 ceiling + tenure table + stress pass/fail, confidence badge, 1-sentence why per number.
- Card: 1 st.container — fair band vs quote, 3 whys, ceiling, 1 warning. Printable / screenshot-able via st.download_button (text) + screen.
- Done when: every number has why, ranges shown as ranges, Unfair flagged red.

## Phase 4 — Docs (2-3 hrs)
- RULES.md from config.py (table, no extra numbers). Include honesty section (what we don't know).
- README.md (<5 min run), RUNTHROUGHS.md (3 personas full trace), WALKTHROUGH.md (next/cut).
- Done when: fresh clone runs first time, docs at root.

## Phase 5 — Harden + submit (1-2 hrs)
- Re-run formulas against v1.1 (no refs to deleted A-C1/A-C5/old-A-B2). Test offline, `pytest` green.
- Live-change drill: change FOIR 55->60 in config.py only, verify app updates. Record walkthrough.
- Submit repo link with 4 deliverables at root.

Total: ~12-16 hrs as brief expects.
