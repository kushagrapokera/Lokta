"""Monthly income: safe number (what you really get) vs lender number (what bank counts)."""
from rules.questions import branch_for, SELF_EMPLOYED

def _f(x, default=0.0) -> float:
    try:
        v = float(x)
        return v if v >= 0 else default
    except (TypeError, ValueError):
        return default


def normalize_income(answers: dict) -> dict:
    own_low_month = _f(answers.get("income_self", 0))
    co_monthly = _f(answers.get("co_income", 0))
    has_co_earner = bool(answers.get("co_active", co_monthly > 0))
    co_status = str(answers.get("co_changed", "no")).lower()
    co_stopped = co_status in ("stopped", "yes_stopped", "unemployed")
    co_counts_for_safe = has_co_earner and not co_stopped

    income_safe = own_low_month + (co_monthly if co_counts_for_safe else 0.0)

    is_self_employed = branch_for(answers) == SELF_EMPLOYED
    itr_annual = _f(answers.get("itr_annual", 0))
    if is_self_employed and itr_annual > 0:
        lender_base = itr_annual / 12.0
    else:
        lender_base = own_low_month
    co_lender_share = 0.5 * co_monthly if has_co_earner else 0.0
    income_lender = lender_base + co_lender_share

    return {
        "income_safe": round(income_safe, 2),
        "income_lender": round(income_lender, 2),
        "co_counts_safe": co_counts_for_safe,
    }
