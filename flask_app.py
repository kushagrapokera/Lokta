"""Borrower Copilot — Flask UI. Flow only, no numbers here. All math in rules/.

Run: conda run -n lokta python flask_app.py  (opens http://127.0.0.1:5000)
"""

from flask import Flask, Response, redirect, render_template, request, session, url_for

from rules import config
from rules.emi import max_tenure_months
from rules.engine import compute
from rules.income import normalize_income
from rules.questions import (
    INFORMAL,
    SALARIED,
    SELF_EMPLOYED,
    SUB_OPTIONS,
    branch_for,
    parse_score,
    product_for_sub,
)

# Step order / branching lives in rules/flow.py so every UI asks the same order.
from rules.flow import (
    STEP_APP_LOANS_DETAIL,
    STEP_BUSINESS_AGE,
    STEP_BUSINESS_EXTRA_INCOME,
    STEP_CARD_USAGE,
    STEP_JOB_STABILITY,
    STEP_PROPERTY_COLLATERAL,
    STEP_RESULTS,
    STEP_VEHICLE_EXTRA_INCOME,
    STEP_YEARLY_ITR,
    _branch_steps,
    _normalize_step,
    _steps,
)

# Must-screen id -> answer keys proving it was answered (empty = always counts).
MUST_ANSWER_KEYS = {
    "loan_purpose": ("sub_purpose",),
    "loan_amount": ("wanted",),
    "repayment_tenure": ("desired_years",),
    "work_type": ("income_type",),
    "monthly_income": ("income_self",),
    "current_loans": ("old_emi",),
    "monthly_expenses": ("expenses",),
    "age": ("age",),
    "credit_score": ("score",),
    "safety_backup": ("buffer",),
    "existing_offer": (),
}
flask_app = Flask(__name__)
flask_app.secret_key = "dev-borrower-copilot-not-for-prod"

BRANCH_SIDS = {
    STEP_JOB_STABILITY,
    STEP_CARD_USAGE,
    STEP_YEARLY_ITR,
    STEP_PROPERTY_COLLATERAL,
    STEP_BUSINESS_AGE,
    STEP_BUSINESS_EXTRA_INCOME,
    STEP_VEHICLE_EXTRA_INCOME,
    STEP_APP_LOANS_DETAIL,
}

TITLES = {
    "loan_purpose": "What do you need the loan for?",
    "loan_amount": "How much do you want? (Rs.)",
    "repayment_tenure": "In how many years do you want to repay?",
    "work_type": "What do you do?",
    "monthly_income": "Your net monthly in-hand income? (Rs.)",
    "current_loans": "Total EMI + app-loan + BNPL you pay per month? (Rs.)",
    "monthly_expenses": "Total household expenses per month incl rent? (Rs.)",
    "age": "Your age?",
    "credit_score": "Credit score?",
    "safety_backup": "If income stops for 2 months, how will you pay EMI?",
    "existing_offer": "Have you already got a loan offer?",
    "job_stability": "How long in your current job?",
    "card_usage": "How much of your credit card limit do you use?",
    "yearly_itr": "What does your ITR show per year? (Rs.)",
    "property_collateral": "Do you own a shop or house free of any loan?",
    "business_age": "How old is your business?",
    "business_extra_income": "Will this loan earn you extra every month? How much? (Rs.)",
    "vehicle_extra_income": "Will this asset increase your income? By how much per month? (Rs.)",
    "app_loans_detail": "App loans outstanding? (Rs. and rate %)",
}


def _get_ans() -> dict:
    return dict(session.get("ans", {}))


def _save(ans: dict, step: int) -> None:
    session["ans"] = ans
    session["step"] = step


def _current():
    ans = _get_ans()
    steps = _steps(ans)
    s = min(int(session.get("step", 0)), len(steps) - 1)
    sid = _normalize_step(steps[s])
    return ans, steps, s, sid


def _is_salaried(ans: dict) -> bool:
    return branch_for(ans) == SALARIED


def _default_offer_tenure(ans: dict) -> int:
    try:
        pm = max_tenure_months(int(ans.get("age", 35)), _is_salaried(ans),
                               str(ans.get("product", "personal")))
        pm = pm or 60
        return pm if str(ans.get("product", "personal")) in ("home", "lap") else min(pm, 60)
    except (TypeError, ValueError):
        return 60


@flask_app.route("/")
def index():
    session.setdefault("ans", {})
    session.setdefault("step", 0)
    return redirect(url_for("step"))


@flask_app.route("/health")
def health():
    return {"ok": True}


