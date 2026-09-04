# Borrower Copilot — Questions List (Locked v1.1)

Order matters. Must questions first (M1-M9), then one shared question (S1), then branch-specific additional questions.
Rule: Every additional question must move O1 / O2 / O3 / O4, else cut it.
Unknown / Don't Know / Skip is always allowed. Fewer answers = wider band + low confidence.

O1 = Borrow / Don't Borrow / Borrow Less + reason
O2 = Max amount (Lender sanction vs Safe capacity)
O3 = Fair rate band + APR with fees
O4 = EMI ceiling + tenure trade-off + stress case

---

## MUST — Everyone sees, in this order

### M1. What do you need + which one fits best? [one screen, two fields]
- M1a Purpose: single-select chips: Home / Vehicle / Education / Personal use / Business / Other
- M1b Sub-purpose (natural labels per purpose, product derived silently underneath):
  - Home: Buying ready house / Building on plot / Renovation / Buying plot / Loan against house (LAP) / Not sure
  - Vehicle: New 2W for myself / Used 2W / New car / Used car / Vehicle for earning / Not sure
  - Education: Degree India / Abroad / Skill course / Coaching / Not sure
  - Personal: Wedding / Medical / Travel / Gadgets / Repay costly loans / Not sure
  - Business: Stock / Machines / Expansion / Commercial vehicle / Working cash / Not sure
  - Other: free text.
- Backend: sub-purpose maps to product band (LAP only via "loan against house"; earning-vehicle settles productive=True at M1; own-use vehicle stays undecided until A-B5/A-C4). All bands reuse locked Sept 2026 products — no score changes.
- Moves: O1, O3 (M1a+M1b move O1 verdict, derived product moves O3 rate band)

### M2. How much do you want?
- Type: Rs. number input, starts 0, blocked at 0 (must-change; phantom wanted flips verdicts)
- Example: Priya 800000, Ravi 1500000, Anita 150000
- Moves: O2
- Why: Compare wanted vs safe capacity.

### M3a. What do you do?
- Type: Free text, empty allowed, display only
- Example: kirana store, delivery rider, software engineer
- Moves: None directly — feeds M3b context and Card copy only.

### M3b. How do you get paid? [a/b/c switch]
- Type: 3 big buttons, compulsory
- Options:
  - a) Fixed salary in bank every month (e.g. IT, teacher in school, nurse in hospital)
  - b) Own shop / business / clinic / freelance, I file ITR (e.g. kirana, private clinic doctor, tuition owner)
  - c) Daily / weekly / gig cash, changes every month (e.g. rider, tailor, daily wage, farmer)
- Moves: O2, O3 + opens branch
- Why: Deterministic branch selector. Decides FOIR %, verifiability, which additional questions show. No AI / API.

### M4a. Your net monthly in-hand income?
- Type: Rs. number, starts 0. Gig/cash branch gets two boxes (LOW + HIGH month); LOW wired to safe.
- Rule: If variable, use LOW end for safe calc, average for lender hint. This is the single source of truth for actual monthly cash income — no other question re-asks it.
- Moves: O2, O4
- Why: Base of FOIR and surplus.

### M4b. Does anyone else earn in family? Is that income steady right now?
- Type: Yes/No -> If Yes: How much per month? Rs. number + Relation + Steady/Stopped (stopped excluded from safe entirely)
- Example: Ravi 60000 + wife 18000 steady = 78000 household. Anita husband unemployed 8 months = excluded from safe.
- Rule: Lender counts 100% yours + 50% co-earner. Safe calc uses only currently-active income; a co-earner who stopped earning is excluded from the safe number entirely, not discounted to 50%.
- Moves: O2, O4
- Why: Raises ceiling slightly but adds dependency risk note. Captures realized income shock vs hypothetical M9 shock.

