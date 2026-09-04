"""Normalize M4a/M4b + A-B2 into Income_safe vs Income_lender."""


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
    # Stopped earner excluded entirely from safe (M4b lock).
    co_counts_safe = co_active and str(answers.get("co_changed", "no")).lower() not in (
        "stopped", "yes_stopped", "unemployed")

    income_safe = self_low + (co if co_counts_safe else 0.0)

    branch = str(answers.get("income_type", "a")).lower()
    if branch.startswith("b"):
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
