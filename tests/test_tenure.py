"""Tenure-choice tests: default preserves old behavior; shorter pace tightens scoring."""

from rules.engine import compute


def _priya(**kw):
    a = {"purpose": "personal", "product": "personal", "wanted": 800000,
         "income_type": "salaried", "income_self": 110000, "co_income": 0,
         "co_active": False, "old_emi": 14000, "bounce": "no",
         "expenses": 55000, "age": 29, "score": "750+",
         "buffer": "3+", "job_vintage": "5yr+", "employer": "mnc",
         "card_util": "<30%", "branch_answers": {"job_stability": "5yr+"}}
    a.update(kw)
    return a


def test_missing_choice_means_max_tenure():
    o = compute(_priya())
    assert o["desired_months"] == o["max_months"] == 60
    assert o["std_months"] == 60


def test_shorter_choice_raises_emi_and_lowers_amounts():
    full = compute(_priya())
    short = compute(_priya(desired_years=2))
    assert short["desired_months"] == 24
    assert short["new_emi"] > full["new_emi"]
    assert short["amount"]["safe"] < full["amount"]["safe"]
    assert short["total_interest"] < full["total_interest"]
    assert short["alt_emi"] == full["new_emi"]


def test_choice_above_typical_max_is_honored_and_flagged():
    o = compute(_priya(desired_years=15))
    assert o["desired_months"] == 180
    assert o["tenure_capped"] is True
    assert o["std_months"] == 180


def test_choice_within_max_not_capped():
    o = compute(_priya(desired_years=2))
    assert o["tenure_capped"] is False
