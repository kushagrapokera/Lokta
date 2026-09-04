"""O1 verdict hierarchy. Decided LAST, first match wins."""

from rules import config
from rules.questions import is_productive


def _f(x, default=0.0) -> float:
    try:
        v = float(x)
        return v if v >= 0 else default
    except (TypeError, ValueError):
        return default


def verdict(answers: dict, c: dict) -> dict:
    surplus = c.get("surplus", 0)
    foir_breach = c.get("foir_breach", False)
    stress_pass = c.get("stress_pass", True)
    productive = is_productive(answers)
    bounce = str(answers.get("bounce", "no")).lower() == "yes"
    buf = str(answers.get("buffer", "unknown")).lower()
    high_cost = _f(answers.get("app_rate", 0)) > config.HIGH_COST_RATE
    borrow_less_amt = bool(c.get("borrow_less_amt", False))

    if surplus < 0:
        return {"verdict": "Don't borrow",
                "reason": f"Surplus Rs.{surplus:,.0f} below zero after new EMI.",
                "flip": "Lower amount or longer tenure until surplus stays above zero."}
    if foir_breach and buf == "none" and (bounce or high_cost):
        return {"verdict": "Don't borrow",
                "reason": "EMI share over safe cap with no backup plus bounce or 30%+ loans.",
                "flip": "Close high-cost loans first and build 1-2 months backup."}
    if borrow_less_amt:
        return {"verdict": "Borrow less",
                "reason": f"Wanted Rs.{_f(answers.get('wanted',0)):,.0f} over 1.5x safe Rs.{_f(c.get('safe_amt',0)):,.0f}.",
                "flip": f"Borrow up to safe Rs.{_f(c.get('safe_amt',0)):,.0f}."}
    if c.get("estimated_exp") and str(answers.get("buffer", "unknown")).lower() == "none":
        return {"verdict": "Borrow with conditions",
                "reason": "Key spending details missing plus no backup, so limit is estimated.",
                "flip": "Fill actual household expenses and keep 1-2 EMIs backup, then recheck."}
    if not stress_pass and productive is False:
        return {"verdict": "Borrow less",
                "reason": "Fails income -20% / rate +2% stress and loan does not earn income.",
                "flip": "Take smaller amount or longer tenure that passes stress."}
    if productive is True:
        extra = _f(answers.get("biz_extra_income", answers.get("scooter_extra_income", 0)))
        new_emi = _f(c.get("new_emi", 0))
        if extra > 0 and extra >= 0.8 * new_emi:
            return {"verdict": "Borrow with conditions",
                    "reason": f"Loan adds Rs.{extra:,.0f}/month which covers EMI Rs.{new_emi:,.0f}.",
                    "flip": "Borrow only the productive part, keep EMI under ceiling."}
        return {"verdict": "Borrow with conditions",
                "reason": "Loan is productive but extra income unproven or thin.",
                "flip": "Confirm extra income covers 80%+ of EMI, else borrow less."}
    if not stress_pass:
        return {"verdict": "Borrow with conditions",
                "reason": "Passes today but fails stress test.",
                "flip": "Keep 1-2 EMIs backup before borrowing."}
    return {"verdict": "Borrow",
            "reason": "Surplus positive, within FOIR cap, passes stress.",
            "flip": "Stay under EMI ceiling."}
