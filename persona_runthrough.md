# Persona run-through — 3 borrowers, brief-only details, latest flow + engine

Method (no old fixtures, nothing invented):
- Each persona was driven screen-by-screen through the **current Flask flow**
  (`flask_app.py`, same test-client harness as `tests/test_results_card.py`),
  then computed once via `compute()` in `rules/engine.py`.
- Only values stated in the **original brief**
  (`Lokta_Borrower_Copilot_Build_Challenge_v2.html`) were typed in. Everything
  else was left blank, skipped, or left on the screen's own default — and each
  such silence is narrated below with exactly what the engine did with it.
- Branch screens the brief doesn't cover were **skipped** (all are skippable).
- Three flow defaults had to be accepted because the screens require them, and
  are disclosed every time they bite: repayment tenure keeps the app's own
  prefilled max (brief never states tenure); backup keeps the UI default
  ("No backup"); bounce keeps the UI default ("no") only where the bounce
  field is hidden (zero EMI). Expense and score confirms ("We assumed…",
  "We read this as…") were accepted to proceed — the assumption itself is the
  documented behaviour under test.
- Small judgement calls forced by the brief's wording are marked [CALL] with
  the reason. Nothing else was added.

Reading order per persona: entered answers → income → ceiling → rate → amounts
→ EMI/surplus/stress → verdict → confidence → card → what the silences cost.

---

## 1. Priya, 29 — Bengaluru, salaried

Brief: software engineer at a large MNC for 5 years. Net Rs.1,10,000/month.
One car loan, EMI Rs.14,000. Score 780. Rents at Rs.28,000. Wants Rs.8,00,000
personal loan for a wedding.

### Entered per screen (brief-only)

- Purpose: Personal use → Wedding (stated). Amount: 8,00,000 (stated).
- Tenure: kept app prefill, 5 years **[flow default; brief silent]**.
- Work: salaried (stated). Income: 1,10,000, no co-earner (brief names none).
- Old EMI: 14,000 (stated). Bounce: **unknown — brief never says**
  (a live car loan exists, so "no" would be invented; "unknown" is the honest
  encoding and the UI offers it).
- Expenses: **left blank — brief gives rent (28k), not total household spend**,
  and rent is not total. Estimate-confirm accepted.
- Age 29 (stated). Score "780" → confirmed 750+ (stated).
- Backup: **UI default "No backup" — brief never mentions savings**.
- Offer: skipped (none mentioned). Job branch: 5yr+ at MNC **(stated)**.
  Card branch: **skipped (brief silent)**.

### Income: Rs.1,10,000 safe = Rs.1,10,000 lender

Salaried, no co-earner. No ITR question exists on this branch, so no ITR
handling was needed — lender income equals safe income by rule.

### Ceiling: 110000 × 35% − 14000 = Rs.24,500 (not 46,500)

Base salaried share is 55%, but backup is "none", so the no-backup rule
squeezes every branch to 35%: 1,10,000 × 0.35 − 14,000 = Rs.24,500. The
bounce-unknown leaves the cap untouched (cap drops only on explicit "yes").
Cost of silence #1: the unstated backup nearly halved her ceiling.

### Rate: 10.5–16.5% (not 11.5–13.5%)

Personal base 10–18 (mid 14). Score 750+ −1% (stated), stable 5yr MNC job
−0.5% (stated), bounce-unknown assumed 1 → +1% with a "confirm" note.
Adjustment −0.5. Any bounce forces a wide band: 6% wide → 10.5–16.5%, mid
13.5. Cost of silence #2: the unstated bounce history tripled her band width
(2% → 6%).

### Amounts: bank 11.53L / safe 10.65L / use 10.65L

60 months. Lender cap 24,500 at 10% → Rs.11,53,000. Safe cap 24,500 at her
13.5% mid → Rs.10,65,000. Use Rs.10,65,000. Wanted 8L is below 1.5 × safe,
so no Borrow Less.

### EMI, surplus, stress: pass on real numbers

8L at 13.5% over 60 months → EMI Rs.18,408 (inside the 24,500 ceiling; total
EMI share 29.5% < 35%). Expenses assumed Rs.44,000 (40% of safe, flagged).
Surplus = 110000 − 14000 − 44000 − 18408 = Rs.33,592, positive. Income −20%
shock leaves Rs.11,592; rate +2% shock pushes EMI to Rs.19,243, surplus stays
positive. Stress passes both.

### Verdict: Borrow with conditions (not clean Borrow)

"Key spending details missing plus no backup, so limit is estimated." Rule 3B:
estimated spend + no buffer can never earn a clean yes, even though every
number passes. Flip: fill actual household expenses and keep 1–2 EMIs backup,
then recheck.

### Confidence: Medium, 2 unknowns (bounce-unknown, estimated spend)

Skipped card screen costs nothing on the salaried branch by rule.

### Card

Fair 10.5–16.5% · ceiling Rs.24,500 · why: score, stable job, bounce-unclear
note · no offer entered · warning: Conditional.

---

## 2. Ravi, 42 — Mysuru, self-employed

