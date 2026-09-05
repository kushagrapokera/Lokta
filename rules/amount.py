"""Max loan amount: what bank may give (lender) vs what you can safely carry (safe)."""

from rules import config
from rules.emi import principal_for_emi
from rules.income import normalize_income
from rules.emi import max_emi_share


def _f(x, default=0.0) -> float:
    try:
        v = float(x)
        return v if v >= 0 else default
    except (TypeError, ValueError):
        return default


def max_amount(answers: dict, fair_mid: float, months: int) -> dict:
    inc = normalize_income(answers)
    max_share = max_emi_share(answers)
    old = _f(answers.get("old_emi", 0))
    lender_cap = max(0.0, inc["income_lender"] * max_share - old)
    safe_cap = max(0.0, inc["income_safe"] * max_share - old)

    product = str(answers.get("product", "personal")).lower()
    base_key = {"lap": "lap_bank", "home": "home", "two_wheeler": "two_wheeler",
                "business": "business", "gold": "gold"}.get(product, "personal_bank")
    lender_rate = config.BASE_BANDS[base_key][0]
    lender_amt = principal_for_emi(lender_cap, lender_rate, months)
    safe_amt = principal_for_emi(safe_cap, fair_mid, months)

    # LAP LTV cap 60% of collateral.
    if product == "lap" and _f(answers.get("collateral_value", 0)) > 0:
        ltv_cap = _f(answers.get("collateral_value", 0)) * 0.60
        lender_amt = min(lender_amt, ltv_cap)
        safe_amt = min(safe_amt, ltv_cap)

    lender_amt = round(lender_amt, -3)
    safe_amt = round(safe_amt, -3)
    use_amt = min(lender_amt, safe_amt)
    wanted = _f(answers.get("wanted", 0))
    borrow_less = wanted > config.WANT_VS_SAFE_BORROW_LESS * safe_amt and safe_amt > 0
    return {"lender": lender_amt, "safe": safe_amt, "use": use_amt,
            "wanted": wanted, "borrow_less": borrow_less}
