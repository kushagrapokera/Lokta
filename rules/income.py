"""Monthly income: safe number (what you really get) vs lender number (what bank counts)."""


def _f(x, default=0.0) -> float:
    try:
        v = float(x)
        return v if v >= 0 else default
    except (TypeError, ValueError):
        return default


def normalize_income(answers: dict) -> dict:
    self_low = _f(answers.get("income_self", 0))
    co = _f(answers.get("co_income", 0))
    co_active = bool(answers.get("co_active", co > 0))
    # A co-earner who stopped earning adds nothing to the safe number.
    co_counts_safe = co_active and str(answers.get("co_changed", "no")).lower() not in (
        "stopped", "yes_stopped", "unemployed")

    income_safe = self_low + (co if co_counts_safe else 0.0)

    from rules.questions import branch_for, SELF_EMPLOYED
    if branch_for(answers) == SELF_EMPLOYED:
        itr_annual = _f(answers.get("itr_annual", 0))
        base_lender = itr_annual / 12.0 if itr_annual > 0 else self_low
    else:
        base_lender = self_low
    income_lender = base_lender + (0.5 * co if co_active else 0.0)

    return {
        "income_safe": round(income_safe, 2),
        "income_lender": round(income_lender, 2),
        "co_counts_safe": co_counts_safe,
    }
