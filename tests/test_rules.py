"""Phase 0 structural + Phase 1 golden tests. Golden asserts direction, not exact
numbers — formulas must earn them honestly, no hardcoding outputs."""

import importlib


def test_config_has_locked_keys():
    from rules import config
    assert config.REPO_RATE == 5.25
    assert config.FOIR_SALARIED == 0.55
    assert config.FOIR_SELF_EMPLOYED == 0.45
    assert config.FOIR_INFORMAL == 0.30
    assert config.WANT_VS_SAFE_BORROW_LESS == 1.5
    assert config.STRESS_INCOME_DROP == 0.20
    assert config.STRESS_RATE_HIKE == 2.0
    for k in ["home", "personal_bank", "lap_bank", "two_wheeler", "business", "gold"]:
        assert k in config.BASE_BANDS


def test_all_rule_modules_importable():
    for m in ["config", "questions", "income", "emi", "amount", "fair_rate",
              "apr", "verdict", "confidence", "card", "explain"]:
        assert importlib.import_module(f"rules.{m}") is not None


def test_no_numbers_outside_config():
    # Real check: threshold literals and redefinitions live only in rules/config.py.
    # Referencing config.X by name (as app.py does) is the correct pattern.
    import pathlib
    import re
    root = pathlib.Path(".")
    files = [p for p in list(root.glob("*.py")) + list(root.glob("rules/*.py"))
             + list(root.glob("tests/*.py")) + list(root.glob("scripts/*.py"))
             if p.name not in ("config.py", "test_rules.py")]
    bad_lits = [str(p) for p in files
                if any(n in p.read_text() for n in ["0.55", "0.45"])]
    assert bad_lits == [], f"FOIR literals outside config: {bad_lits}"
    redef = [str(p) for p in files
             if re.search(r"^\s*(FOIR_\w+|WANT_VS_SAFE_BORROW_LESS|HIGH_COST_RATE|"
                          r"EXPENSE_ESTIMATE_PCT|LAP_SUGGEST_INCOME_MULT|ADJ_\w+)\s*=",
                          p.read_text(), re.M)]
    assert redef == [], f"threshold redefinitions outside config: {redef}"
    cfg = (root / "rules" / "config.py").read_text()
    assert all(n in cfg for n in ["0.55", "WANT_VS_SAFE_BORROW_LESS", "HIGH_COST_RATE"])


def _priya():
    return {"purpose": "personal", "product": "personal", "wanted": 800000,
            "income_type": "salaried", "income_self": 110000, "co_income": 0,
            "co_active": False, "old_emi": 14000, "bounce": "no",
            "expenses": 55000, "age": 29, "score": "750+",
            "buffer": "3+", "job_vintage": "5yr+", "employer": "mnc",
            "card_util": "<30%", "branch_answers": {"job_stability": "5yr+", "variable_pay": "0%"}}


def _ravi():
    return {"purpose": "business", "product": "lap", "wanted": 1500000,
            "income_type": "self_employed", "income_self": 60000, "co_income": 18000,
            "co_active": True, "co_changed": "no", "itr_annual": 420000,
            "old_emi": 0, "bounce": "no", "expenses": 30000, "age": 42,
            "score": "no_history", "buffer": "1-2",
            "collateral_value": 4500000, "collateral_free": True,
            "collateral_type": "commercial", "biz_vintage": "10yr+",
            "biz_extra_income": 20000,
            "branch_answers": {"business_age": "10yr+", "yearly_itr": "4.2L", "property_collateral": "45L"}}


def _anita():
    return {"purpose": "vehicle", "product": "two_wheeler", "wanted": 150000,
            "income_type": "informal", "income_self": 28000, "co_income": 0,
            "co_active": False, "co_changed": "stopped", "old_emi": 4000,
            "bounce": "yes", "bounce_count": 1, "expenses": 22000, "age": 35,
            "score": "unknown", "buffer": "none",
            "app_outstanding": 35000, "app_rate": 32,
            "scooter_extra_income": 9000,
            "branch_answers": {"family_dependents": "2 kids", "app_loans_detail": "35k@32%"}}


