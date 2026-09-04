# Borrower Copilot — Thresholds & Rules (India, as of Sept 2026)

Source date: 4 Sept 2026. RBI repo 5.25% unchanged (Feb/June/Aug 2026 MPC, neutral stance).
All bands are advertised minimums for best profile (750+ salaried). App starts here, then adjusts.

## 0. Base anchor

| What | Value (Sept 2026) | Why | Source |
|------|-------------------|-----|--------|
| RBI repo rate | 5.25% | Anchor for all floating loans, stable now | RBI / CEIC 30 Aug 2026, RBI MPC Aug 2026 |
| Home loan | 8.40% - 9.80% | PNB 8.40% lowest, SBI 8.50-9.65%, HDFC 8.75-9.80%, ICICI 8.75-9.85%. Fee 0.35-0.50%. 30yr max | Bankopedia Aug 2026, UrbanMoney Aug 2026 |
| Personal bank | 10% - 18% | HDFC 9.99%, SBI 10%, ICICI 10.45%, Kotak 10.50%, Axis 10.99%. 750+ gets 10-11%, avg 14-16%, thin file 16-18% | CreditMitra July 2026, Vizzve Feb 2026 |
| Personal NBFC/app | 12% - 24% (up to 44%) | Bajaj 11-13%, Tata 10.99-29.99%, KreditBee 14-24%, Fibe 18-24%, IIFL up to 44% | BankBazaar 04 Sep 2026, CreditMitra 2026 |
| LAP | 9.5-11.5% bank, 11-14% NBFC | HDFC 9.50-11.00%, SBI 10.10-11.65%, Kotak 9.15%+, Axis 10.50-10.95%. LTV 50-70% | Finnova 24 June 2026, ClearTax May 2026 |
| Two-wheeler | 10.5% - 24% | ICICI from 10.25%, Axis 10.50-25%, SBI 11.70-15.70% (0.5% EV off), HDFC 14.50%+, Bajaj up to 24%. Fee up to 2.5% | TradeBrains Feb 2026 |
| Business unsecured | 11% - 24% (avg 14-20%) | PSU 9-14%, Private 13-18%, NBFC 14-26% | IIFL July 2026, FlexiLoans Jan 2026 |
| Gold | 9% - 12% | Muthoot 9.96%, Rupeek 9.48%, Fedfina 12% | Bajaj Markets May 2026 |

## 1. O4 — EMI ceiling (do first, everything needs it) [LOCKED]

- FOIR cap (Total EMI / Income) — LOCKED:
  - Salaried stable + buffer: 55%
  - Self-employed with ITR: 45%
  - Informal / 0 backup / bounce in 12m / 30%+ active loans: 30% (35% max if buffer 1-2 months, no bounce)
  - Bounce drops one level (55%->45%, 45%->30%). No backup caps at 35% even if salaried.
  - Why: Indian banks use 40-60% in practice. Lower cap for volatile income = safety. My judgement + bank practice.
- Ceiling = Income_safe x FOIR_cap - Old_EMI (M5a). Floor 0.
  - Income_safe = M4a LOW end + only active co-earner (M4b). Stopped earner excluded entirely.
  - Income_lender = salaried: same, self-employed: ITR/mo (A-B2), informal: same as safe but unverified.
- Max tenure = min(65 - age, 60 - age if salaried conservative, product max: home 30yr, LAP 15-20yr, personal 5yr, two-wheeler 5-7yr, business 5yr)
- Tenure table: show same loan over short vs long tenure EMI + total interest.
- Stress — LOCKED: recompute surplus with income -20% OR rate +2% (one shock at a time, not both). Pass = surplus >0. Fail + non-productive = Borrow Less. Fail + productive with extra income covering EMI = Conditional Borrow.
- Why line: "Ceiling Rs.X because (income Y x FOIR Z% - old EMI W)".

## 2. O2 — Two amounts

- Lender amount = EMI_capacity_lender x tenure factor at lender rate, capped by collateral LTV (LAP 50-60% of A-B3 value).
  - Uses Income_lender, bank FOIR, ITR only for self-employed.
- Safe amount = EMI_capacity_safe x tenure factor at fair mid-rate, capped by surplus.
  - Uses Income_safe LOW, safe FOIR, excludes stopped co-earner.
- Recommend = min(lender, safe). If wanted (M2) > 1.5x safe -> Borrow Less to safe. [LOCKED 1.5x]
- Why line: "Bank sees 35k ITR so 6L, you can safely carry 9L on 60k actual — use 6L".

