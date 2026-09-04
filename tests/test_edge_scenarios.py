"""Edge scenarios: easy/medium/hard with blanks. Asserts honest handling.
No hardcoded outputs — formulas must earn them."""

from rules.engine import compute


def _easy():
    # Rohan, 32, Pune, salaried. All must answered + offer given.
    return {"purpose": "personal", "product": "personal", "wanted": 500000,
            "income_type": "a", "income_self": 80000, "co_income": 0,
            "co_active": False, "old_emi": 0, "bounce": "no",
            "expenses": 35000, "age": 32, "score": "750+",
            "buffer": "3+", "job_vintage": "5yr+", "employer": "mnc",
            "card_util": "<30%", "offer_rate": 12.0, "offer_fee": 1.5,
            "branch_answers": {"A-S1": "5yr+"}}


def _medium():
    # Meena, 38, Jaipur boutique, self-employed. Blanks: score unknown,
    # co-earner skipped, offer skipped, collateral skipped.
    return {"purpose": "business", "product": "business", "wanted": 1000000,
            "income_type": "b", "income_self": 55000,
            "old_emi": 12000, "bounce": "no", "expenses": 28000, "age": 38,
            "score": "unknown", "buffer": "family", "itr_annual": 480000,
            "biz_vintage": "2-10yr", "biz_extra_income": 15000,
            "branch_answers": {"A-B1": "2-10yr"}}


def _hard():
    # Salim, 45, auto driver, informal. Blanks: expenses, co-earner,
    # old EMI, bounce unknown, extra income unproven.
    return {"purpose": "vehicle", "product": "two_wheeler", "wanted": 120000,
            "income_type": "c", "income_self": 22000,
            "bounce": "unknown", "age": 45, "score": "no_history",
            "buffer": "none", "branch_answers": {}}


def test_easy_full_answers_narrow_high():
    o = compute(_easy())
    assert o["confidence"]["level"] == "High"
    assert o["rate"]["high"] - o["rate"]["low"] <= 3.5
    assert o["verdict"]["verdict"] == "Borrow"
    assert "FAIR" in o["card"]["lines"][3]
    assert o["estimated_exp"] is False


def test_medium_blanks_wide_never_zero():
    o = compute(_medium())
    assert o["confidence"]["level"] in ("Medium", "Low")
    assert o["rate"]["high"] - o["rate"]["low"] >= 3.0  # wide, silence acknowledged
    assert o["rate"]["high"] < 40  # unknown never treated as 300
    assert o["verdict"]["verdict"] in ("Don't borrow", "Borrow less", "Borrow with conditions")
    assert o["estimated_exp"] is False


def test_hard_many_blanks_estimated_never_borrow():
    o = compute(_hard())
    assert o["estimated_exp"] is True  # missing spend assumed 40%, never zero
    assert o["confidence"]["level"] == "Low"
    assert o["verdict"]["verdict"] in ("Don't borrow", "Borrow less", "Borrow with conditions")
    assert o["verdict"]["verdict"] != "Borrow"
    assert "40%" in o["why"]["o4"]
    assert len(o["card"]["lines"]) == 5
