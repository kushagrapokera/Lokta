# Rules walkthrough — what each file does, in plain words

Line numbers are given so you can open the code alongside.
No math lives in the screens; all of it lives in `rules/`.

## config.py

Aim: the single number store every file reads.
It targets no questions.

Exact contents:
- Base bands → `BASE_BANDS:7`
- Allowed EMI shares 55/45/30/35 → `MAX_EMI_SHARE_*:17-20`
- 1.5x borrow-less line → `WANT_VS_SAFE_BORROW_LESS:23`
- −20%/+2% stress → `STRESS_*:24-25`
- 25% high-cost line → `HIGH_COST_RATE:26`
- Every rate move → `ADJ_*:29-41`
- 40% spend estimate → `EXPENSE_ESTIMATE_PCT:44`
- 10x collateral trigger → `LAP_SUGGEST_INCOME_MULT:48`
- Retirement ages + product year caps → `RETIRE_AGE*:51-53`

Why only these values: anything two places need must live once, so a live rule change is one edit. Example: changing `MAX_EMI_SHARE_SALARIED` 0.55→0.60 moves Priya's ceiling 46500→52000 with no other file touched.

## questions.py

Aim: your clicks become stable codes.
It targets choice and parsing questions: purpose, branch, score text.

Exact on-screen questions feeding it:
- What do you need the loan for? + Which one fits best? → product + productive flag (`SUB_OPTIONS:7`, `product_for_sub:49`, `is_productive:109`)
- How do you get paid? → branch (`branch_for:64`)
- Credit score? (free text) → score band (`parse_score:80`)

Why only these questions: they are the only answers whose screen wording must never drive logic directly — codes do.

## flow.py

Aim: screen order and follow-ups.
It targets branching questions: work type, sub-purpose, ticket size.

Exact on-screen questions feeding it:
- How do you get paid? → follow-up list (`_branch_steps:57`)
- Which one fits best? → home_lap / consolidate injections
- How much do you want? → 10x income collateral injection

Why only these questions: order and visibility depend solely on branch and ticket size.

## income.py

Aim: real cash versus paper income.
It targets earnings questions: own income, co-earner, ITR.

Exact on-screen questions feeding it:
- Your net monthly in-hand income? → LOW (`normalize_income:12`)
- Does anyone else earn in family? → co-earner exists
- Is that income steady right now? → counts for safe or not
- What does your ITR show per year? → lender base on business branch

Why only these questions: affordability is built from earnings alone; nothing else enters it. Example: Ravi safe 78k vs lender ~44k.

## emi.py

Aim: payment math, period cap, share cap, ceiling.
It targets age, work type, record and backup questions.

Exact on-screen questions feeding it:
- Your age? → longest loan (`max_tenure_months:27`)
- What do you need the loan for? + Which one fits best? → product cap
- How do you get paid? → 55/45/30 share (`max_emi_share:39`)
- Any EMI bounced in last 12 months? → drops one level
- If income stops for 2 months, how will you pay EMI? → none caps at 35%

Why only these questions: payment, period, share and committed EMIs fully fix the ceiling. Example: Priya 110000×0.55−14000 = 46500.

## amount.py

Aim: the two max principals.
It targets no screen directly; it reuses computed caps.

Exact inputs feeding it (`max_amount:17`):
- Lender EMI cap → lender principal at base-min rate
- Safe EMI cap → safe principal at fair-mid rate
- Do you own a shop or house free of any loan? → LAP 60% cap on both
- How much do you want? → 1.5x borrow-less flag

Why only these inputs: a principal is fully fixed by payment capacity, rate, period and collateral cap. Example: Ravi lender 21.2L < safe 27L → use 21.2L.

## fair_rate.py

Aim: the borrower's honest expected interest band.
It targets trust questions: credit history, job stability, card discipline, business vintage, bounce record, and pledged collateral.

Exact on-screen questions feeding it:
- What do you need the loan for? + Which one fits best? → product → base band.
- Credit score? (free text) → score slab.
- How long in your current job? → stable/new job move.
- Employer type? → stable/new job move.
- How much of your credit card limit do you use? → +1 if >70%.
- How old is your business? → −0.5 at 10yr+.
- Do you own a shop or house free of any loan? (+ value, loan-free, type) → −4/−3.
- Any EMI bounced in last 12 months? (+ count) → +1/+2.

Why only these questions: lenders price the rate on trust signals — history, stability, collateral. Income answers a different question: how large an EMI fits, which is the ceiling and the two amounts. Feeding income into the rate would double-count it and let high earners buy artificially cheap bands.

## apr.py

Aim: the all-in yearly cost including fees.
It targets quote questions: rate, fee, tenure.

Exact on-screen questions feeding it:
- Have you already got a loan offer? → offer rate + fee + tenure (`apr:6`)
- Fair band → fair APR band bounds

Why only these questions: same EMI on less cash received defines the true rate. Example: 8L at 11.5% + 2% over 5yr ≈ 12.3%.

## verdict.py

Aim: the final advice with reason and flip.
It targets no screen directly; it reads six computed inputs.

Exact inputs feeding it (`verdict:15`):
- Surplus → rule 1 Don't borrow
- Over-limit + no backup + bounce/30%+ loans → rule 2 Don't borrow
- Wanted vs 1.5x safe → rule 3 Borrow less
- Stress + non-productive → rule 4 Borrow less
- Productive + extra income → rule 5 Conditional
- Other stress fails → Conditional, else Borrow

Why only these inputs: the six locked rules consume exactly these six inputs. Example: Anita −1829 surplus → rule 1; Ravi +20k extra → rule 5.

## confidence.py

Aim: the honesty badge.
It targets silence: skipped and estimated answers.

Exact unknowns feeding it (`confidence:6`):
- Credit score? → unknown score
- Any EMI bounced in last 12 months? → unknown bounce
- Your net monthly in-hand income? → missing income
- Branch follow-ups → fewer than 2 filled
- Total household expenses per month incl rent? → estimated spend
- Total EMI + app-loan + BNPL you pay per month? / Your age? → missing old EMI / age

Why only these questions: silence is the only thing confidence measures. Example: Salim's 5 unknowns → Low.

## card.py

Aim: the one screen for the branch.
It targets price, limit, quote and verdict.

Exact inputs feeding it (`build_card:14`):
- Fair band + notes → fair line
- EMI ceiling → limit line
- Have you already got a loan offer? → FAIR / COSTLY / GOOD compare
- Verdict → warning line

Why only these inputs: a negotiation needs fair price, limit, quote compare and warning. Example: 14% + 1% vs 11.5–13.5% → COSTLY.

## explain.py

Aim: one reason per number.
It targets computed outputs, not questions.

Exact inputs feeding it (`explain:4`):
- Computed amounts → amount_reason
- Computed rate → rate_reason
- Computed ceiling + stress + flags → ceiling_reason

Why only these inputs: every displayed number carries its own inputs.

## engine.py

Aim: fixed order, one bundle.
It targets the whole answers dict.

Exact order in `compute:23`:
- Income → share and ceiling → rate → amounts → EMI, surplus and stress → verdict → confidence → APR → card → reasons

Why only this order: each step feeds the next, so the verdict is always decided last. Example: Anita 28k → 30% → 4.4k → 15.25–21.25% → negative surplus → Don't borrow.

## flask_app.py

Aim: screens only, zero math.
It targets one screen id at a time.

Exact handling:
- Each screen → validate + save (`_apply:191`)
- Each screen → show (`_render:359`)
- Order → `rules/flow.py`
- Numbers → one `compute()` call at results

Why only the current screen's fields per POST: past answers are already in session; re-reading them would risk overwriting.
