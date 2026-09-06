# RULES.md — Every rule, threshold, band and assumption

Single source of truth in code: `rules/config.py`. This file mirrors it.
Each rule is written in plain words first, then repeated as a table at the end of its section.
Table format follows the brief: what · value · why · source or "my judgement".

## 0. Anchor (Sept 2026)

Dated context, not a formula input. No calculation consumes the repo number below; it records when the market survey was taken so the bands can be re-anchored later. All bands are advertised minimums for the best profile.

### Dateline: repo rate anchor
- Rule: All floating-rate reasoning is anchored to the Sept 2026 repo rate.
- Source: RBI / CEIC 30 Aug 2026, RBI MPC Aug 2026.
- What: RBI repo rate.
- Value: 5.25%.
- Why: The repo rate was unchanged at the Feb, June and Aug 2026 MPC meetings with a neutral stance, so bands assume stable rates.

### Rule: home base band
- Rule: A best-profile home loan starts from this band before any adjustment.
- Source: Bankopedia Aug 2026, UrbanMoney Aug 2026.
- What: Home base band.
- Value: 8.40–9.80%.
- Why: PNB 8.40 is the lowest advertised; SBI 8.50–9.65; HDFC 8.75–9.80; ICICI 8.75–9.85. Fee 0.35–0.50%. Max 30 years.

### Rule: personal bank base band
- Rule: A best-profile unsecured bank personal loan starts from this band.
- Source: CreditMitra July 2026, Vizzve Feb 2026.
- What: Personal bank base band.
- Value: 10–18%.
- Why: HDFC 9.99; SBI 10; ICICI 10.45; Kotak 10.50; Axis 10.99. 750+ scores get 10–11%, average profiles 14–16%, thin files up to 18%.

### Rule: personal NBFC/app base band
- Rule: App and NBFC personal loans cost more than bank loans. This band is market context only.
- Source: BankBazaar 04 Sep 2026, CreditMitra 2026.
- What: Personal NBFC/app base band.
- Value: 12–24% (up to 44% for some lenders).
- Why: Bajaj 11–13; Tata 10.99–29.99; KreditBee 14–24; Fibe 18–24; IIFL up to 44%.
- Code note: no sub-purpose maps to this band; every unsecured personal loan prices off `personal_bank`. App-loan cost enters only through the danger rule's `app_rate` flag (above 25%, see §4 Rule 2).

### Rule: LAP base band
- Rule: Loan-against-property starts from this band and is capped by collateral value.
- Source: Finnova 24 June 2026, ClearTax May 2026.
- What: LAP base band.
- Value: 9.5–11.5% bank, 11–14% NBFC. LTV 50–70%.
- Why: HDFC 9.50–11.00; SBI 10.10–11.65; Kotak 9.15%+; Axis 10.50–10.95%.

### Rule: two-wheeler base band
- Rule: Scooter and bike loans start from this band.
- Source: TradeBrains Feb 2026.
- What: Two-wheeler base band.
- Value: 10.5–24%.
- Why: ICICI from 10.25; Axis 10.50–25; SBI 11.70–15.70 with 0.5% off for EV; HDFC 14.50%+; Bajaj up to 24%. Fee up to 2.5%.

### Rule: business base band
- Rule: Unsecured business loans start from this band.
- Source: IIFL July 2026, FlexiLoans Jan 2026.
- What: Business base band.
- Value: 11–24% (average 14–20%).
- Why: PSU banks 9–14; private banks 13–18; NBFCs 14–26%.

### Rule: gold base band
- Rule: Gold loans start from this band.
- Source: Bajaj Markets May 2026.
- What: Gold base band.
- Value: 9–12%.
- Why: Muthoot 9.96; Rupeek 9.48; Fedfina 12%.

### Rule: processing fees used for APR
- Rule: The APR calculation adds the lender's upfront fee to the nominal rate.
- Source: Sept 2026 lender pages (same sources as the bands).
- What: Typical fees.
- Value: home 0.35–0.5%; personal 1–2%; business 0.5–3%; two-wheeler up to 2.5%; LAP about 1%; gold 0.25–1%.
- Why: The borrower receives the principal minus the fee, so the all-in cost is higher than the quoted rate.

