"""O3 base band by product (Sept 2026) + adjustments. Band only, never point."""

from rules import config


def _product_key(product: str) -> str:
    p = str(product or "personal").lower()
    if p in ("lap",):
        return "lap_bank"
    if p in ("home",):
        return "home"
    if p in ("two_wheeler", "vehicle_scooter"):
        return "two_wheeler"
    if p in ("business",):
        return "business"
    if p in ("gold",):
        return "gold"
    if p in ("car",):
        return "lap_bank"  # secured auto ~ LAP band; judgement, in RULES.md
    return "personal_bank"


def fair_rate(answers: dict) -> dict:
    product = answers.get("product", "personal")
    key = _product_key(product)
    base_lo, base_hi = config.BASE_BANDS[key]
    mid = (base_lo + base_hi) / 2
    adj = 0.0
    notes: list[str] = []

    score = str(answers.get("score", "unknown")).lower()
    if score in ("750+", "750 plus", "780", "800"):
        adj += config.ADJ_SCORE_750_PLUS
        notes.append("score 750+ -1%")
    elif score in ("700-750", "700_750"):
        adj += config.ADJ_SCORE_700_750
        notes.append("score 700-750 -0.5%")
    elif score in ("650-700",):
        adj += config.ADJ_SCORE_650_700
        notes.append("score 650-700 +0.5%")
    elif score in ("below650", "below 650", "<650"):
        adj += config.ADJ_SCORE_BELOW_650
        notes.append("score <650 +1.5%")

    branch = str(answers.get("income_type", "a")).lower()
    if branch.startswith("a"):
        vint = str(answers.get("job_vintage", "")).lower()
        emp = str(answers.get("employer", "")).lower()
        if vint in ("5yr+", "5+", "5 plus") or emp in ("mnc", "govt", "large"):
            adj += config.ADJ_JOB_STABLE
            notes.append("stable job -0.5%")
        elif vint in ("<1yr", "<1", "new"):
            adj += config.ADJ_JOB_NEW
            notes.append("new job +0.5%")
        card = str(answers.get("card_util", "")).lower()
        if card in (">70%", "high", "70+"):
            adj += config.ADJ_CARD_HIGH
            notes.append("card >70% +1%")
    if branch.startswith("b"):
        vint = str(answers.get("biz_vintage", "")).lower()
        if vint in ("10yr+", "10+", "14yr", "long"):
            adj += -0.5
            notes.append("business 10yr+ -0.5%")

    bounce = str(answers.get("bounce", "no")).lower()
    if bounce == "yes":
        bounces = int(answers.get("bounce_count", 1) or 1)
    elif bounce in ("unknown", "dontremember", "don't remember", ""):
        bounces = 1  # history unclear: assume 1, flagged; never best-case 0 (RULES.md)
        notes.append("bounce history unclear: assumed 1, confirm")
    else:
        bounces = 0
    if bounces >= 2:
        adj += config.ADJ_BOUNCE_MULTI
        notes.append("2+ bounces +2%")
    elif bounces == 1:
        adj += config.ADJ_BOUNCE_ONE
        notes.append("1 bounce +1%")

    if branch.startswith("b") and float(answers.get("collateral_value", 0) or 0) > 0 \
            and bool(answers.get("collateral_free", False)):
        ctype = str(answers.get("collateral_type", "residential")).lower()
        if ctype.startswith("com"):
            adj += config.ADJ_LAP_COMMERCIAL
            notes.append("commercial collateral -3%")
        else:
            adj += config.ADJ_LAP_RESIDENTIAL
            notes.append("residential collateral -4%")

    unknown = score in ("unknown", "dontknow", "don't know", "no_history", "no history", "")
    widen = 0.0
    if unknown:
        widen = config.ADJ_UNKNOWN_WIDEN
        notes.append("unknown score: widen +2%, low confidence")

    base_width = base_hi - base_lo
    mid0 = (base_lo + base_hi) / 2
    mid_adj = mid0 + adj
    # Width by risk: known-clean narrow, known-risky medium, unknown wide.
    if unknown or bounces >= 1:
        width = min(base_width + widen, 6.0)
        if base_width > 8:  # very wide base (2W/business): anchor to risk slice
            width = 4.0 + widen
    elif adj <= -1.0:
        width = 2.0
    else:
        width = 3.0
    width = max(width, config.BAND_MIN_WIDTH)
    lo = mid_adj - width / 2
    hi = mid_adj + width / 2
    # clamp into [base_lo, base_hi + 2]
    lo = max(lo, base_lo)
    hi = min(max(hi, lo + config.BAND_MIN_WIDTH), base_hi + 2.0)
    if hi - lo < config.BAND_MIN_WIDTH:
        hi = lo + config.BAND_MIN_WIDTH
    mid = round((lo + hi) / 2, 2)
    return {"low": round(lo, 2), "high": round(hi, 2), "mid": mid,
            "base": [base_lo, base_hi], "adj": round(adj, 2), "notes": notes,
            "unknown": unknown}
