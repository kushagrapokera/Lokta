# Scenario results — batch review (engine-generated, no hand edits)

Engine: rules/engine.py. Tests: `python -m pytest tests/ -q`.

## Summary

| ID | Verdict | Ceiling | Wanted EMI | Fair band | Conf | Handling note |
|----|---------|---------|------------|-----------|------|---------------|
| S1-kunal-fresher | Borrow | 24,750 | 7,137 | 13.5-16.5 | High | as answered |
| S2-lakshmi-near-retire | Don't borrow | 39,500 | 62,494 | 8.4-9.9 | High | as answered |
| S3-arjun-clinic-lap | Borrow with conditions | 39,000 | 24,541 | 9.5-11.0 | High | as answered |
| S4-divya-freelancer | Borrow with conditions | 26,500 | 12,561 | 14.5-20.5 | Medium | as answered |
| S5-chotu-rider-productive | Borrow with conditions | 7,000 | 3,498 | 14.25-20.25 | Medium | as answered |
| S6-farah-homemaker-gold | Don't borrow | 7,500 | 6,548 | 9.0-13.0 | Low | as answered, wide band |
| S7-vikram-forgetful | Borrow | 44,250 | 17,494 | 9.5-13.0 | Medium | as answered |
| S8-joseph-age-cap | Borrow with conditions | 31,000 | 19,668 | 15.5-17.5 | Medium | as answered |

## S1-kunal-fresher — Kunal, 24, Bengaluru, salaried fresher (<1yr startup), high card use.

Blanks: S1 skipped.

### Answers (questions filled on their behalf)

```json
{
 "purpose": "personal",
 "product": "personal",
 "wanted": 300000,
 "income_type": "salaried",
 "income_self": 45000,
 "co_income": 0,
 "co_active": false,
 "old_emi": 0,
 "bounce": "no",
 "expenses": 22000,
 "age": 24,
 "score": "700-750",
 "buffer": "1-2",
 "job_vintage": "<1yr",
 "employer": "startup",
 "card_util": ">70%",
 "branch_answers": {
  "job_stability": "<1yr",
  "card_usage": ">70%"
 }
}
```

### Outputs

- O1: Borrow — Surplus positive, within FOIR cap, passes stress.
  Flip: Stay under EMI ceiling.
- O2: lender 1,165,000 / safe 1,040,000 / use 1,040,000 (wanted 300,000)
- O3: 13.5–16.5% (base [10.0, 18.0], adj 1.0; score 700-750 -0.5%; new job +0.5%; card >70% +1%)
- O4: ceiling 24,750 (FOIR cap 55%), EMI 7,137/60mo, surplus 15,863, stress passes
- Confidence: High (0 unknowns)
- Card:
  - Fair for your profile: 13.5% - 16.5%
  - EMI ceiling: Rs.24,750/month. Do not cross it.
  - Why: score 700-750 -0.5%; new job +0.5%; card >70% +1%.
  - No offer entered: show this card before accepting any quote.
  - Warning: Surplus positive, within FOIR cap, passes stress. [Borrow]

## S2-lakshmi-near-retire — Lakshmi, 55, Chennai, salaried teacher, wants home loan near retirement.

Blanks: S1 skipped.

### Answers (questions filled on their behalf)

```json
{
 "purpose": "home",
 "product": "home",
 "wanted": 3000000,
 "income_type": "salaried",
 "income_self": 90000,
 "co_income": 0,
 "co_active": false,
 "old_emi": 10000,
 "bounce": "no",
 "expenses": 40000,
 "age": 55,
 "score": "750+",
 "buffer": "3+",
 "job_vintage": "5yr+",
 "employer": "govt",
 "card_util": "<30%",
 "branch_answers": {
  "job_stability": "5yr+"
 }
}
```

### Outputs

- O1: Don't borrow — Surplus Rs.-22,494 below zero after new EMI.
  Flip: Lower amount or longer tenure until surplus stays above zero.