Brief: kirana store 14 years. Cash income Rs.40,000–80,000/month. ITR
Rs.4,20,000/year. Shop premises ~Rs.45,00,000, unencumbered. Never taken a
formal loan; no credit score. Wife earns Rs.18,000 teaching. Wants
Rs.15,00,000 for a second stock line and a delivery vehicle.

### Entered per screen (brief-only)

- Purpose: Business → Stock/inventory **[CALL: brief names two uses (stock +
  vehicle); one sub-purpose per screen. Both map to product `business` and
  both settle productive=True, so the pick moves no number — verified in
  `rules/questions.py`.]**
- Amount: 15,00,000 (stated). Tenure: kept app prefill, 5 years
  **[flow default; brief silent]**.
- Work: self-employed (stated). Income: **40,000 — the LOW end of the stated
  range, per the M4a rule "if variable, use LOW end for safe calc" [CALL:
  rule application, not a persona statement]**. Co-earner: wife 18,000, steady
  **[CALL: brief's present tense "earns" read as active; only a "stopped"
  earns exclusion]**.
- Old EMI: 0 — never borrowed (derived). Bounce: UI hides the field at zero
  EMI and records "no" (UI behaviour, matches "never taken a loan").
- Expenses: **left blank — brief states none. Estimate-confirm accepted.**
- Age 42 (stated). Score: typed "never taken a loan" → confirmed no-history
  (exact brief wording; unknown-handling applies).
- Backup: **UI default "No backup" — brief silent.** Offer: skipped.
- ITR: 4,20,000 (stated). Collateral: 45,00,000, loan-free Yes, commercial
  **[CALL: "shop premises" read as commercial; residential would only change
  −3% to −4%]**. Vintage: 10yr+ (14 years stated). Extra income: **0 — brief
  gives intent (stock + vehicle) but no monthly amount, and the field reads
  "0 if none"**. Productive stays True via the stock sub-purpose; the zero
  only selects the "unproven or thin" branch of verdict Rule 5.

### Income: Rs.58,000 safe vs Rs.44,000 lender

Safe = 40,000 LOW + 18,000 wife = Rs.58,000. Lender = ITR 4,20,000 ÷ 12 =
35,000 + half the wife (9,000) = Rs.44,000. The bank sees ~75% of reality.

### Ceiling: 58000 × 35% − 0 = Rs.20,300

Self-employed base is 45%, squeezed to 35% by the unstated backup
(UI default "none"). No bounce. 58,000 × 0.35 = Rs.20,300.

### Rate: 11–17% — and NOT the LAP band

**Finding: the current question list has no path from a Business purpose to
the LAP product band** — every business sub-purpose maps to product
`business`. The 45L shop therefore earns only the −3% collateral discount
off the business base 11–24 (mid 17.5): −0.5% vintage (14yr stated) −3%
commercial = −3.5 → mid 14.0. Unknown score (no-history) widens to 6%:
11–17%. Older run-throughs showing Ravi at LAP 9.5–11% came from a
hand-set product, not from this flow.

### Amounts: bank 7.08L / safe 8.72L / use 7.08L

60 months (business max 5 years). Lender cap = 44,000 × 35% = 15,400 at 11%
→ Rs.7,08,000. Safe cap = 58,000 × 35% = 20,300 at 14% mid → Rs.8,72,000
(LTV 60% of 45L = 27L does not bind at this tenure). Wanted 15L exceeds
1.5 × safe (13.08L) → Borrow Less flag is set — but Rule 1 fires first.

### EMI, surplus: the household breaks by Rs.102

15L at 14% over 60 months → EMI Rs.34,902. Expenses assumed Rs.23,200 (40%
of 58,000, flagged). Surplus = 58000 − 0 − 23200 − 34902 = **Rs.−102**.
Share used 60.2% breaches the 35% cap; both shocks fail.

### Verdict: Don't borrow — "Surplus Rs.−102 below zero after new EMI."

Rule 1, instant. Flip: lower amount or longer tenure until surplus stays
above zero. The honest path the numbers point at: borrow up to ~Rs.7–8.7L
(the computed safe/lender pair), or stretch tenure beyond the 5-year
business max the flow allows — which is exactly the LAP conversation, and
the flow currently cannot price it as LAP.

### Confidence: Medium, 2 unknowns (no-history score, estimated spend)

### Card

Fair 11–17% · ceiling Rs.20,300 · why: vintage, collateral, unknown-score
note · no offer entered · warning: Don't borrow.

---

## 3. Anita, 35 — Hubballi, informal

Brief: delivery rider + home tailoring. Rs.26,000–30,000/month. Two children,
husband unemployed 8 months. Three app loans, Rs.35,000 outstanding at 30%+,
one EMI bounced last month. Wants Rs.1,50,000 e-scooter to double delivery
runs.

### Entered per screen (brief-only)