@flask_app.route("/restart", methods=["GET", "POST"])
def restart():
    session["ans"] = {}
    session["step"] = 0
    return redirect(url_for("step"))


@flask_app.route("/step", methods=["GET", "POST"])
def step():
    ans, steps, s, sid = _current()

    if request.method == "GET":
        return _render(ans, steps, s, sid)

    action = request.form.get("action", "next")
    if action == "back":
        _save(ans, max(0, s - 1))
        return redirect(url_for("step"))
    if action == "confirm_yes":
        if "_exp_pending" in ans:
            ans.pop("_exp_pending", None)
            _save(ans, s + 1)
            return redirect(url_for("step"))
        if "_score_pending" in ans:
            band, _label = ans.pop("_score_pending")
            ans["score"] = band
            ans.pop("score_raw", None)
            _save(ans, s + 1)
            return redirect(url_for("step"))
    if action == "confirm_edit":
        ans.pop("_exp_pending", None)
        ans.pop("_score_pending", None)
        _save(ans, s)
        return redirect(url_for("step"))
    if action == "skip" and sid in BRANCH_SIDS:
        # Skip clears only that step's keys (each branch below names its own).
        for k in ("job_vintage", "employer", "card_util", "itr_annual", "collateral_value",
                  "collateral_free", "collateral_type", "biz_vintage", "biz_extra_income",
                  "scooter_extra_income", "app_outstanding", "app_rate"):
            # only clear keys belonging to this step; keep it simple and safe:
            pass
        if sid == "job_stability":
            ans.pop("job_vintage", None)
            ans.pop("employer", None)
        elif sid == "card_usage":
            ans.pop("card_util", None)
        elif sid == "yearly_itr":
            ans.pop("itr_annual", None)
        elif sid == "property_collateral":
            for k in ("collateral_value", "collateral_free", "collateral_type"):
                ans.pop(k, None)
        elif sid == "business_age":
            ans.pop("biz_vintage", None)
        elif sid == "business_extra_income":
            ans.pop("biz_extra_income", None)
        elif sid == "vehicle_extra_income":
            ans.pop("scooter_extra_income", None)
        elif sid == "app_loans_detail":
            for k in ("app_outstanding", "app_rate"):
                ans.pop(k, None)
        _save(ans, s + 1)
        return redirect(url_for("step"))

    # action == "next": parse + validate per step
    err = _apply(sid, ans, request.form)
    if err:
        return _render(ans, steps, s, sid, error=err)
    # intermediate confirm states stay on same step
    if "_exp_pending" in ans or "_score_pending" in ans:
        _save(ans, s)
    else:
        _save(ans, s + 1)
    return redirect(url_for("step"))