### Rule: car mapping
- Rule: Car loans reuse the LAP band.
- Source: My judgement.
- What: Car product mapping.
- Value: Uses LAP band.
- Why: Secured auto loans sit near 9–11.5%, closest to LAP among the locked bands.

### Rule: agriculture mapping
- Rule: Agriculture loans reuse the home band.
- Source: My judgement.
- What: Agriculture product mapping.
- Value: Uses home band.
- Why: Priority-sector secured lending sits closest to home-loan pricing.

### Anchor table

| What | Value | Why | Source |
|------|-------|-----|--------|
| RBI repo rate | 5.25% | Anchor for floating loans, unchanged Feb/Jun/Aug 2026 MPC | RBI / CEIC 30 Aug 2026 |
| Home base band | 8.40–9.80% | PNB 8.40 lowest; SBI 8.50–9.65; HDFC 8.75–9.80; ICICI 8.75–9.85 | Bankopedia Aug 2026, UrbanMoney Aug 2026 |
| Personal bank band | 10–18% | HDFC 9.99; SBI 10; ICICI 10.45; Kotak 10.50; Axis 10.99; thin file to 18 | CreditMitra Jul 2026, Vizzve 2026 |
| Personal NBFC/app band | 12–24% (to 44%) | Bajaj 11–13; Tata 10.99–29.99; KreditBee 14–24; IIFL to 44 — market context, unused in code (app cost enters via app_rate > 25% flag) | BankBazaar 04 Sep 2026 |
| LAP band | 9.5–11.5% bank, 11–14% NBFC | HDFC 9.50–11.00; SBI 10.10–11.65; Kotak 9.15+; LTV 50–70% | Finnova 24 Jun 2026, ClearTax May 2026 |
| Two-wheeler band | 10.5–24% | ICICI from 10.25; Axis 10.50–25; SBI 11.70–15.70 (EV −0.5); Bajaj to 24 | TradeBrains Feb 2026 |
| Business band | 11–24% (avg 14–20) | PSU 9–14; private 13–18; NBFC 14–26 | IIFL Jul 2026, FlexiLoans Jan 2026 |
| Gold band | 9–12% | Muthoot 9.96; Rupeek 9.48; Fedfina 12 | Bajaj Markets May 2026 |
| Fees (for APR) | home 0.35–0.5; personal 1–2; business 0.5–3; 2W to 2.5; LAP ~1; gold 0.25–1 | Sept 2026 lender pages | Same as bands |
| Car mapping | uses LAP band | Secured auto ~9–11.5%, closest to LAP; my judgement | My judgement |
| Agri mapping | uses home band | Priority-sector secured, closest to home; my judgement | My judgement |

## 1. EMI ceiling + tenure + stress [LOCKED]

The brief calls the max EMI share FOIR. The code calls it `max_emi_share` in `rules/emi.py`. They are the same number.

### Rule: salaried cap
- Rule: A salaried borrower may spend at most this share of safe income on all EMIs together.
- Source: Bank practice + my judgement.
- What: Max EMI share, salaried.
- Value: 55%.
- Why: Banks in practice allow 50–60% for stable salaried income. 55% is the middle.

### Rule: self-employed cap
- Rule: A self-employed borrower gets a lower cap because only part of the cash income is proven on paper.
- Source: Bank practice + my judgement.
- What: Max EMI share, self-employed.
- Value: 45%.
- Why: The bank counts ITR income, not full cash income, so the safe share is lower.

### Rule: informal cap
- Rule: An informal or gig borrower gets the lowest cap because income changes every month.
- Source: My judgement.
- What: Max EMI share, informal.
- Value: 30% flat. The code never raises it: `MAX_EMI_SHARE_INFORMAL_WITH_BUFFER` (35%) acts only as the no-backup ceiling for the other branches, not as an uplift for informal.
- Why: Volatile income needs a larger safety margin.