- Purpose: Vehicle → Vehicle for earning (stated intent: "double delivery
  runs"; productive=True from the sub-purpose). Amount: 1,50,000 (stated).
- Tenure: kept app prefill, 7 years **[flow default; brief silent]**.
- Work: informal (stated). Income: LOW 26,000 + HIGH 30,000 (stated range;
  LOW drives; HIGH is collected, never used — disclosed, not hidden).
- Co-earner: No — husband unemployed 8 months earns nothing (stated; adds 0
  either way).
- Old EMI: **left blank — brief states outstanding (35k), never a monthly
  EMI figure**. Bounce: yes, count 1 (stated). (The results screen prints a
  "no current loans" bounce note at zero EMI — cosmetic; the explicit yes
  still loaded the rate +1% and armed the danger rule, as the notes show.)
- Expenses: **left blank — children stated, amounts never. Estimate-confirm
  accepted.**
- Age 35 (stated). Score: **left blank — brief states no score for Anita** →
  confirmed unknown.
- Backup: **UI default "No backup" — brief silent.** Offer: skipped.
- Scooter extra: **0 — intent stated, no amount; field default.**
  App loans: outstanding 35,000 (stated) + rate **30 [CALL: brief says "30%+";
  recorded the stated floor. Any value above 25 arms the same danger rule,
  so the verdict path is unaffected]**.

### Income: Rs.26,000 safe = Rs.26,000 lender (unverified)

LOW month drives; HIGH 30,000 rides along unused by rule.

### Ceiling: 26000 × 30% − 0 = Rs.7,800

Informal share is 30% flat. Blank old EMI means 0 committed, so the full
7,800 is available for new EMI. Bounce cannot drop informal below its floor.

### Rate: 15.25–21.25%

Two-wheeler base 10.5–24 (mid 17.25). One bounce (stated) +1% → mid 18.25.
Blank score + bounce → 6% wide → 15.25–21.25%. Her 30%+ app loans sit above
even this band's top.

### Amounts: bank 4.63L / safe 3.69L / use 3.69L

84 months. Lender cap 7,800 at 10.5% → Rs.4,63,000. Safe cap 7,800 at her
18.25% mid → Rs.3,69,000. Wanted 1.5L is inside 1.5 × safe — no Borrow Less.

### EMI, surplus, stress: pass — on estimates

1.5L at 18.25% over 84 months → EMI Rs.3,175. Expenses assumed Rs.10,400
(40% of 26,000, flagged). Surplus = 26000 − 0 − 10400 − 3175 = Rs.12,425,
positive. Share used 12.2% — inside the cap, so the armed danger rule
(bounce + 30% app rate + no backup) does not fire. Both shocks pass.

### Verdict: Borrow with conditions (NOT Don't borrow)

"Key spending details missing plus no backup, so limit is estimated."
Rule 3B. **Contrast with older versions: those typed an invented Rs.4,000
monthly EMI and Rs.22,000 expenses for Anita — those two invented numbers
alone flipped her to Don't borrow.** With brief-only data she is Conditional
on estimates, and the flip tells her exactly what earns a recheck: fill
actual EMI + expenses and build 1–2 EMIs backup.

### Confidence: Medium, 2 unknowns (blank score, estimated spend)

Old-EMI blank counts as answered here only because the flow wrote an
explicit 0; the warning still shows that the ceiling assumes no existing EMI.

### Card

Fair 15.25–21.25% · ceiling Rs.7,800 · why: bounce, unknown score · no offer
entered · warning: Conditional.

---

## Appendix — how every silence was handled (the no-black-box list)

Standing engine rules, each exercised above:

- **Expenses blank → assumed 40% of safe income**, flagged estimated, one
  confidence point off, and with no backup the verdict caps at Conditional —
  never clean Borrow. (All three: 44,000 / 23,200 / 10,400.)
- **Tenure unstated → app's prefilled max used** (5 / 5 / 7 years). A choice,
  not a persona fact — disclosed per persona.
- **Backup unstated → UI default "No backup"**, which squeezes
  salaried/self-employed caps to 35% (Priya 55→35, Ravi 45→35) and arms half
  the danger rule. The single most expensive silence in all three runs.
- **Bounce unstated with live loans (Priya) → "unknown"**: +1% rate with a
  confirm note, cap untouched, one confidence point off. At zero EMI the UI
  hides the field and records "no" (Ravi); an explicit yes at zero EMI still
  penalises the rate (Anita).
- **Score blank / no-history → unknown band**: no discount, +2% widen,
  confidence down one, never 0, never 300. (Ravi's exact brief wording
  "never taken a loan" → no-history; Anita's blank → unknown.)
- **Income range (Ravi 40–80k) → LOW end 40,000** per the M4a variable-income
  rule; lender side uses ITR regardless. Informal HIGH month collected, never
  consumed.
- **Co-earner present-tense "earns" (Ravi's wife) → steady**; "unemployed 8
  months" (Anita's husband) → adds nothing. A merely "stopped" earner is
  excluded from safe fully while the lender view still counts half.
- **Branch screens skipped → self-employed/informal need ≥2 filled** or lose
  a badge point; salaried skips are free. (Priya's skipped card screen cost
  nothing; Ravi filled 4 keys; Anita filled 3 keys across 2 screens.)
- **App rate "30%+" → recorded floor 30.** Above the 25% danger-rule tripwire
  under any reading, so the verdict path is identical.
- **Missing income entirely → ceiling 0 → Don't borrow.** (Not triggered;
  all three stated income.)
