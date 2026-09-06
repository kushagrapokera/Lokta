"""Question defs from QUESTIONS.md v1.1. Branching on a/b/c."""

import re

# (code, label, product). Product keys must match fair_rate bands.
SUB_OPTIONS = {
    "Home": [("home_buy", "Buying a ready house / flat", "home"),
             ("home_build", "Building on my own plot", "home"),
             ("home_renovate", "Renovation / repair", "home"),
             ("home_plot", "Buying a plot", "home"),
             ("home_lap", "Loan against my house / plot", "lap"),
             ("home_unsure", "Not sure yet", "unknown")],
    "Vehicle": [("vehicle_2w_new", "New scooter / bike for myself", "two_wheeler"),
                ("vehicle_2w_used", "Used scooter / bike", "two_wheeler"),
                ("vehicle_car_new", "New car for family", "car"),
                ("vehicle_car_used", "Used car", "car"),
                ("vehicle_earn", "Vehicle for earning (taxi, goods, delivery)", "two_wheeler"),
                ("vehicle_unsure", "Not sure yet", "unknown")],
    "Education": [("edu_india", "Degree in India", "personal"),
                  ("edu_abroad", "Studies abroad", "personal"),
                  ("edu_skill", "Short skill / professional course", "personal"),
                  ("edu_coaching", "Coaching / exam prep", "personal"),
                  ("edu_unsure", "Not sure yet", "unknown")],
    "Personal use": [("personal_wedding", "Wedding / celebration", "personal"),
                     ("personal_medical", "Medical emergency", "personal"),
                     ("personal_travel", "Travel / vacation", "personal"),
                     ("personal_gadget", "Gadgets / home durables", "personal"),
                     ("personal_consolidate", "Repay costly loans together", "personal"),
                     ("personal_unsure", "Not sure yet", "unknown")],
    "Business": [("biz_stock", "Stock / inventory", "business"),
                 ("biz_machine", "Machines / equipment", "business"),
                 ("biz_expand", "New branch / shop expansion", "business"),
                 ("biz_vehicle", "Delivery / commercial vehicle", "business"),
                 ("biz_cash", "Day-to-day working cash", "business"),
                 ("biz_unsure", "Not sure yet", "unknown")],
}



# Sub-purposes that settle productive=True right at M1 (earning assets).
EARN_SUBS = {"vehicle_earn", "biz_stock", "biz_machine", "biz_expand", "biz_vehicle", "biz_cash",
             "home_buy", "home_build"}
# Settled non-productive at M1.
BURN_SUBS = {"personal_wedding", "personal_travel", "personal_gadget", "personal_medical",
             "vehicle_2w_new", "vehicle_2w_used", "vehicle_car_new", "vehicle_car_used"}


def product_for_sub(code: str) -> str:
    for _p, opts in SUB_OPTIONS.items():
        for c, _l, prod in opts:
            if c == code:
                return prod
    return "unknown"


# Readable work-type names used across the app.
# Old short codes "a"/"b"/"c" still work (accepted for backward compatibility).
SALARIED = "salaried"
SELF_EMPLOYED = "self_employed"
INFORMAL = "informal"


def branch_for(answers: dict) -> str:
    """Which borrower path? Returns 'salaried' | 'self_employed' | 'informal'.

    Reads answers["income_type"]. Accepts old codes "a"/"b"/"c" too.
    Defaults to 'salaried' only if missing.
    """
    t = str(answers.get("income_type", answers.get("M3b", "salaried"))).strip().lower()
    if t in ("a", "salaried", "salary"):
        return SALARIED
    if t in ("b", "self", "self-employed", "self_employed", "business"):
        return SELF_EMPLOYED
    if t in ("c", "informal", "gig", "cash"):
        return INFORMAL
    return SALARIED


def parse_score(raw: object) -> tuple[str, str]:
    """Free-text credit score -> (band_key, label).

    band_key in 750+ | 700-750 | 650-700 | below650 | unknown | no_history.
    Unparseable or blank is unknown (never zero, never 300). Pure function.
    """
    s = str(raw or "").strip().lower()
    if not s or s in ("na", "n/a", "?", "-", "nil", "none", "idk"):
        return ("unknown", "Don't know")
    if any(k in s for k in ("no history", "no-history", "first loan", "first time",
                            "never", "no loan", "thin file", "no cibil")):
        return ("no_history", "No history (never taken a loan)")
    if any(k in s for k in ("dont know", "don't know", "unknown", "not sure", "no idea")):
        return ("unknown", "Don't know")
    m = re.search(r"(\d{3,4})", s)
    if m:
        v = int(m.group(1))
        if v >= 750 and v <= 900:
            return ("750+", "750+ band")
        if 700 <= v < 750:
            return ("700-750", "700-750 band")
        if 650 <= v < 700:
            return ("650-700", "650-700 band")
        if 300 <= v < 650:
            return ("below650", "Below 650 band")
        return ("unknown", "Don't know")
    return ("unknown", "Don't know")


def is_productive(answers: dict) -> bool | None:
    """Will this loan earn extra income? Sub-purpose decides first, else extra-income answers."""
    sub = str(answers.get("sub_purpose", "")).lower()
    if sub in EARN_SUBS:
        return True
    if sub in BURN_SUBS:
        return False
    purpose = str(answers.get("purpose", "other")).lower()
    branch = branch_for(answers)
    if branch == SELF_EMPLOYED and "biz_extra_income" in answers:
        try:
            return float(answers.get("biz_extra_income") or 0) > 0
        except (TypeError, ValueError):
            return None
    if branch == INFORMAL and "scooter_extra_income" in answers:
        try:
            return float(answers.get("scooter_extra_income") or 0) > 0
        except (TypeError, ValueError):
            return None
    if purpose == "business":
        return True
    if purpose in ("wedding", "personal", "travel", "gadget", "medical"):
        return False
    if purpose == "vehicle":
        return None  # unknown until extra-income question is answered
    if purpose in ("home", "education"):
        return True
    return None