def _apply(sid: str, ans: dict, form) -> str | None:
    def num(name: str, default: float = 0.0) -> float:
        try:
            v = float(form.get(name, default))
            return v if v >= 0 else default
        except (TypeError, ValueError):
            return default

    if sid == "loan_purpose":
        # Default is set to Personal Use
        p = form.get("purpose", "Personal use")
        sub_code = form.get("sub_code", "")
        other = (form.get("other_text", "") or "").strip()
        if p == "Other":
            ans["purpose"] = "other"
            ans["purpose_label"] = other or "Other"
            ans["sub_purpose"] = ""
            ans["sub_label"] = ans["purpose_label"]
            ans["product"] = "unknown"
        else:
            opts = SUB_OPTIONS.get(p, [])
            labels = {c: (l, pr) for c, l, pr in opts}
            if sub_code not in labels:
                return "Pick an option that belongs to the chosen purpose."
            amap = {"Home": "home", "Vehicle": "vehicle", "Education": "education",
                    "Personal use": "personal", "Business": "business"}
            ans["purpose"] = amap.get(p, "other")
            ans["purpose_label"] = p
            ans["sub_purpose"] = sub_code
            ans["sub_label"] = labels[sub_code][0]
            ans["product"] = product_for_sub(sub_code) if sub_code else "unknown"
        return None

    if sid == "loan_amount":
        v = num("wanted", 0)
        if v <= 0:
            return "Enter an amount above 0 to continue."
        ans["wanted"] = v
        return None

    if sid == "repayment_tenure":
        try:
            years = float(form.get("desired_years", 0) or 0)
        except (TypeError, ValueError):
            years = 0
        if years <= 0:
            return "Enter years above 0 to continue."
        ans["desired_years"] = years
        return None

    if sid == "work_type":
        ans["job_label"] = (form.get("job_label", "") or "")
        t = form.get("income_type", SALARIED)
        if t not in (SALARIED, SELF_EMPLOYED, INFORMAL):
            return "Pick how you get paid."
        ans["income_type"] = t
        return None

    if sid == "monthly_income":
        t_now = branch_for(ans)
        lo = num("income_self", 0)
        hi = num("income_high", 0) if t_now == INFORMAL else 0
        has_co = form.get("has_co", "No") == "Yes"
        co = num("co_income", 0) if has_co else 0
        ans["income_self"] = lo
        ans["income_high"] = hi
        ans["co_income"] = co
        ans["co_active"] = has_co
        ans["co_changed"] = form.get("co_changed", "no") if has_co else "no"
        return None

    if sid == "current_loans":
        v = num("old_emi", 0)
        b = form.get("bounce", "no")
        bc = int(num("bounce_count", 1) or 1)
        ans["old_emi"] = v
        ans["bounce"] = b
        ans["bounce_count"] = int(bc)
        if v == 0:
            ans["bounce_note"] = "no current loans, bounce screen skipped"
        else:
            ans.pop("bounce_note", None)
        return None

    if sid == "monthly_expenses":
        v = num("expenses", 0)
        if v <= 0:
            inc0 = normalize_income(ans).get("income_safe", 0) or 0
            ans["_exp_pending"] = round(config.EXPENSE_ESTIMATE_PCT * inc0, 2)
            ans["expenses"] = 0
        else:
            ans["expenses"] = v
        return None

    if sid == "age":
        try:
            ans["age"] = int(num("age", 35))
        except (TypeError, ValueError):
            return "Enter a valid age."
        return None

    if sid == "credit_score":
        raw = (form.get("score_raw", "") or "")
        ans["score_raw"] = raw
        ans["_score_pending"] = list(parse_score(raw))
        return None

    if sid == "safety_backup":
        ans["buffer"] = form.get("buffer", "none")
        return None

    if sid == "existing_offer":
        has = form.get("has_offer", "Skip")
        if has == "Skip":
            for k in ("offer_rate", "offer_fee", "offer_tenure"):
                ans.pop(k, None)
        else:
            ans["offer_rate"] = num("offer_rate", 14.0)
            ans["offer_fee"] = num("offer_fee", 1.0)
            ans["offer_tenure"] = int(num("offer_tenure", _default_offer_tenure(ans)) or 60)
        return None

    if sid == "job_stability":
        ans["job_vintage"] = form.get("job_vintage", "1-3yr")
        ans["employer"] = "mnc" if form.get("employer", "other") == "mnc" else "other"
        return None

    # Branch: salaried (fixed salary) only.
    if sid == "card_usage":
        v = form.get("card_util", "No card")
        ans["card_util"] = None if v == "No card" else v
        return None

    # Branch: self_employed (own shop/business) only.
    if sid == "yearly_itr":
        ans["itr_annual"] = num("itr_annual", 0)
        return None

    # Branch: self_employed, plus home_lap sub-purpose or wanted > 10x income (any branch).
    if sid == "property_collateral":
        v = num("collateral_value", 0)
        ans["collateral_value"] = v
        if v > 0:
            ans["collateral_free"] = form.get("collateral_free", "No") == "Yes"
            ans["collateral_type"] = form.get("collateral_type", "residential")
        else:
            ans.pop("collateral_free", None)
            ans.pop("collateral_type", None)
        return None

    # Branch: self_employed (own shop/business) only.
    if sid == "business_age":
        ans["biz_vintage"] = form.get("biz_vintage", "2-10yr")
        return None

    # Branch: self_employed (own shop/business) only.
    if sid == "business_extra_income":
        ans["biz_extra_income"] = num("biz_extra_income", 0)
        return None

    # Branch: informal (daily/weekly/gig cash) only.
    if sid == "vehicle_extra_income":
        ans["scooter_extra_income"] = num("scooter_extra_income", 0)
        return None

    # Branch: informal, plus personal_consolidate sub-purpose (any branch).
    if sid == "app_loans_detail":
        o = num("app_outstanding", 0)
        ans["app_outstanding"] = o
        if o > 0:
            ans["app_rate"] = num("app_rate", 0.0)
        else:
            ans.pop("app_rate", None)
        return None

    return None


