"""EMI math, tenure cap, O4 ceiling, stress test."""

from rules import config


def emi(principal: float, annual_rate_pct: float, months: int) -> float:
    if principal <= 0 or months <= 0:
        return 0.0
    r = annual_rate_pct / 12.0 / 100.0
    if r <= 0:
        return principal / months
    f = (1 + r) ** months
    return principal * r * f / (f - 1)


def principal_for_emi(emi_amt: float, annual_rate_pct: float, months: int) -> float:
    if emi_amt <= 0 or months <= 0:
        return 0.0
    r = annual_rate_pct / 12.0 / 100.0
    if r <= 0:
        return emi_amt * months
    f = (1 + r) ** months
    return emi_amt * (f - 1) / (r * f)


def max_tenure_months(age: int, salaried: bool, product: str) -> int:
    try:
        age = int(age)
    except (TypeError, ValueError):
        age = 35
    retire = config.RETIRE_AGE_SALARIED if salaried else config.RETIRE_AGE
    age_cap = max(0, (retire - age)) * 12
    prod = config.PRODUCT_MAX_TENURE_YRS.get(product, 5) * 12
    return int(min(age_cap, prod))


def foir_cap(answers: dict) -> float:
    t = str(answers.get("income_type", "a")).lower()
    base = config.FOIR_SALARIED if t.startswith("a") else (
        config.FOIR_SELF_EMPLOYED if t.startswith("b") else config.FOIR_INFORMAL)
    bounce = str(answers.get("bounce", "no")).lower() == "yes"
    buf = str(answers.get("buffer", "unknown")).lower()
    if bounce:
        if base >= config.FOIR_SALARIED:
            base = config.FOIR_SELF_EMPLOYED
        elif base >= config.FOIR_SELF_EMPLOYED:
            base = config.FOIR_INFORMAL
    if buf == "none" and base > config.FOIR_INFORMAL_WITH_BUFFER:
        base = config.FOIR_INFORMAL_WITH_BUFFER
    if buf == "none" and str(answers.get("income_type", "a")).lower().startswith("a"):
        base = min(base, config.FOIR_INFORMAL_WITH_BUFFER)
    return base


def emi_ceiling(income_safe: float, foir_cap_value: float, old_emi: float) -> float:
    return max(0.0, income_safe * foir_cap_value - max(0.0, old_emi))
