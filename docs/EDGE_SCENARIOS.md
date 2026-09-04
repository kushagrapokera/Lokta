# Edge scenarios — easy / medium / hard with blanks (not the brief's 3 borrowers)

Tests: `tests/test_edge_scenarios.py`. All outputs from `rules/engine.py::compute`. No hand editing.

## Easy — Rohan, 32, Pune, salaried. Zero blanks + offer given.

Filled: personal + personal 5L; salary 80k; old EMI 0; expenses 35k; age 32; score 750+; buffer 3+; 5yr MNC; card <30%; offer 12% + 1.5% fee.

| Output | Value |
|--------|-------|
| O1 | Borrow — surplus positive, cap + stress pass |
| O4 ceiling | 44,000 (80000×55% − 0); wanted EMI 11,249/60mo; stress passes |
| O3 | 11.5–13.5% width 2, High confidence; offer 12% flagged FAIR |
| Handling | Nothing estimated. Narrow band earned by complete answers. |

## Medium — Meena, 38, Jaipur boutique, self-employed. Blanks: score unknown, co-earner skipped, offer skipped, collateral skipped.

Filled: business + business 10L; actual 55k; ITR 4.8L/yr (40k/mo); old EMI 12k; expenses 28k; age 38; buffer family; vintage 2–10yr; extra +15k/mo.

| Output | Value |
|--------|-------|
| O1 | Don't borrow — surplus −10,122 (55k − 12k − 28k − 25k EMI) |
| O4 ceiling | 12,750 (55000×45% − 12000, lender cap on ITR 40k lower) |
| O3 | 14.5–20.5% width 6, Medium; unknown never treated as 300 (finite band) |
| Handling | Blanks widen band + drop confidence; math still decides honestly. Fix path: prove score/collateral to narrow; reduce wanted or tenure to turn surplus positive. |

## Hard — Salim, 45, auto driver, informal. Blanks: expenses, co-earner, old EMI, bounce unknown, extra unproven.

Filled: vehicle + two_wheeler 1.2L; income 22k; age 45; score no_history; buffer none.

| Output | Value |
|--------|-------|
| O1 | Borrow with conditions — key spending details missing plus no backup, limit estimated |
| O4 ceiling | 6,600 (22000×30% − 0); expenses assumed 8,800 = 40% of income, flagged estimated; EMI 2,998; stress passes on estimates |
| O3 | 14.25–21.25% width 6, Low (5 unknowns) |
| Handling | Before fix this case wrongly said Borrow (missing spend defaulted to 0). Now: spend never zero (40% estimate, flagged), confidence Low, verdict capped at Conditional — never clean Borrow with estimated spend + no backup. Fill actual expenses + build 1–2 EMI backup to recheck. |

## Every-scenario guarantees (tested)

- Missing spend → 40% estimate + flagged + Low (never 0). Missing old EMI / age → 0 / 35 + unknown counted.
- Unknown score → wide band + lower confidence, never 300, always finite.
- Low + no backup → at most Conditional, never Borrow.
- Skip path never crashes; card always 5 lines; every number carries a why.
