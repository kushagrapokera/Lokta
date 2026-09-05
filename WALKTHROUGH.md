Here is a walkthrough you can speak in the interview. It traces each answer to the exact output it changes.
1. Start with the flow - 30 seconds
All answers go into one dictionary. rules/engine.py:23 compute() runs in fixed order: income -> ceiling O4 -> rate O3 -> amounts O2 -> EMI + surplus + stress -> verdict O1 -> confidence + card. UI in app.py collects answers only, it does no calculation.
2. Where each answer goes
M1 purpose + sub-purpose:
Goes to two places. First, sub-purpose sets product in rules/questions.py:47. Product selects the starting band in rules/fair_rate.py:6 from rules/config.py:7. Example: home 8.4-9.8, personal 10-18, LAP 9.5-11.5. Second, sub-purpose sets productive flag in rules/questions.py:96. Earning use = True, wedding/travel/own vehicle = False. This flag is read in rules/verdict.py:19 for step 5 and 6.
M2 wanted amount:
Goes to three places. In rules/engine.py:51 it is converted to new_emi at fair-mid rate over standard tenure. That new_emi is used for surplus, FOIR actual, and stress. In rules/amount.py:40 it is compared to 1.5 * safe. If larger, verdict becomes Borrow less. In O2 it is shown next to lender/safe for comparison.
M3 a/b/c income type:
This is the switch. In rules/emi.py:37 it selects FOIR cap: a=55%, b=45%, c=30%. In rules/income.py:22 it selects how lender income is read. In app.py:13 it selects which branch questions appear. In rules/emi.py:26 it selects retirement age: 60 if a, 65 otherwise.
M4 income + co-earner:
Creates two separate incomes in rules/income.py:12. income_safe = your LOW + co-earner only if active. Stopped earner is excluded fully. income_lender = for b, ITR/12 + 50% co-earner, for others, self + 50% co-earner. income_safe drives ceiling O4 and safe amount. income_lender drives lender amount only. This split is why Ravi has lender 21.2L and safe 27L - bank sees ITR 35k, we see actual 78k.
M5 old EMI + bounce:
Old EMI is subtracted directly: ceiling = income_safe * FOIR - old_emi in rules/emi.py:55. Bounce = yes drops FOIR one level in rules/emi.py:43: 55->45, 45->30. Bounce also adds to rate in rules/fair_rate.py:65: +1% for 1, +2% for 2+. Bounce + FOIR breach + no buffer triggers Don't borrow in rules/verdict.py:29. If old EMI = 0, we record bounce = no and skip the penalty. This is tested in tests/test_adaptive.py:35.
M6 expenses:
Used in rules/engine.py:53: surplus = income_safe - old - expenses - new_emi. If surplus < 0, verdict is Don't borrow in rules/verdict.py:25. If expenses are 0 or missing and income > 0, we do not use 0. We assume 40% of safe income in rules/engine.py:39, set estimated_exp=True, and cap verdict at Conditional in rules/verdict.py:37.
M7 age:
Used only for tenure in rules/emi.py:26: min(65-age, product-max), 60-age if salaried. Shorter tenure = higher EMI for same principal, and lower max amount. This is why Lakshmi at 55 gets only 60 months for home loan and EMI 62k for 30L.
M8 score:
Used only for rate in rules/fair_rate.py:31. 750+ = -1.0%, 700-750 = -0.5%, 650-700 = +0.5%, below 650 = +1.5%. Unknown / no history = no minus, width +2%, confidence down. Unknown is never treated as 300. Width is 2% if clean, 3% if risky, up to 6% if unknown.
M9 buffer:
Modifies FOIR in rules/emi.py:48. If buffer = none, cap is limited to 35% even if salaried. It is also read in verdict step 2: FOIR breach + none + bounce/high-cost = Don't borrow.
S1 offer rate + fee + tenure:
Does not change verdict, ceiling, amount, or fair rate. It is used only in rules/card.py:26 to compute offer APR and compare to fair APR band. If offer APR > fair top, card shows COSTLY.
Branch questions - each moves a number:
- A-S1 job vintage + employer: stable 5yr+ MNC = -0.5% in O3.
- A-S3 card >70% = +1% in O3.
- A-B1 business 10yr+ = -0.5% in O3.
- A-B2 ITR annual: sets lender income for b-branch, creates the lender vs safe gap in O2.
- A-B3 collateral value + free + type: if loan-free, -4% residential / -3% commercial in O3, and caps both amounts at 60% of value in rules/amount.py:32. This routes Ravi from personal 16%+ to LAP 9.5-11%.
- A-B5 / A-C4 extra income per month: finalizes productive for vehicle/business. If extra >= 80% of new EMI, verdict = Borrow with conditions in rules/verdict.py:48.
- A-C3 app outstanding + rate: if rate > 25%, sets high-cost flag in rules/verdict.py:22 for the danger rule.
Confidence:
Counted in rules/confidence.py:4. +1 for unknown score, unknown bounce, missing income, branch <2 filled, estimated expenses, missing old EMI/age. 0 = High, 1-2 = Medium, 3+ = Low. It does not change numbers, it labels them. Widening already happened inside rate.
3. Close with one trace - 60 seconds
Take Anita: income_safe 28k, FOIR 30% because c + bounce, ceiling = 28k*0.30 - 4k = 4.4k. Wanted 1.5L gives EMI 3.8k. Surplus = 28k - 4k - 22k - 3.8k = negative, so verdict step 1 fires Don't borrow. Rate = 2W base +1% bounce + widen for unknown = 15.25-21.25%. Card shows ceiling and warning. Change any input and only that path updates because all numbers come from rules/config.py.
Say this last line - interviewers test it: only config.py holds numbers, so a live change is one edit.