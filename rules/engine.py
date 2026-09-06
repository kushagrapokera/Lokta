"""Pipeline: answers -> verdict + amounts + rate + ceiling + card. Pure, deterministic."""

from rules import config
from rules.income import normalize_income
from rules.emi import emi, max_tenure_months, max_emi_share, emi_ceiling
from rules.questions import branch_for, SALARIED
from rules.fair_rate import fair_rate
from rules.amount import max_amount
from rules.apr import apr
from rules.verdict import verdict
from rules.confidence import confidence
from rules.card import build_card
from rules.explain import explain


def _f(x, default=0.0) -> float:
    try:
        v = float(x)
        return v if v >= 0 else default
    except (TypeError, ValueError):
        return default


def compute(answers: dict) -> dict:
    a = dict(answers)
    inc = normalize_income(a)
    salaried = branch_for(a) == SALARIED
    product = str(a.get("product", "personal")).lower()
    age_given = a.get("age", None) not in (None, "")
    months_max = max_tenure_months(a.get("age", 35), salaried, product)
    months_max = months_max or 60
    # Chosen pace ("In how many years do you want to repay?"), clamped to
    # [6 months, max]. Missing means max, so old answers behave as before.
    desired_raw = a.get("desired_years", None)
    try:
        requested_months = int(round(float(desired_raw) * 12)) if desired_raw not in (None, "") else months_max
    except (TypeError, ValueError):
        requested_months = months_max
    # User pace governs: only the 6-month floor applies. Anything above the
    # typical max is honored and flagged, not clamped.
    tenure_capped = requested_months > months_max
    months = max(6, requested_months)
    max_share = max_emi_share(a)
    old_emi_unknown = "old_emi" not in a or a.get("old_emi") in (None, "")
    old = _f(a.get("old_emi", 0))
    # Missing/zero expenses with real income is never treated as zero spend.
    # Honest fallback: assume 40% of safe income, flag estimated + Low confidence.
    exp_raw = a.get("expenses", None)
    estimated_exp = False
    if (exp_raw in (None, "") or _f(exp_raw) <= 0) and inc["income_safe"] > 0:
        exp = round(config.EXPENSE_ESTIMATE_PCT * inc["income_safe"], 2)
        estimated_exp = True
    else:
        exp = _f(exp_raw, 0)
    ceiling = emi_ceiling(inc["income_safe"], max_share, old)

    rate = fair_rate(a)
    amt = max_amount(a, rate["mid"], months)
    # EMI runs at the chosen pace in full; the typical max is only the trade-off.
    std_months = months
    wanted_amt = _f(a.get("wanted", 0))
    new_emi = emi(wanted_amt, rate["mid"], std_months) if wanted_amt > 0 else 0.0
    # Tenure trade-off: same loan at the typical max allowed tenure.
    std_max_months = months_max
    alt_emi = emi(wanted_amt, rate["mid"], std_max_months) if wanted_amt > 0 else 0.0
    total_interest = round(new_emi * std_months - wanted_amt, 2) if wanted_amt > 0 else 0.0
    alt_total_interest = round(alt_emi * std_max_months - wanted_amt, 2) if wanted_amt > 0 else 0.0

    surplus = inc["income_safe"] - old - exp - new_emi
    emi_share_used = (old + new_emi) / inc["income_safe"] if inc["income_safe"] > 0 else 99.0
    over_emi_limit = emi_share_used > max_share + 1e-9

    # Stress: income -20% OR rate +2% (one shock, worse of the two for surplus).
    stress_emi = emi(_f(a.get("wanted", 0)), rate["mid"] + 2.0, std_months)
    surplus_income_shock = inc["income_safe"] * 0.80 - old - exp - new_emi
    surplus_rate_shock = inc["income_safe"] - old - exp - stress_emi
    stress_pass = min(surplus_income_shock, surplus_rate_shock) > 0

    # Productive extra covers EMI? (verdict reads it from answers directly)
    v = verdict(a, {"surplus": round(surplus, 2), "over_emi_limit": over_emi_limit,
                    "stress_pass": stress_pass, "borrow_less_amt": amt["borrow_less"],
                    "safe_amt": amt["safe"], "new_emi": round(new_emi, 2),
                    "estimated_exp": estimated_exp, "old_emi_unknown": old_emi_unknown,
                    "age_given": age_given})
    conf = confidence(a, extra_unknowns=(
        (1 if estimated_exp else 0) + (1 if old_emi_unknown else 0)
        + (0 if age_given else 1)))
    fee = _f(a.get("offer_fee", _f(a.get("fee", 0))))
    fair_apr_lo = apr(rate["low"], fee, std_months)
    fair_apr_hi = apr(rate["high"], fee, std_months)

    out = {"income": inc, "months": months, "max_months": months_max,
           "tenure_capped": tenure_capped,
           "desired_months": months, "std_months": std_months,
           "std_max_months": std_max_months, "max_emi_share": max_share,
           "ceiling": round(ceiling, 2), "rate": rate, "amount": amt,
           "new_emi": round(new_emi, 2), "alt_emi": round(alt_emi, 2),
           "shock_income_surplus": round(surplus_income_shock, 2),
           "shock_rate_emi": round(stress_emi, 2),
           "total_interest": total_interest, "alt_total_interest": alt_total_interest,
           "surplus": round(surplus, 2),
           "expenses_used": round(exp, 2), "estimated_exp": estimated_exp,
           "old_emi_unknown": old_emi_unknown, "age_given": age_given,
           "emi_share_used": round(emi_share_used, 4),
           "stress_pass": stress_pass,
           "verdict": v, "confidence": conf,
           "fair_apr": [fair_apr_lo, fair_apr_hi]}
    out["card"] = build_card(a, out)
    out["why"] = explain(out)
    return out