## 3. O3 — Fair rate band + APR

- Start = Base(product, M1b) from table above.
- Adjust:
  - Score 780+ : -1.0%, 700-750: -0.5%, <650: +1.5-2%, Don't Know / No history: widen +2-3% + low confidence (never 300)
  - Job 5yr+ MNC/Govt (A-S1): -0.5%, Business 10yr+ (A-B1): -0.5%
  - Bounce (M5b Yes): +1-2%, Card >70% (A-S3): +1%
  - Collateral LAP route (A-B3): -3 to -4% vs personal (e.g. 16% -> 10-11.5%)
  - (Removed: NBFC-only +2% was never applied in code; thin-file cost already carried by unknown-widen + low confidence.)
- Always band 1.5-2% wide, never point. Unknowns widen, never narrow.
- APR (RBI-style all-in) [LOCKED method]: EMI computed on full P at nominal rate. Borrower receives P minus fee. APR = rate that gives same EMI on (P minus fee), found by binary search 0-50% in 30 steps. Pure JS, no library. My judgement for transparent all-in compare.
  - Fee refs Sept 2026: home 0.35-0.5%, personal 1-2%, business 0.5-3%, two-wheeler up to 2.5%, LAP ~1%.
  - Examples: 8L personal 11.5% +2% fee 5yr -> APR ~12.3%. Home 8.5% +0.35% 20yr -> APR ~8.55%. 1.5L 2W 18% +2.5% 3yr -> APR ~19.7%.
  - Card: Fair APR band (fair rate + typical fee) vs Offer APR (S1 rate + S1 fee). Offer APR above fair top = Unfair.
- Why line: "11-12.5% because personal base 12-18% -1% for 780 + stable 5yr job".

## 4. O1 — Verdict (decided LAST, first match wins) [LOCKED thresholds from Sec 1]

1. Surplus <0 after new EMI -> Don't Borrow. Surplus = Income_safe - Old_EMI - Expenses (M6) - New_EMI.
2. FOIR breach on safe cap + 0 buffer (M9) + bounce (M5b) + 30%+ active loans (A-C3) -> Don't / Borrow Less + consolidate costly first.
3. Wanted >1.5x safe -> Borrow Less to safe number.
4. Stress fails + non-productive (M1a provisional + A-B5/A-C4 final) -> Borrow Less + longer tenure warning.
5. Productive + passes stress even with wide band (Ravi LAP, Anita scooter if extra income covers EMI) -> Conditional Borrow + conditions list.
6. Else Borrow.
- Every verdict + 1 reason + what would flip it. Don't is legitimate and must be reachable (Anita).

## 5. Confidence + Card

- High = 0 unknowns; Med = 1-2; Low = 3+. Widening happens at source (wide bands for unknown); the badge only labels it.
- (Removed: Low O2 +/-20% / O3 +2% post-widening was computed but never applied.)
- Card = one screen: Fair band vs lender quote (S1 or typed: Bank/NBFC/App + rate + fee), 3 bullets why, EMI ceiling, 1 warning. Copy from M3a + whys.

## 6. Worked direction (Sept 2026 rates)

- Priya (29, 110k, 14k EMI, 780): Wants 8L personal wedding. Fair 10.5-12%. Ceiling 110k*55%-14k=46.5k. 8L/5yr@11.5%=~17.4k EMI -> passes math, wedding non-productive -> Borrow Less / Conditional Borrow.
- Ravi (42, ITR 35k vs actual 60k+18k wife, shop 45L, no score): Lender on 35k*45%=15.7k EMI -> ~9-10L personal @16-18% OR LAP @10-11% on 45L (50%=22.5L cap, income caps to ~12L). Route LAP 10-11.5% Borrow Less 9-12L Conditional.
- Anita (35, 26-30k, 4k old, 22k exp, bounce, 0 buffer, 35k@30%+): Safe ceiling 28k*30%-4k=4.4k. 1.5L/3yr@18-22%=5.4-5.7k EMI -> fails + danger combo -> Don't / Borrow Less only if income proof + consolidation. Scooter productive only if +8-10k extra covers EMI + stress.

## 7. What we do NOT know (honesty)

- Exact bank FOIR internal cutoffs (vary by bank, we use practice bands, judgement).
- Future repo moves (assume stable Sept 2026, note assumption).
- Informal moneylender rates (out of scope, formal lender only).
- Bureau score mapping exact (we use slab +/- not scorecard).