### Rule: bounce drops the cap one level, informal is the floor
- Rule: An explicit bounced-EMI answer ("yes") in the last 12 months lowers the cap one full level, down to a floor of 30%.
- Source: My judgement.
- What: Bounce penalty on the cap.
- Value: 55→45, 45→30, 30 stays 30. Applies only on explicit "yes"; "Don't Remember"/unknown leaves the cap untouched (it still adds +1% to the rate, see §3).
- Why: A recent missed payment lowers trust, so the affordable share drops. Informal is already at the floor, so a bounce cannot drop it further; the danger-combination verdict rule handles that case instead.

### Rule: no backup caps every branch at 35%
- Rule: With no backup savings (`buffer` = none), no branch may use a share above 35%. Any other buffer value (family, 1–2, 3+) leaves the base share unchanged.
- Source: My judgement.
- What: No-backup cap.
- Value: 35% for all branches (salaried 55→35, self-employed 45→35, informal already 30 and unchanged).
- Why: Without any buffer, one income shock breaks the EMI, so the ceiling stays low regardless of work type.

### Rule: ceiling formula
- Rule: The EMI ceiling is the affordable new EMI per month.
- Source: Definition.
- What: Ceiling.
- Value: income_safe × max share − old EMI, minimum 0.
- Why: Total EMIs must fit inside the allowed share; old EMIs are already committed.

### Rule: lender EMI cap uses the same share on lender income
- Rule: The lender side reuses the same max-share percentage, applied to lender income instead of safe income.
- Source: My judgement.
- What: Lender EMI cap.
- Value: income_lender × same max share − old EMI, minimum 0.
- Why: The two-number split compares the bank's view against the borrower's view under one shared share rule; only the income input differs.

### Rule: missing expenses are estimated, never zero
- Rule: If household expenses are left blank while income is above zero, the app assumes spending instead of using zero.
- Source: My judgement.
- What: Missing-expenses fallback.
- Value: Assume 40% of safe income, flag estimated, lower confidence.
- Why: Missing spending is never zero in real households; typical spend is 40–60% of income. Zero would inflate surplus and wrongly allow borrowing.

### Rule: missing old EMI and age defaults
- Rule: Blank old EMI and blank age get safe defaults plus a visible warning.
- Source: My judgement.
- What: Missing old EMI / age.
- Value: Old EMI defaults to 0, age defaults to 35; each counts as unknown and the reason line warns that the ceiling may be overstated or the tenure will be rechecked.
- Why: Zero old EMI keeps the ceiling on the honest side only when flagged; 35 is a neutral working age.

### Rule: low detail plus no backup never earns a clean yes
- Rule: Estimated spending together with no backup caps the verdict below a clean Borrow.
- Source: My judgement.
- What: Low-detail cap.
- Value: At most Conditional Borrow, never clean Borrow.
- Why: Silence plus no buffer must not earn a full yes.

### Rule: safe income definition
- Rule: Safe income counts only money that actually arrives now.
- Source: QUESTIONS v1.1 M4 lock.
- What: income_safe.
- Value: Your LOW month plus co-earner income only if that earner is still active; a stopped earner is excluded fully.
- Why: Gig income uses the low end; a stopped earner adds nothing.

### Rule: lender income definition
- Rule: Lender income is what a bank would count, not what you receive.
- Source: QUESTIONS v1.1 M4 lock.
- What: income_lender.
- Value: Salaried: same as safe. Self-employed: ITR per month plus 50% of any listed co-earner (even a stopped one — the lender view still counts half; only the safe number excludes the stopped earner fully). Informal: same as safe but unverified.
- Why: Banks believe paper income, not cash in hand.
- Code note: the informal screen also collects a HIGH month alongside LOW, but the engine never consumes it; LOW drives both safe and lender income.

### Rule: maximum tenure
- Rule: Loan years are limited by retirement age and by product. This sets the typical maximum, not the pace used in math (see chosen-pace rule below).
- Source: Bank norms + my judgement.
- What: Max tenure.
- Value: min(65 − age, product max); 60 − age if salaried. Product caps: home 30, LAP 20, personal 5, two-wheeler 7, business 5, gold 3 years.
- Why: EMIs should end near retirement; each product has a market-standard maximum.