- O2: lender 1,930,000 / safe 1,896,000 / use 1,896,000 (wanted 3,000,000)
- O3: 8.4–9.9% (base [8.4, 9.8], adj -1.5; score 750+ -1%; stable job -0.5%)
- O4: ceiling 39,500 (FOIR cap 55%), EMI 62,494/60mo, surplus -22,494, stress fails
- Confidence: High (0 unknowns)
- Card:
  - Fair for your profile: 8.4% - 9.9%
  - EMI ceiling: Rs.39,500/month. Do not cross it.
  - Why: score 750+ -1%; stable job -0.5%.
  - No offer entered: show this card before accepting any quote.
  - Warning: Surplus Rs.-22,494 below zero after new EMI. [Don't borrow]

## S3-arjun-clinic-lap — Arjun, 40, Pune, private clinic 12yr, residential flat 80L loan-free, ITR 12L/yr.

Blanks: Offer skipped.

### Answers (questions filled on their behalf)

```json
{
 "purpose": "business",
 "product": "lap",
 "wanted": 2500000,
 "income_type": "self_employed",
 "income_self": 120000,
 "co_income": 0,
 "co_active": false,
 "itr_annual": 1200000,
 "old_emi": 15000,
 "bounce": "no",
 "expenses": 55000,
 "age": 40,
 "score": "700-750",
 "buffer": "3+",
 "biz_vintage": "10yr+",
 "collateral_value": 8000000,
 "collateral_free": true,
 "collateral_type": "residential",
 "biz_extra_income": 40000,
 "branch_answers": {
  "business_age": "10yr+",
  "yearly_itr": "12L",
  "property_collateral": "80L"
 }
}
```

### Outputs

- O1: Borrow with conditions — Loan adds Rs.40,000/month which covers EMI Rs.24,541.
  Flip: Borrow only the productive part, keep EMI under ceiling.
- O2: lender 3,218,000 / safe 3,973,000 / use 3,218,000 (wanted 2,500,000)
- O3: 9.5–11.0% (base [9.5, 11.5], adj -5.0; score 700-750 -0.5%; business 10yr+ -0.5%; residential collateral -4%)
- O4: ceiling 39,000 (FOIR cap 45%), EMI 24,541/240mo, surplus 25,459, stress passes
- Confidence: High (0 unknowns)
- Card:
  - Fair for your profile: 9.5% - 11.0%
  - EMI ceiling: Rs.39,000/month. Do not cross it.
  - Why: score 700-750 -0.5%; business 10yr+ -0.5%; residential collateral -4%.
  - No offer entered: show this card before accepting any quote.
  - Warning: Loan adds Rs.40,000/month which covers EMI Rs.24,541. [Borrow with conditions]

## S4-divya-freelancer — Divya, 30, Mumbai freelancer, no collateral, unsecured business loan.

Blanks: Score unknown, offer skipped, no collateral details.

### Answers (questions filled on their behalf)

```json
{
 "purpose": "business",
 "product": "business",
 "wanted": 500000,
 "income_type": "self_employed",
 "income_self": 70000,
 "old_emi": 5000,
 "bounce": "no",
 "expenses": 35000,
 "age": 30,
 "score": "unknown",
 "buffer": "1-2",
 "itr_annual": 600000,
 "biz_vintage": "2-10yr",
 "biz_extra_income": 10000,
 "branch_answers": {
  "business_age": "2-10yr"
 }
}
```

### Outputs

- O1: Borrow with conditions — Loan is productive but extra income unproven or thin.
  Flip: Confirm extra income covers 80%+ of EMI, else borrow less.
- O2: lender 805,000 / safe 1,055,000 / use 805,000 (wanted 500,000)
- O3: 14.5–20.5% (base [11.0, 24.0], adj 0.0; unknown score: widen +2%, low confidence)
- O4: ceiling 26,500 (FOIR cap 45%), EMI 12,561/60mo, surplus 17,439, stress passes
- Confidence: Medium (2 unknowns)
- Card:
  - Fair for your profile: 14.5% - 20.5%
  - EMI ceiling: Rs.26,500/month. Do not cross it.
  - Why: unknown score: widen +2%, low confidence.
  - No offer entered: show this card before accepting any quote.
  - Warning: Loan is productive but extra income unproven or thin. [Borrow with conditions]

## S5-chotu-rider-productive — Chotu, 28, Lucknow delivery rider, scooter loan with proven extra + brother backup.

Blanks: Score no_history, offer skipped.

### Answers (questions filled on their behalf)

```json
{
 "purpose": "vehicle",
 "product": "two_wheeler",
 "wanted": 140000,
 "income_type": "informal",
 "income_self": 30000,
 "co_income": 0,
 "co_active": false,
 "old_emi": 2000,
 "bounce": "no",
 "expenses": 18000,
 "age": 28,
 "score": "no_history",
 "buffer": "family",
 "scooter_extra_income": 12000,
 "branch_answers": {
  "family_dependents": "none",
  "vehicle_extra_income": "+12k"
 }
}
```

### Outputs

- O1: Borrow with conditions — Loan adds Rs.12,000/month which covers EMI Rs.3,498.
  Flip: Borrow only the productive part, keep EMI under ceiling.
- O2: lender 415,000 / safe 340,000 / use 340,000 (wanted 140,000)
- O3: 14.25–20.25% (base [10.5, 24.0], adj 0.0; unknown score: widen +2%, low confidence)
- O4: ceiling 7,000 (FOIR cap 30%), EMI 3,498/60mo, surplus 6,502, stress passes
- Confidence: Medium (1 unknowns)
- Card:
  - Fair for your profile: 14.25% - 20.25%
  - EMI ceiling: Rs.7,000/month. Do not cross it.
  - Why: unknown score: widen +2%, low confidence.
  - No offer entered: show this card before accepting any quote.
  - Warning: Loan adds Rs.12,000/month which covers EMI Rs.3,498. [Borrow with conditions]

## S6-farah-homemaker-gold — Farah, 50, Hyderabad homemaker, no self income, husband 25k active, gold ornaments, wants 2L gold loan.

Blanks: Score unknown, offer skipped.

### Answers (questions filled on their behalf)

```json
{
 "purpose": "other",
 "product": "gold",
 "wanted": 200000,
 "income_type": "informal",
 "income_self": 0,
 "co_income": 25000,
 "co_active": true,
 "co_changed": "no",
 "old_emi": 0,
 "bounce": "no",
 "expenses": 20000,
 "age": 50,
 "score": "unknown",
 "buffer": "1-2",
 "branch_answers": {}
}
```

### Outputs

- O1: Don't borrow — Surplus Rs.-1,548 below zero after new EMI.
  Flip: Lower amount or longer tenure until surplus stays above zero.
- O2: lender 118,000 / safe 229,000 / use 118,000 (wanted 200,000)
- O3: 9.0–13.0% (base [9.0, 12.0], adj 0.0; unknown score: widen +2%, low confidence)
- O4: ceiling 7,500 (FOIR cap 30%), EMI 6,548/36mo, surplus -1,548, stress fails
- Confidence: Low (3 unknowns)
- Card:
  - Fair for your profile: 9.0% - 13.0%
  - EMI ceiling: Rs.7,500/month. Do not cross it.
  - Why: unknown score: widen +2%, low confidence.
  - No offer entered: show this card before accepting any quote.
  - Warning: Surplus Rs.-1,548 below zero after new EMI. [Don't borrow]

## S7-vikram-forgetful — Vikram, 36, Delhi salaried, does not remember bounce, score unknown, wants car 8L.

Blanks: Bounce unknown, score unknown, offer skipped.

### Answers (questions filled on their behalf)

```json
{
 "purpose": "vehicle",
 "product": "car",
 "wanted": 800000,
 "income_type": "salaried",
 "income_self": 95000,
 "co_income": 0,
 "co_active": false,
 "old_emi": 8000,
 "bounce": "unknown",
 "expenses": 45000,
 "age": 36,
 "score": "unknown",
 "buffer": "1-2",
 "job_vintage": "1-3yr",
 "employer": "large",
 "card_util": "30-70%",
 "branch_answers": {
  "job_stability": "1-3yr"
 }
}
```

### Outputs

- O1: Borrow — Surplus positive, within FOIR cap, passes stress.
  Flip: Stay under EMI ceiling.
- O2: lender 2,083,000 / safe 2,024,000 / use 2,024,000 (wanted 800,000)
- O3: 9.5–13.0% (base [9.5, 11.5], adj 0.5; stable job -0.5%; bounce history unclear: assumed 1, confirm; 1 bounce +1%; unknown score: widen +2%, low confidence)
- O4: ceiling 44,250 (FOIR cap 55%), EMI 17,494/60mo, surplus 24,506, stress passes
- Confidence: Medium (2 unknowns)
- Card:
  - Fair for your profile: 9.5% - 13.0%
  - EMI ceiling: Rs.44,250/month. Do not cross it.
  - Why: stable job -0.5%; bounce history unclear: assumed 1, confirm; 1 bounce +1%.
  - No offer entered: show this card before accepting any quote.
  - Warning: Surplus positive, within FOIR cap, passes stress. [Borrow]

## S8-joseph-age-cap — Joseph, 60, Kochi self-employed trader, age-cap tenure test, wants business 8L.

Blanks: Offer skipped.

### Answers (questions filled on their behalf)

```json
{
 "purpose": "business",
 "product": "business",
 "wanted": 800000,
 "income_type": "self_employed",
 "income_self": 80000,
 "old_emi": 5000,
 "bounce": "no",
 "expenses": 35000,
 "age": 60,
 "score": "700-750",
 "buffer": "1-2",
 "itr_annual": 720000,
 "biz_vintage": "10yr+",
 "biz_extra_income": 12000,
 "branch_answers": {
  "business_age": "10yr+"
 }
}
```

### Outputs

- O1: Borrow with conditions — Loan is productive but extra income unproven or thin.
  Flip: Confirm extra income covers 80%+ of EMI, else borrow less.
- O2: lender 1,012,000 / safe 1,261,000 / use 1,012,000 (wanted 800,000)
- O3: 15.5–17.5% (base [11.0, 24.0], adj -1.0; score 700-750 -0.5%; business 10yr+ -0.5%)
- O4: ceiling 31,000 (FOIR cap 45%), EMI 19,668/60mo, surplus 20,332, stress passes
- Confidence: Medium (1 unknowns)
- Card:
  - Fair for your profile: 15.5% - 17.5%
  - EMI ceiling: Rs.31,000/month. Do not cross it.
  - Why: score 700-750 -0.5%; business 10yr+ -0.5%.
  - No offer entered: show this card before accepting any quote.
  - Warning: Loan is productive but extra income unproven or thin. [Borrow with conditions]
