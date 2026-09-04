# RULES.md — Every rule, threshold, band and assumption

Single source of truth in code: `rules/config.py`. This file mirrors it.
Format: what · value · why · source or "my judgement".

## 0. Anchor (Sept 2026)

| What | Value | Why | Source |
|------|-------|-----|--------|
| RBI repo rate | 5.25% | Anchor for floating loans, unchanged Feb/Jun/Aug 2026 MPC | RBI / CEIC 30 Aug 2026 |
| Home base band | 8.40–9.80% | PNB 8.40 lowest; SBI 8.50–9.65; HDFC 8.75–9.80; ICICI 8.75–9.85 | Bankopedia Aug 2026, UrbanMoney Aug 2026 |
| Personal bank band | 10–18% | HDFC 9.99; SBI 10; ICICI 10.45; Kotak 10.50; Axis 10.99; thin file to 18 | CreditMitra Jul 2026, Vizzve 2026 |
| Personal NBFC/app band | 12–24% (to 44%) | Bajaj 11–13; Tata 10.99–29.99; KreditBee 14–24; IIFL to 44 | BankBazaar 04 Sep 2026 |
| LAP band | 9.5–11.5% bank, 11–14% NBFC | HDFC 9.50–11.00; SBI 10.10–11.65; Kotak 9.15+; LTV 50–70% | Finnova 24 Jun 2026, ClearTax May 2026 |
| Two-wheeler band | 10.5–24% | ICICI from 10.25; Axis 10.50–25; SBI 11.70–15.70 (EV −0.5); Bajaj to 24 | TradeBrains Feb 2026 |
| Business band | 11–24% (avg 14–20) | PSU 9–14; private 13–18; NBFC 14–26 | IIFL Jul 2026, FlexiLoans Jan 2026 |
| Gold band | 9–12% | Muthoot 9.96; Rupeek 9.48; Fedfina 12 | Bajaj Markets May 2026 |
| Fees (for APR) | home 0.35–0.5; personal 1–2; business 0.5–3; 2W to 2.5; LAP ~1; gold 0.25–1 | Sept 2026 lender pages | Same as bands |
| Car mapping | uses LAP band | Secured auto ~9–11.5%, closest to LAP; my judgement | My judgement |
| Agri mapping | uses home band | Priority-sector secured, closest to home; my judgement | My judgement |

## 1. O4 ceiling + tenure + stress [LOCKED]

| What | Value | Why | Source |
|------|-------|-----|--------|
| FOIR salaried | 55% | Banks allow 50–60% for stable salaried | Bank practice + my judgement |
| FOIR self-employed | 45% | Cash partly proven (ITR only) | Bank practice + my judgement |
| FOIR informal | 30% (35% max w/ 1–2mo buffer, no bounce) | Volatile gig income | My judgement |
| Bounce drops FOIR one level | 55→45, 45→30 | Recent miss = lower trust | My judgement |
| No backup caps salaried at 35% | 35% | Even salary can't cover shock without buffer | My judgement |
| Ceiling | income_safe × FOIR − old_EMI, floor 0 | Affordable new EMI | Definition |
| Missing expenses | assume 40% of income_safe, flag estimated + Low | Missing spend is never zero; typical household 40–60% | My judgement |
| Missing old EMI / age | 0 / 35 + count unknown + surfaced warning in O4 why ("ceiling may be overstated", "age assumed 35") | 0 keeps ceiling honest-side only with warning; age neutral with flag | My judgement |
| Low + no backup cap | at most Conditional Borrow, never clean Borrow | Silence + no buffer must not earn full yes | My judgement |
| Income_safe | M4a LOW + active co-earner only; stopped excluded | Gig use low end; stopped earner adds nothing | QUESTIONS v1.1 M4 lock |
| Income_lender | salaried: same; self: ITR/mo + 50% co; informal: same unverified | Bank believes paper, not cash | QUESTIONS v1.1 M4 lock |
| Max tenure | min(65−age, product max); 60−age if salaried | Retirement + product caps (home 30, LAP 20, personal 5, 2W 7, business 5, gold 3) | Bank norms + my judgement |
| Stress | income −20% OR rate +2%, one shock; pass = surplus > 0 | Gig dip 20% realistic; repo cycle moves 1–2% | RBI 2022–26 history + my judgement |