### Rule: chosen pace governs all math
- Rule: The borrower's chosen repayment years (`desired_years`) set the tenure every calculation uses. Missing means the typical max, so old answers behave as before.
- Source: My judgement.
- What: Pace tenure.
- Value: months = max(6, chosen years × 12). A choice above the typical max is honoured and flagged (`tenure_capped`), never clamped. EMI, surplus, stress, both amounts and fair APR all run at this pace; the Results screen additionally shows the same loan at the typical max (`alt_emi`, total interest) as a trade-off.
- Why: The borrower repays at their own pace; the max is only the comparison point.

### Rule: stress test
- Rule: Every proposal faces one shock at a time, and must survive both.
- Source: RBI 2022–26 history + my judgement.
- What: Stress.
- Value: Income −20% OR rate +2%, each shock computed separately at the chosen pace; pass means surplus stays above zero under both (the worse of the two decides).
- Why: A 20% gig dip is realistic and policy rates have moved 1–2% in a cycle.

### Ceiling table

| What | Value | Why | Source |
|------|-------|-----|--------|
| Max share salaried | 55% | Banks allow 50–60% for stable salaried | Bank practice + my judgement |
| Max share self-employed | 45% | Cash partly proven (ITR only) | Bank practice + my judgement |
| Max share informal | 30% flat (no uplift; 35% const is the no-backup cap for other branches) | Volatile gig income | My judgement |
| Bounce drops share one level | 55→45, 45→30, 30 stays 30; explicit yes only | Recent miss = lower trust; informal already at floor | My judgement |
| No backup caps all branches at 35% | 35%; other buffers leave base unchanged | No buffer means one shock breaks the EMI, any work type | My judgement |
| Ceiling | income_safe × share − old_EMI, floor 0 | Affordable new EMI | Definition |
| Lender EMI cap | income_lender × same share − old_EMI, floor 0 | Same share on paper income; only the income input differs | My judgement |
| Missing expenses | assume 40% of income_safe, flag estimated + Low | Missing spend is never zero; typical household 40–60% | My judgement |
| Missing old EMI / age | 0 / 35 + count unknown + warning in reason | 0 keeps ceiling honest-side only with warning; age neutral with flag | My judgement |
| Low + no backup cap | at most Conditional Borrow, never clean Borrow | Silence + no buffer must not earn full yes | My judgement |
| income_safe | LOW + active co-earner only; stopped excluded | Gig use low end; stopped earner adds nothing | QUESTIONS v1.1 M4 lock |
| income_lender | salaried: same; self: ITR/mo + 50% of any listed co (even stopped); informal: same unverified (HIGH month collected but unused) | Bank believes paper, not cash | QUESTIONS v1.1 M4 lock |
| Max tenure | min(65−age, product max); 60−age if salaried — typical max only | Retirement + product caps (home 30, LAP 20, personal 5, 2W 7, business 5, gold 3) | Bank norms + my judgement |
| Chosen pace | desired_years × 12 (floor 6mo, missing = max); above-max honoured + flagged | Borrower repays at own pace; max is the trade-off | My judgement |
| Stress | income −20% OR rate +2% at chosen pace, must pass both; pass = surplus > 0 | Gig dip 20% realistic; repo cycle moves 1–2% | RBI 2022–26 history + my judgement |

## 2. Two amounts [LOCKED 1.5x]

### Rule: lender amount
- Rule: The lender amount is what the bank's own formula would sanction.
- Source: Definition + LTV norm.
- What: Lender amount.
- Value: Convert the lender EMI cap back into a principal at the base-minimum rate over the chosen pace (not the max); for LAP also cap at 60% of collateral value. Rounded to the nearest Rs.1000. Unknown/education/unsure products price off `personal_bank`; car prices off `lap_bank`.
- Why: It mirrors the bank's view using paper income and the cheapest advertised rate.

### Rule: safe amount
- Rule: The safe amount is what the borrower can carry without breaking surplus and stress.
- Source: Definition.
- What: Safe amount.
- Value: Convert the safe EMI cap back into a principal at the fair-mid rate over the same chosen pace, with the same 60% LAP cap and the same Rs.1000 rounding.
- Why: It uses real cash income and the borrower's actual expected rate.

### Rule: recommended amount
- Rule: The borrower should use the tighter of the two numbers.
- Source: Brief requirement.
- What: Recommend.
- Value: min(lender, safe).
- Why: The safe number protects the borrower; the lender number protects approval. The smaller satisfies both.

