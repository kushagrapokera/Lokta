"""Borrower flow: step order + branching. Framework-free, no numbers here.

Both the old Streamlit UI and the Flask UI read step order from here so they
always ask the same questions in the same order. All math lives in rules/.
"""

from rules import config
from rules.income import normalize_income
from rules.questions import SUB_OPTIONS, SALARIED, SELF_EMPLOYED, INFORMAL, branch_for

STEP_LOAN_PURPOSE = "loan_purpose"
STEP_LOAN_AMOUNT = "loan_amount"
STEP_WORK_TYPE = "work_type"
STEP_MONTHLY_INCOME = "monthly_income"
STEP_CURRENT_LOANS = "current_loans"
STEP_MONTHLY_EXPENSES = "monthly_expenses"
STEP_AGE = "age"
STEP_CREDIT_SCORE = "credit_score"
STEP_SAFETY_BACKUP = "safety_backup"
STEP_EXISTING_OFFER = "existing_offer"

STEP_JOB_STABILITY = "job_stability"
STEP_CARD_USAGE = "card_usage"
STEP_YEARLY_ITR = "yearly_itr"
STEP_PROPERTY_COLLATERAL = "property_collateral"
STEP_BUSINESS_AGE = "business_age"
STEP_BUSINESS_EXTRA_INCOME = "business_extra_income"
STEP_VEHICLE_EXTRA_INCOME = "vehicle_extra_income"
STEP_APP_LOANS_DETAIL = "app_loans_detail"
STEP_RESULTS = "results"

MUST_STEPS = [
    STEP_LOAN_PURPOSE,
    STEP_LOAN_AMOUNT,
    STEP_WORK_TYPE,
    STEP_MONTHLY_INCOME,
    STEP_CURRENT_LOANS,
    STEP_MONTHLY_EXPENSES,
    STEP_AGE,
    STEP_CREDIT_SCORE,
    STEP_SAFETY_BACKUP,
    STEP_EXISTING_OFFER,
]
PURPOSES = list(SUB_OPTIONS.keys()) + ["Other"]

OLD_TO_NEW_STEP = {
    "M1": STEP_LOAN_PURPOSE, "M2": STEP_LOAN_AMOUNT, "M3": STEP_WORK_TYPE,
    "M4": STEP_MONTHLY_INCOME, "M5": STEP_CURRENT_LOANS, "M6": STEP_MONTHLY_EXPENSES,
    "M7": STEP_AGE, "M8": STEP_CREDIT_SCORE, "M9": STEP_SAFETY_BACKUP,
    "S1": STEP_EXISTING_OFFER, "A-S1": STEP_JOB_STABILITY, "A-S3": STEP_CARD_USAGE,
    "A-B2": STEP_YEARLY_ITR, "A-B3": STEP_PROPERTY_COLLATERAL, "A-B1": STEP_BUSINESS_AGE,
    "A-B5": STEP_BUSINESS_EXTRA_INCOME, "A-C4": STEP_VEHICLE_EXTRA_INCOME,
    "A-C3": STEP_APP_LOANS_DETAIL, "DONE": STEP_RESULTS,
}


def _branch_steps(ans: dict) -> list:
    """Extra questions based on work type. Accepts old or new step names."""
    work_type = branch_for(ans)
    if work_type == SELF_EMPLOYED:
        steps = [STEP_YEARLY_ITR, STEP_PROPERTY_COLLATERAL, STEP_BUSINESS_AGE,
                 STEP_BUSINESS_EXTRA_INCOME]
    elif work_type == INFORMAL:
        steps = [STEP_VEHICLE_EXTRA_INCOME, STEP_APP_LOANS_DETAIL]
    else:
        steps = [STEP_JOB_STABILITY, STEP_CARD_USAGE]
    if ans.get("sub_purpose") == "home_lap" and STEP_PROPERTY_COLLATERAL not in steps:
        steps = steps + [STEP_PROPERTY_COLLATERAL]
    if ans.get("sub_purpose") == "personal_consolidate" and STEP_APP_LOANS_DETAIL not in steps:
        steps = steps + [STEP_APP_LOANS_DETAIL]
    try:
        inc = normalize_income(ans).get("income_safe", 0) or 0
        if inc > 0 and float(ans.get("wanted", 0) or 0) > config.LAP_SUGGEST_INCOME_MULT * float(inc) \
                and STEP_PROPERTY_COLLATERAL not in steps:
            steps = steps + [STEP_PROPERTY_COLLATERAL]
    except (TypeError, ValueError):
        pass
    return steps


def _normalize_step(sid: str) -> str:
    return OLD_TO_NEW_STEP.get(sid, sid)


def _steps(ans: dict) -> list:
    return MUST_STEPS + _branch_steps(ans) + [STEP_RESULTS]