def test_priya_passes_math_but_wedding_guarded():
    from rules.engine import compute
    o = compute(_priya())
    assert 40000 <= o["ceiling"] <= 55000
    assert o["new_emi"] < o["ceiling"]
    assert o["rate"]["low"] <= 11.5 and o["rate"]["high"] <= 16.5
    assert o["rate"]["high"] - o["rate"]["low"] <= 3.5
    assert o["verdict"]["verdict"] in ("Borrow", "Borrow less", "Borrow with conditions")
    assert o["confidence"]["level"] in ("High", "Medium")


def test_ravi_lender_uses_itr_and_lap_routes():
    from rules.engine import compute
    o = compute(_ravi())
    assert o["income"]["income_lender"] < o["income"]["income_safe"]
    assert o["rate"]["high"] <= 14.0
    assert o["amount"]["lender"] > 0 and o["amount"]["safe"] > 0
    assert o["verdict"]["verdict"] in ("Borrow", "Borrow less", "Borrow with conditions")
    assert o["confidence"]["level"] in ("Medium", "Low")


def test_anita_dont_or_borrow_less():
    from rules.engine import compute
    o = compute(_anita())
    assert 3000 <= o["ceiling"] <= 6000
    assert o["new_emi"] > o["ceiling"] or o["verdict"]["verdict"] in (
        "Don't borrow", "Borrow less", "Borrow with conditions")
    assert o["verdict"]["verdict"] in ("Don't borrow", "Borrow less", "Borrow with conditions")


def test_unknown_score_never_zero_and_edges():
    from rules.engine import compute
    from rules.apr import apr
    o = compute({"purpose": "personal", "product": "personal", "wanted": 100000,
                 "income_type": "salaried", "income_self": 50000, "old_emi": 0,
                 "bounce": "unknown", "expenses": 20000, "age": 30,
                 "score": "unknown", "buffer": "unknown", "branch_answers": {}})
    assert o["rate"]["high"] < 40  # finite, never treated as 300-score penalty blowup
    z = compute({"purpose": "personal", "product": "personal", "wanted": 50000,
                 "income_type": "salaried", "income_self": 0, "old_emi": 0,
                 "expenses": 20000, "age": 30, "score": "unknown",
                 "buffer": "none", "branch_answers": {}})
    assert z["ceiling"] == 0 and z["verdict"]["verdict"] == "Don't borrow"
    assert apr(12.0, 0.0, 36) == 12.0
    assert apr(11.5, 2.0, 60) > 11.5


def test_parse_score_free_text_to_bands():
    from rules.questions import parse_score
    assert parse_score("780")[0] == "750+"
    assert parse_score("Score is 720")[0] == "700-750"
    assert parse_score("660")[0] == "650-700"
    assert parse_score("550")[0] == "below650"
    assert parse_score("850")[0] == "750+"
    assert parse_score("don't know")[0] == "unknown"
    assert parse_score("")[0] == "unknown"
    assert parse_score("never taken a loan")[0] == "no_history"
    assert parse_score("first time borrower")[0] == "no_history"
    assert parse_score("abc")[0] == "unknown"


def test_sub_purpose_maps_to_known_products():
    from rules.questions import SUB_OPTIONS, product_for_sub, is_productive
    from rules import config
    known = set(config.BASE_BANDS) | {"unknown"}
    band_of = {"home": "home", "lap": "lap_bank", "two_wheeler": "two_wheeler",
               "car": "lap_bank", "business": "business", "personal": "personal_bank",
               "unknown": "personal_bank"}
    n = 0
    for _p, opts in SUB_OPTIONS.items():
        for c, _l, prod in opts:
            assert product_for_sub(c) == prod
            assert band_of[prod] in known
            n += 1
    assert n >= 25
    assert is_productive({"sub_purpose": "vehicle_earn", "purpose": "vehicle"}) is True
    assert is_productive({"sub_purpose": "vehicle_2w_new", "purpose": "vehicle"}) is False
    assert is_productive({"sub_purpose": "biz_stock", "purpose": "business"}) is True
    # legacy answers without sub_purpose keep old behavior
    assert is_productive({"purpose": "vehicle"}) is None
    assert is_productive({"purpose": "business"}) is True