### Rule: borrow-less trigger
- Rule: A wanted amount far above the safe amount becomes Borrow Less.
- Source: My judgement, locked at 1.5x.
- What: Borrow Less trigger.
- Value: Wanted above 1.5 × safe amount (a loan-to-safe-capacity comparison; different quantity from the 10x income check below, intentionally — this one governs the verdict, the other only decides whether to surface an extra question).
- Why: Beyond this gap the surplus and stress tests break in practice.

### Rule: large-want collateral question
- Rule: Very large tickets earn the collateral question even outside the business branch.
- Source: My judgement.
- What: Large-want surface.
- Value: Wanted above 10 × monthly safe income surfaces the property question.
- Why: Big tickets deserve the secured LAP alternative to be checked.

### Amounts table

| What | Value | Why | Source |
|------|-------|-----|--------|
| Lender amount | invert lender EMI cap at base-min rate over chosen pace, LTV-cap LAP 60%, round Rs.1000 | What bank's formula yields | Definition + LTV norm |
| Safe amount | invert safe EMI cap at fair-mid over same pace, same LTV cap + rounding | What borrower survives | Definition |
| Recommend | min(lender, safe) | Use tighter of the two | Brief requirement |
| Borrow Less trigger | wanted > 1.5 × safe | Gap breaks surplus + stress | My judgement |
| Large-want collateral surface | wanted > 10 × monthly safe income → ask property Q outside business branch | Big tickets deserve the LAP alternative | My judgement |

## 3. Fair rate band + APR [LOCKED]

### Rule: fair-mid rate
- Rule: The single rate used for amount and EMI math is the midpoint of the adjusted fair band.
- Source: Definition.
- What: Fair-mid rate.
- Value: (adjusted band low + adjusted band high) / 2, after all score, job, bounce, card and collateral adjustments and clamping.
- Why: Amount inversion and EMI need one rate; the midpoint of the borrower's own band is the neutral choice inside a band-only design.

### Rule: adjustment clamp to the base band
- Rule: Stacked adjustments can never push the band outside real-world bounds.
- Source: My judgement.
- What: Adjustment clamp.
- Value: The adjusted low end never drops below the product base floor; the high end never exceeds base ceiling + 2%.
- Why: Evidence floors (for example personal bank 10%) stay intact no matter how many discounts stack, as in Priya's −1.5%.

### Rule: score 750+
- Rule: Top credit scores earn the largest discount.
- Source: SBI slabs + my judgement.
- What: Score 750+ adjustment.
- Value: −1.0%.
- Why: The SBI 8.50 vs 9.65 slab gap is about 1.15%.

### Rule: score 700–750
- Rule: Good scores earn half the top discount.
- Source: My judgement.
- What: Score 700–750 adjustment.
- Value: −0.5%.
- Why: Half-step between top and average slabs.

### Rule: score 650–700
- Rule: Below-average scores add cost.
- Source: My judgement.
- What: Score 650–700 adjustment.
- Value: +0.5%.
- Why: One slab below average pricing.

### Rule: score below 650
- Rule: Weak scores add a full slab of cost.
- Source: My judgement.
- What: Score below 650 adjustment.
- Value: +1.5%.
- Why: Sub-prime slab pricing.

### Rule: unknown or no-history score
- Rule: An unknown score is never treated as zero or as 300.
- Source: Brief rule + my judgement.
- What: Unknown score handling.
- Value: No discount, band widened by +2%, minimum width kept, confidence lowered.
- Why: Silence must widen the range and lower the badge, never invent a number.

### Rule: stable job discount
- Rule: Long, stable salaried employment earns a small discount. Either condition alone is enough.
- Source: Bank offers + my judgement.
- What: Stable job — 5yr+ vintage OR MNC/Govt/large employer (salaried branch only).
- Value: −0.5%.
- Why: Salary-account and corporate discounts run 0.25–0.5%. The stable check wins: a <1yr vintage at an MNC still gets −0.5%, not the new-job loading.

