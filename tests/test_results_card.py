"""Results + card view tests: shared compute, no drift, stress shown."""

from flask_app import flask_app
from rules.engine import compute


def _priya():
    return {"purpose": "personal", "product": "personal", "wanted": 800000,
            "purpose_label": "Personal use", "sub_label": "Wedding",
            "income_type": "salaried", "income_self": 110000, "co_income": 0,
            "co_active": False, "old_emi": 14000, "bounce": "no",
            "expenses": 55000, "age": 29, "score": "750+",
            "buffer": "3+", "job_vintage": "5yr+", "employer": "mnc",
            "card_util": "<30%", "branch_answers": {"job_stability": "5yr+"}}


def _drive(client, answers, desired="5"):
    c = client
    c.get("/")
    c.post("/step", data={"action": "next", "purpose": "Personal use",
                           "sub_code": "personal_wedding", "other_text": ""},
           follow_redirects=True)
    c.post("/step", data={"action": "next", "wanted": str(answers["wanted"])},
           follow_redirects=True)
    c.post("/step", data={"action": "next", "desired_years": desired},
           follow_redirects=True)
    c.post("/step", data={"action": "next", "job_label": "s",
                           "income_type": answers["income_type"]},
           follow_redirects=True)
    c.post("/step", data={"action": "next", "income_self": str(answers["income_self"]),
                           "has_co": "No", "co_income": "0", "co_changed": "no"},
           follow_redirects=True)
    c.post("/step", data={"action": "next", "old_emi": str(answers["old_emi"]),
                           "bounce": answers["bounce"], "bounce_count": "1"},
           follow_redirects=True)
    c.post("/step", data={"action": "next", "expenses": str(answers["expenses"])},
           follow_redirects=True)
    c.post("/step", data={"action": "next", "age": str(answers["age"])},
           follow_redirects=True)
    c.post("/step", data={"action": "next", "score_raw": "780"},
           follow_redirects=True)
    c.post("/step", data={"action": "confirm_yes"}, follow_redirects=True)
    c.post("/step", data={"action": "next", "buffer": answers["buffer"]},
           follow_redirects=True)
    c.post("/step", data={"action": "next", "has_offer": "Skip", "offer_rate": "14.0",
                           "offer_fee": "1.0", "offer_tenure": "60"},
           follow_redirects=True)
    c.post("/step", data={"action": "next", "job_vintage": "5yr+", "employer": "mnc"},
           follow_redirects=True)
    return c.post("/step", data={"action": "next", "card_util": "<30%"},
                  follow_redirects=True)


def test_engine_exposes_stress_and_share_numbers():
    from rules import config
    o = compute(_priya())
    assert "shock_income_surplus" in o and "shock_rate_emi" in o
    assert o["emi_share_used"] > 0 and o["max_emi_share"] == config.MAX_EMI_SHARE_SALARIED


def test_results_and_card_share_numbers():
    client = flask_app.test_client()
    results = _drive(client, _priya(), desired="3").get_data(as_text=True)
    card = client.get("/card").get_data(as_text=True)
    for needle in ["11.5", "46500", "Borrow"]:
        assert (needle in results) and (needle in card), needle
    assert "total interest" in results
    assert "shock" in results.lower()
    assert "relevant questions" in results or "you answered" in results


def test_card_download_is_plain_text():
    client = flask_app.test_client()
    _drive(client, _priya())
    r = client.get("/card/download")
    assert r.status_code == 200
    assert "NEGOTIATION CARD" in r.get_data(as_text=True)