def _results_bundle(ans: dict):
    """Shared compute for results + card so numbers never drift between views."""
    ans = dict(ans)
    ans.pop("_score_pending", None)
    ans.pop("_exp_pending", None)
    ba = {k: v for k, v in ans.items()
          if k in ("job_vintage", "employer", "card_util", "itr_annual", "collateral_value",
                    "biz_vintage", "biz_extra_income", "scooter_extra_income",
                    "app_outstanding", "app_rate")
          and v not in (None, "", "skip")}
    ans["branch_answers"] = ba
    o = compute(ans)
    for_line = f"For: {ans.get('purpose_label', '')} — {ans.get('sub_label', '')}"
    if ans.get("job_label", "").strip():
        for_line += f" ({ans['job_label'].strip()})"
    branch_total = len(_branch_steps(ans))
    must_answered = sum(1 for keys in MUST_ANSWER_KEYS.values()
                        if not keys or any(k in ans for k in keys))
    total = len(MUST_ANSWER_KEYS) + branch_total
    answered = min(must_answered + len(ba), total)
    return ans, o, for_line, answered, total


@flask_app.route("/card")
def card():
    ans, o, for_line, answered, total = _results_bundle(_get_ans())
    session["ans"] = ans
    return render_template("card.html", o=o, for_line=for_line,
                           answered=answered, total=total)


@flask_app.route("/card/download")
def card_download():
    ans, o, for_line, answered, total = _results_bundle(_get_ans())
    body = "\n".join([
        "BORROWER NEGOTIATION CARD", for_line,
        f"Verdict: {o['verdict']['verdict']} — {o['verdict']['reason']}",
        f"Fair rate: {o['rate']['low']}-{o['rate']['high']}% "
        f"(APR {o['fair_apr'][0]}-{o['fair_apr'][1]}%)",
        f"EMI ceiling: Rs.{o['ceiling']:,.0f}/month",
        f"Bank may sanction Rs.{o['amount']['lender']:,.0f} / "
        f"Safe Rs.{o['amount']['safe']:,.0f} — use Rs.{o['amount']['use']:,.0f}",
        f"Confidence: {o['confidence']['level']} ({answered}/{total} questions)",
    ] + o["card"]["lines"])
    return Response(body, mimetype="text/plain",
                    headers={"Content-Disposition": "attachment;filename=negotiation-card.txt"})


def _render(ans: dict, steps: list, s: int, sid: str, error: str = ""):
    if sid == STEP_RESULTS:
        ans, o, for_line, answered, total = _results_bundle(ans)
        session["ans"] = ans
        return render_template("results.html", o=o, for_line=for_line,
                               answered=answered, total=total)

    if "_exp_pending" in ans and sid == "monthly_expenses":
        return render_template("step.html", sid=sid, title=TITLES[sid], idx=s + 1,
                               total=len(steps), pct=round((s + 1) / len(steps) * 100),
                               confirm="expenses", pending=f"{ans['_exp_pending']:,.0f}",
                               pending_label="", show_back=True, skippable=False, error=error,
                               ans=ans)
    if "_score_pending" in ans and sid == "credit_score":
        band, label = ans["_score_pending"]
        return render_template("step.html", sid=sid, title=TITLES[sid], idx=s + 1,
                               total=len(steps), pct=round((s + 1) / len(steps) * 100),
                               confirm="score", pending="", pending_label=label,
                               show_back=True, skippable=False, error=error, ans=ans)

    note = ""
    if sid == "age":
        try:
            m = max_tenure_months(int(ans.get("age", 35)), _is_salaried(ans),
                                  str(ans.get("product", "personal")))
            if m <= 84:
                note = f"Lenders cap tenure around {m // 12} years at this age, so EMIs run higher."
        except (TypeError, ValueError):
            pass

    max_years = 0
    try:
        max_years = (max_tenure_months(int(ans.get("age", 35)), _is_salaried(ans),
                                       str(ans.get("product", "personal"))) or 60) // 12
    except (TypeError, ValueError):
        max_years = 5
    if sid == "repayment_tenure" and max_years > 0:
        note = f"Lenders typically allow up to {max_years} years for your age and product. Your pace is used as-is."

    return render_template(
        "step.html", sid=sid, title=TITLES.get(sid, sid), idx=s + 1, total=len(steps),
        pct=round((s + 1) / len(steps) * 100), confirm="", pending="", pending_label="",
        show_back=s > 0, skippable=sid in BRANCH_SIDS, error=error, note=note, ans=ans,
        purposes=list(SUB_OPTIONS.keys()) + ["Other"], sub_options=SUB_OPTIONS,
        cur_purpose=ans.get("purpose_label", "Personal use"),
        cur_sub=ans.get("sub_purpose", ""),
        other_text="" if ans.get("purpose_label") != "Other" else ans.get("purpose_label", ""),
        is_informal=branch_for(ans) == INFORMAL,
        default_tenure=_default_offer_tenure(ans),
        max_years=max_years,
    )


if __name__ == "__main__":
    flask_app.run(debug=True)