### Rule: new job loading
- Rule: A very new job at a non-qualifying employer adds cost.
- Source: My judgement.
- What: Job under 1 year (salaried branch only, and only when the stable rule above does not fire).
- Value: +0.5%.
- Why: Probation and attrition risk.

### Rule: old business discount
- Rule: A long-running business earns a small discount.
- Source: My judgement.
- What: Business 10yr+ (self-employed branch only).
- Value: −0.5%.
- Why: Vintage and survival signal trust.

### Rule: bounce loading
- Rule: Missed payments add cost per miss.
- Source: My judgement.
- What: Bounce adjustment.
- Value: 1 bounce +1%; 2 or more +2%; Don't Remember counts as 1 with Medium confidence.
- Why: Each recent miss downgrades the borrower roughly one slab.

### Rule: high card utilisation
- Rule: Maxed-out cards add cost.
- Source: My judgement.
- What: Card use above 70% (salaried branch only).
- Value: +1%.
- Why: Revolving-balance behaviour signals stress.

### Rule: LAP collateral discount
- Rule: Pledging a loan-free property cuts the rate versus unsecured personal credit.
- Source: Band gap + my judgement.
- What: LAP discount (self-employed branch only in code).
- Value: Residential −4%, commercial −3% on any loan-free collateral value. The code applies no LTV gate to the rate — the 60% LTV cap binds the two amounts, not the discount. Collateral answers collected outside the self-employed branch (home-LAP purpose, 10x large-want injection) therefore do not move the rate.
- Why: The real secured-vs-unsecured gap is 5–6%; the rule keeps 3–4% to stay conservative.

### Rule: band width
- Rule: The band is always a range, never one number.
- Source: My judgement.
- What: Band width.
- Value: Clean (adjustment at or below −1%) 2%; anything else known 3%; unknown score or any bounce 3–6% (base width + 2% widen, capped at 6%; very wide bases such as two-wheeler/business use 4% + widen); never below 1.5%.
- Why: Good profiles earn narrow ranges; silence or a bounce earns wide ones.

### Rule: APR method
- Rule: APR shows the all-in yearly cost including the upfront fee.
- Source: My judgement.
- What: APR method.
- Value: EMI is computed on the full principal at the nominal rate; APR is the rate that gives the same EMI on principal-minus-fee, found by binary search from 0–50%.
- Why: The fee reduces cash in hand on day one, so the true yearly cost is higher than the quoted rate. This follows the RBI all-in disclosure intent.

### Rule: offer compare
- Rule: Any lender quote is compared on APR, not on nominal rate.
- Source: My judgement.
- What: Offer APR compare.
- Value: Offer APR from offer rate plus fee over the offer tenure versus the fair APR band. The fair APR band is computed over the chosen pace using that same fee input (offer fee, else 0); the on-screen offer-tenure field is prefilled from the age/product standard (capped at 60 months except home/LAP), and the card falls back to the chosen pace when no tenure is entered.
- Why: Tenure-aware comparison is the only honest way to call a quote fair or costly.

### Rule: APR worked examples
- Rule: The locked method reproduces known examples.
- Source: Computed.
- What: APR examples.
- Value: 8L personal 11.5% + 2% fee over 5yr ≈ 12.3%; home 8.5% + 0.35% over 20yr ≈ 8.55%; 1.5L two-wheeler 18% + 2.5% over 3yr ≈ 19.7%.
- Why: Computed by the locked binary-search method.

### Rate table

