"""Adaptive flow tests: injections, offer-APR card, zero-EMI bounce skip.
No hardcoded outputs — behavior must be earned."""

from app import (
    _branch_steps,
    STEP_PROPERTY_COLLATERAL,
    STEP_APP_LOANS_DETAIL,
)
from rules.engine import compute


def _base(branch="salaried", **kw):
    a = {"purpose": "personal", "product": "personal", "wanted": 300000,
         "income_type": branch, "income_self": 60000,
         "old_emi": 5000, "bounce": "no", "expenses": 25000, "age": 35,
         "score": "700-750", "buffer": "1-2", "branch_answers": {}}
    a.update(kw)
    return a


def test_home_lap_injects_collateral_outside_b_branch():
    assert STEP_PROPERTY_COLLATERAL in _branch_steps(_base("salaried", sub_purpose="home_lap"))
    assert STEP_PROPERTY_COLLATERAL in _branch_steps(_base("informal", sub_purpose="home_lap"))
    assert _branch_steps(_base("self_employed")).count(STEP_PROPERTY_COLLATERAL) == 1  # no duplicate


def test_consolidate_injects_app_detail_outside_c_branch():
    assert STEP_APP_LOANS_DETAIL in _branch_steps(_base("salaried", sub_purpose="personal_consolidate"))
    assert STEP_APP_LOANS_DETAIL in _branch_steps(_base("self_employed", sub_purpose="personal_consolidate"))


def test_large_wanted_injects_collateral_small_does_not():
    big = _base("salaried", wanted=2000000, income_self=15000)  # 133x monthly
    small = _base("salaried", wanted=100000, income_self=50000)  # 2x monthly
    assert STEP_PROPERTY_COLLATERAL in _branch_steps(big)
    assert STEP_PROPERTY_COLLATERAL not in _branch_steps(small)


def test_zero_emi_skips_bounce_penalty():
    o = compute(_base("salaried", old_emi=0, bounce="no"))
    assert all("bounce" not in n for n in o["rate"]["notes"])
    o2 = compute(_base("salaried", old_emi=5000, bounce="yes", bounce_count=1))
    assert any("bounce" in n for n in o2["rate"]["notes"])


def test_offer_card_compares_apr_with_tenure():
    a = _base("salaried", offer_rate=14.0, offer_fee=1.0, offer_tenure=60,
              income_self=110000, old_emi=14000, expenses=55000, age=29,
              score="750+", buffer="3+", job_vintage="5yr+",
              employer="mnc", card_util="<30%",
              branch_answers={"job_stability": "5yr+"})
    a.update({"purpose": "personal", "product": "personal", "wanted": 800000})
    o = compute(a)
    line = o["card"]["lines"][3]
    assert "APR" in line and "COSTLY" in line


def test_old_short_codes_still_work():
    """Backward compat: old 'a'/'b'/'c' and 'A-B3' callers keep working."""
    from app import OLD_TO_NEW_STEP
    assert OLD_TO_NEW_STEP["A-B3"] == STEP_PROPERTY_COLLATERAL
    assert OLD_TO_NEW_STEP["A-C3"] == STEP_APP_LOANS_DETAIL
    assert STEP_PROPERTY_COLLATERAL in _branch_steps(_base("a", sub_purpose="home_lap"))
