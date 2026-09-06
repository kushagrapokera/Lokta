"""EMI math, max loan years, and monthly EMI ceiling you should not cross."""

from rules import config
from rules.questions import branch_for, SALARIED, SELF_EMPLOYED

#  converts a loan amount into its monthly payment
def emi(principal: float, annual_rate_pct: float, months: int) -> float:
    if principal <= 0 or months <= 0:
        return 0.0
    r = annual_rate_pct / 12.0 / 100.0
    if r <= 0:
        return principal / months
    f = (1 + r) ** months
    return principal * r * f / (f - 1)

# converts a monthly payment back into the loan amount it supports.
def principal_for_emi(emi_amt: float, annual_rate_pct: float, months: int) -> float:
    if emi_amt <= 0 or months <= 0:
        return 0.0
    r = annual_rate_pct / 12.0 / 100.0
    if r <= 0:
        return emi_amt * months
    f = (1 + r) ** months
    return emi_amt * (f - 1) / (r * f)

# sets the longest loan period from age and product.
def max_tenure_months(age: int, salaried: bool, product: str) -> int:
    try:
        age = int(age)
    except (TypeError, ValueError):
        age = 35
    retire = config.RETIRE_AGE_SALARIED if salaried else config.RETIRE_AGE
    age_cap = max(0, (retire - age)) * 12
    prod = config.PRODUCT_MAX_TENURE_YRS.get(product, 5) * 12
    return int(min(age_cap, prod))


# sets the allowed share of income for all EMIs.
def max_emi_share(answers: dict) -> float:
    """Max share of income allowed for all EMIs."""
    work_type = branch_for(answers)
    if work_type == SALARIED:
        base = config.MAX_EMI_SHARE_SALARIED
    elif work_type == SELF_EMPLOYED:
        base = config.MAX_EMI_SHARE_SELF_EMPLOYED
    else:
        base = config.MAX_EMI_SHARE_INFORMAL

    # EMI bounced??
    bounce = str(answers.get("bounce", "no")).lower() == "yes"

    # from if income stopped after x months
    buf = str(answers.get("buffer", "unknown")).lower()

    if bounce:
        if base >= config.MAX_EMI_SHARE_SALARIED:
            base = config.MAX_EMI_SHARE_SELF_EMPLOYED
        elif base >= config.MAX_EMI_SHARE_SELF_EMPLOYED:
            base = config.MAX_EMI_SHARE_INFORMAL
    if buf == "none" and base > config.MAX_EMI_SHARE_INFORMAL_WITH_BUFFER:
        base = config.MAX_EMI_SHARE_INFORMAL_WITH_BUFFER
    if buf == "none" and work_type == SALARIED:
        base = min(base, config.MAX_EMI_SHARE_INFORMAL_WITH_BUFFER)
    return base

# affordable new emi per month
def emi_ceiling(income_safe: float, max_share: float, old_emi: float) -> float:
    return max(0.0, income_safe * max_share - max(0.0, old_emi))