| What | Value | Why | Source |
|------|-------|-----|--------|
| Score 750+ | −1.0% | SBI 8.50 vs 9.65 gap ≈1.15% | SBI slabs + my judgement |
| Score 700–750 | −0.5% | Half-step | My judgement |
| Score 650–700 | +0.5% | Slab down | My judgement |
| Score <650 | +1.5% | Sub-prime slab | My judgement |
| Unknown / no history | no minus, top +2%, width ≥3%, Low conf | Never zero, never 300 | Brief rule + my judgement |
| Stable job 5yr+ OR MNC/Govt/large (salaried) | −0.5% (wins over new-job loading) | Salary-account discount 0.25–0.5% | Bank offers + my judgement |
| New job <1yr (salaried, non-stable only) | +0.5% | Probation risk | My judgement |
| Business 10yr+ (self-employed only) | −0.5% | Vintage trust | My judgement |
| 1 bounce | +1%; 2+ bounces +2%; Don't Remember +1% Med (rate only, cap untouched) | One slab downgrade per miss | My judgement |
| Card >70% (salaried only) | +1% | Revolver risk | My judgement |
| LAP residential / commercial (self-employed only) | −4% / −3% vs personal on any loan-free value; no LTV gate on rate (60% binds amounts) | Real gap 5–6%, kept conservative | Band gap + my judgement |
| Band width | clean (adj ≤ −1%) 2%; known else 3%; unknown/bounce 3–6% (wide bases 4% + widen) | Good profile narrow, silence/bounce wide | My judgement |
| Fair-mid rate | midpoint of adjusted band after clamp | Single neutral rate for amount and EMI math | Definition |
| Adjustment clamp | low ≥ base floor; high ≤ base ceiling + 2% | Evidence bounds survive stacked adjustments | My judgement |
| APR method | EMI on P, solve same EMI on (P−fee) by binary search 0–50% | Upfront fee cuts cash in hand; RBI all-in intent | My judgement |
| Offer APR compare | offer APR from offer rate+fee over offer tenure (prefill = age/product standard; fallback = chosen pace) vs fair APR band at chosen pace with same fee | Tenure-aware honest compare on the card | My judgement |
| APR examples | 8L 11.5%+2% 5yr ≈12.3%; home 8.5%+0.35% 20yr ≈8.55%; 1.5L 18%+2.5% 3yr ≈19.7% | Computed by locked method | Computed |

## 4. Verdict [LOCKED, first match wins]

The verdict is decided last, after ceiling, amounts, rate, EMI, surplus and stress are known. The first matching rule wins. Every verdict carries a reason and a flip condition.

### Rule 1: negative surplus
- Rule: If the monthly surplus after the new EMI is below zero, the answer is Don't borrow.
- Source: Definition.
- What: Surplus below zero.
- Value: Don't borrow.
- Why: The household cannot cover existing spend plus the new EMI.

### Rule 2: danger combination
- Rule: Breaching the EMI-share cap with no backup plus an explicit bounce or high-cost loans is Don't borrow.
- Source: My judgement.
- What: Cap breach + no buffer + (explicit bounce "yes" or `app_rate` above 25%).
- Value: Don't borrow, consolidate costly loans first.
- Why: Over-limit borrowing with no cushion and a damaged record fails together. "Don't Remember" bounce does not trigger this rule (rate only); the app-loan trigger is 25%, not 30%.

### Rule 3: wanted far above safe
- Rule: Asking far more than the safe amount becomes Borrow Less.
- Source: Locked 1.5x.
- What: Wanted above 1.5 × safe.
- Value: Borrow less, down to the safe number.
- Why: The gap breaks surplus and stress in practice.

### Rule 3B: estimated spend plus no backup
- Rule: Missing-spend estimates together with no backup cap the verdict below a clean yes.
- Source: My judgement.
- What: Estimated expenses (40% assumption active) + `buffer` none.
- Value: Borrow with conditions. Fires after the Borrow Less check and before the stress rules, so it can still be preceded by Don't borrow or Borrow less but never by a clean Borrow.
- Why: Silence plus no buffer must not earn a full yes.

### Rule 4: stress fails on a non-earning loan
- Rule: A loan that fails the shock test and earns nothing becomes Borrow Less.
- Source: Locked stress.
- What: Stress fails + non-productive.
- Value: Borrow less, with a longer-tenure warning.
- Why: A consumption loan has no extra income to cover the shock.

### Rule 5: productive loans
- Rule: A loan that earns income is treated more leniently, with conditions, and never earns a clean Borrow on projected income alone.
- Source: My judgement.
- What: Productive + extra income at or above 80% of EMI.
- Value: Conditional Borrow. Productive but unproven or thin extra income is also Conditional. Deliberate stance: projected income is never certain enough for a clean yes, no matter how strong the proof.
- Why: Extra monthly income covers the EMI; unproven income needs confirmation first; even proven extra income is a forecast, so the verdict keeps its conditions.