### M5a. Total EMI + all app-loans / BNPL / chit fund you pay every month?
- Type: Rs. number + No EMIs option, starts 0
- Bounce screen skipped at 0 EMI (recorded no + note; accepted edge: a closed loan's old bounce is missed)
- Hint: Include car loan, app loans, chit fund, buy-now-pay-later.
- Example: Priya 14000, Ravi 0, Anita 3000-4000
- Moves: O1, O2, O4
- Why: FOIR = (old EMI + new EMI) / income. Old EMI directly reduces surplus for EMI-ceiling calc. Must include informal loans users don't call "EMI."

### M5b. Any EMI bounced in last 12 months?
- Type: Yes/No + Don't Remember
- Moves: O1, O3
- Why: A bounce is a danger flag — rate +1-2%, FOIR down. Anita case needs this.

### M6. Total household expenses per month incl. rent?
- Type: Rs. number, starts 0; 0 opens an estimate-confirm screen (assumed 40%, must acknowledge)
- Hint: rent + food + school + transport + etc.
- Moves: O1, O4
- Why: Surplus = Income - Old EMI - Expenses - New EMI. If <0 -> Don't Borrow / Borrow Less.

### M7. Your age?
- Type: Number 18-70 (starts 35; residual phantom-age risk documented)
- Early tenure note at 60+: lenders cap around N years, EMIs run higher (display only)
- Rule: Max tenure = 65 - age (60 for salaried, conservative).
- Moves: O2, O4
- Why: Without age, tenure trade-off is fake. 29yr = 25yr possible, 42yr = 18yr max.

### M8. Credit score?
- Type: Free text (e.g. 780, or "don't know"). Backend parses to bands via parse_score: 750+ / 700-750 / 650-700 / Below 650 / Don't Know / No history, with a confirm screen ("We read this as X. Correct?").
- Rule: Unknown is never zero. Unknown -> wide band, low confidence, never treated as 300.
- Moves: O3
- Why: 780 narrows to band with high confidence. Don't Know keeps wide band + message on consequence.

### M9. Safety buffer — if income stops for 2 months, how will you pay EMI?
- Type: Single-select + helper text "We ask this to set a safe EMI, not to reject you."
- Options: No backup / Family or friend could cover 1-2 EMIs (state who) / Savings for 1-2 months expenses / Savings for 3+ months
- Backend map: No backup = 0 months / Family help = 1 month, low confidence / 1-2 months = medium / 3+ = strong
- Moves: O1, O4
- Why: Sets FOIR cap and drives the O4 stress case. 0 buffer + dependents -> FOIR 30-35% + Borrow Less/Don't. 3+ buffer -> FOIR 50-60% + Borrow allowed.

---

## SHARED — Asked to everyone, before branching. Optional, always skippable.

### S1. Have you already got a loan offer? [Rate + processing fee % + tenure months, or Skip]
- Type: Rate number + fee % + tenure months (tenure prefilled from age/product standard), or Skip
- Moves: O3, O4 (feeds APR comparison and the Card directly)
- Why: Single input the Negotiation Card most depends on ("lender quotes 14%, fair is 11-12.5%"). Relevant to all branches, including borrowers with existing high-cost loans.

---

## ADDITIONAL — Branch specific. Skip / Don't Know always allowed.

### If a) Salaried — skip collateral / ITR
- A-S1 Job vintage + employer type? [<1yr / 1-3yr / 5yr+ MNC/Govt/Reputed] -> Moves O3 down 0.5-1%, confidence up
- A-S2 Variable pay %? [0% fixed / 10-30% / >30%] -> If >30%, use 6-month average for O2/O4. Moves O2, O4
- A-S3 Credit card utilisation? [No card / <30% / 30-70% / >70%] -> >70% = O3 +1%. No card = no change. Moves O3

### If b) Self-employed — skip salary-slip
- A-B1 Business vintage? [<2yr / 2-10yr / 10yr+] -> Moves O2 up, O3 down
- A-B2 ITR yearly income? [e.g. 4.2L -> ~35k/mo] -> ITR-only. Lender-side O2 uses ITR figure; safe-side O2 uses M4a actual figure. The gap is the two-number split. Moves O2
- A-B3 Collateral? Own shop/house value, loan-free? [e.g. 45L unencumbered] -> Routes to LAP 10-11.5% vs personal 16%+, raises O2 to 50-60% of collateral value. Follow-ups hidden at value 0. Also injected when sub = loan-against-house (any branch) or wanted > 10x monthly safe income. Moves O2, O3, O1
- A-B4 Existing business loan detail? [amount + rate] -> Moves O2
- A-B5 Will this loan earn more? Extra per month? [e.g. +X from second stock + vehicle] -> Finalizes productive vs non-productive for Vehicle/Business purpose. Moves O1 from No to Conditional Yes if productive.

### If c) Informal — skip ITR / collateral, ask survival
- A-C2 Dependents + upcoming big expense? [e.g. 2 kids + husband jobless 8m] -> Lowers O4 to 30-35% FOIR, adds stress case. Moves O1, O4
- A-C3 Total app loans outstanding + rate? [e.g. 35k @30%+] -> Rate hidden at 0 outstanding. Also injected when sub = repay-costly-loans (any branch). If >25%, advise consolidate first before new borrowing. Moves O1
- A-C4 Will the scooter/asset increase income? By how much? [+8k-10k?] -> Finalizes productive vs non-productive for informal branch. Only reason to allow Borrow. Moves O1

---

## UX Rules
1. One question per screen, Choice > Number > Text.
2. No why-hints on input screens (removed per UI review); every output still carries a one-sentence why.
3. Confirm step for Other purpose: "We understood: Wedding. Correct?"
4. Progress: Must (9 steps) -> Shared (1 step) -> Branch (max 5) -> Results + Negotiation Card.
5. Results show: Verdict + 2 amounts + Rate band + APR + EMI ceiling + one-sentence why per number + Confidence badge (High/Med/Low) + Card screen.