## 2. O2 two amounts [LOCKED 1.5x]

| What | Value | Why | Source |
|------|-------|-----|--------|
| Lender amount | invert lender EMI cap at base-min rate over max tenure, LTV-cap LAP 60% | What bank's formula yields | Definition + LTV norm |
| Safe amount | invert safe EMI cap at fair-mid over same tenure, same LTV cap | What borrower survives | Definition |
| Recommend | min(lender, safe) | Use tighter of the two | Brief requirement |
| Borrow Less trigger | wanted > 1.5 × safe | Gap breaks surplus + stress | My judgement |
| Large-want collateral surface | wanted > 10 × monthly safe income → ask A-B3 outside b-branch | Big tickets deserve the LAP alternative | My judgement |

## 3. O3 band + APR [LOCKED]

| What | Value | Why | Source |
|------|-------|-----|--------|
| Score 750+ | −1.0% | SBI 8.50 vs 9.65 gap ≈1.15% | SBI slabs + my judgement |
| Score 700–750 | −0.5% | Half-step | My judgement |
| Score 650–700 | +0.5% | Slab down | My judgement |
| Score <650 | +1.5% | Sub-prime slab | My judgement |
| Unknown / no history | no minus, top +2%, width ≥3%, Low conf | Never zero, never 300 | Brief rule + my judgement |
| Stable job 5yr+ MNC/Govt | −0.5% | Salary-account discount 0.25–0.5% | Bank offers + my judgement |
| New job <1yr | +0.5% | Probation risk | My judgement |
| Business 10yr+ | −0.5% | Vintage trust | My judgement |
| 1 bounce | +1%; 2+ bounces +2%; Don't Remember +1% Med | One slab downgrade per miss | My judgement |
| Card >70% | +1% | Revolver risk | My judgement |
| LAP residential / commercial | −4% / −3% vs personal | Real gap 5–6%, kept conservative; needs loan-free + LTV ≤60% | Band gap + my judgement |
| Band width | known-clean 2%; known-risky 3%; unknown wide (≤6%) | Good profile narrow, silence wide | My judgement |
| APR method | EMI on P, solve same EMI on (P−fee) by binary search 0–50% | Upfront fee cuts cash in hand; RBI all-in intent | My judgement |
| Offer APR compare | offer APR from offer rate+fee over offer tenure (std fallback) vs fair APR band | Tenure-aware honest compare on the card | My judgement |
| APR examples | 8L 11.5%+2% 5yr ≈12.3%; home 8.5%+0.35% 20yr ≈8.55%; 1.5L 18%+2.5% 3yr ≈19.7% | Computed by locked method | Computed |

## 4. O1 verdict [LOCKED, first match wins]

| # | Rule | Source |
|---|------|--------|
| 1 | Surplus < 0 → Don't borrow | Definition |
| 2 | FOIR breach + no buffer + (bounce or 30%+ loans) → Don't + consolidate first | My judgement |
| 3 | Wanted > 1.5× safe → Borrow less to safe | Locked 1.5x |
| 4 | Stress fails + non-productive → Borrow less | Locked stress |
| 5 | Productive + extra ≥ 80% EMI → Conditional Borrow; productive unproven → Conditional | My judgement |
| 6 | Stress fails (else) → Conditional; else Borrow | My judgement |

Productive final: M1a provisional; Vehicle unknown until A-B5/A-C4 extra income. Every verdict carries reason + flip condition.

## 5. Confidence + Card

| What | Value | Why | Source |
|------|-------|-----|--------|
| High / Med / Low | 0 / 1–2 / 3+ unknowns (score, bounce, income, branch<2, estimated spend, missing old EMI/age) | Silence lowers badge; bands already widen at source | My judgement |
| Zero current EMI | bounce recorded no, screen skipped; closed-loan past bounce missed (accepted edge) | Bounce needs live loans; rare miss accepted | My judgement |
| Card | fair APR band vs offer APR + 3 whys + ceiling + warning; ≤5 lines | Branch-usable | Brief requirement |

## 6. What we do NOT know

Bank internal FOIR cutoffs and scorecards (we use practice bands); future repo moves (assume stable Sept 2026); moneylender rates (formal lenders only); exact bureau mapping (slabs, not scorecard).