### Rule 6: stress fails otherwise, else Borrow
- Rule: Failing stress on any other loan is Conditional; passing everything is Borrow.
- Source: My judgement.
- What: Stress fails (else) → Conditional; else Borrow.
- Value: As stated.
- Why: A pass today that breaks under shock needs a backup before borrowing.

Productive is settled at Q1 for clear cases (earning assets True, including home-buy/build; wedding, medical and own-use vehicles False) and finalised by the extra-income answers for vehicles and business; home and education default True, vehicle stays undecided until those answers arrive. Unknown stays undecided until those answers arrive.

The O4 stress case is always computed and shown regardless of which verdict rule matched. Verdict rules never suppress it.

### Verdict table

| # | Rule | Source |
|---|------|--------|
| 1 | Surplus < 0 → Don't borrow | Definition |
| 2 | Share breach + no buffer + (explicit bounce yes or app_rate > 25%) → Don't + consolidate first | My judgement |
| 3 | Wanted > 1.5× safe → Borrow less to safe | Locked 1.5x |
| 3B | Estimated spend + no buffer → Borrow with conditions (never clean Borrow) | My judgement |
| 4 | Stress fails + non-productive → Borrow less | Locked stress |
| 5 | Productive + extra ≥ 80% EMI → Conditional Borrow; productive unproven → Conditional; never clean Borrow on projected income | My judgement |
| 6 | Stress fails (else) → Conditional; else Borrow | My judgement |

## 5. Confidence + Card

### Rule: confidence badge
- Rule: The badge counts how many answers were skipped or estimated.
- Source: My judgement.
- What: High / Medium / Low.
- Value: 0 unknowns = High; 1–2 = Medium; 3+ = Low. Unknowns counted: score (incl. no-history), bounce (unknown/Don't Remember only), missing income, fewer than 2 branch answers on the self-employed/informal branches only (salaried branch answers never touch the badge), estimated spend, blank old EMI or blank age. An explicit old EMI of 0 counts as answered, not unknown.
- Why: Silence lowers the badge. The numbers already widen at their source; the badge only labels it.

### Rule: zero current EMI
- Rule: With zero current EMI recorded as no bounce, there is no bounce penalty.
- Source: My judgement, accepted edge.
- What: Zero-EMI bounce handling.
- Value: No cap drop and no rate loading when bounce is recorded no; but an explicit bounce "yes" alongside zero EMI still loads the rate (+1%/+2%) and drops the cap — the code does not auto-clear it. A past bounce on a closed loan recorded as no is missed and accepted as a rare edge.
- Why: A bounce check needs live loans to be meaningful, but an explicit yes is never ignored.

### Rule: negotiation card
- Rule: The card fits on one phone screen for use in the branch.
- Source: Brief requirement.
- What: Card.
- Value: Fair APR band versus offer APR, 3 reason bullets, EMI ceiling, 1 warning. Maximum 5 lines.
- Why: The borrower can hold it up against any quote.
- Wiring: the Results screen (`templates/results.html`) and the Card view (`templates/card.html`, plus `/card/download`) both render one shared bundle built by `_results_bundle()` in `flask_app.py` from a single `compute()` call in `rules/engine.py`, so numbers cannot drift between the two views. The `.txt` download prints `card.lines`; the HTML card lays out those same numbers directly.

### Confidence + card table

| What | Value | Why | Source |
|------|-------|-----|--------|
| High / Med / Low | 0 / 1–2 / 3+ unknowns (score incl. no-history, bounce unknown only, missing income, branch<2 on self/informal only, estimated spend, blank old EMI/age; explicit 0 EMI is known) | Silence lowers badge; bands already widen at source | My judgement |
| Zero current EMI | no penalty when bounce recorded no; explicit yes still penalised even at 0 EMI; closed-loan past bounce missed (accepted edge) | Bounce needs live loans, but explicit yes is never ignored | My judgement |
| Card | fair APR band vs offer APR + 3 whys + ceiling + warning; ≤5 lines | Branch-usable | Brief requirement |

## 6. What we do NOT know

Bank internal EMI-share cutoffs and scorecards (we use practice bands); future repo moves (assume stable Sept 2026); moneylender rates (formal lenders only); exact bureau mapping (slabs, not scorecard).
