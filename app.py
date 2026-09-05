"""Borrower Copilot — Streamlit UI. Flow only, no numbers here. All math in rules/."""

from rules import config
from rules.engine import compute
from rules.emi import max_tenure_months
from rules.income import normalize_income
from rules.questions import (
    SUB_OPTIONS,
    SALARIED,
    SELF_EMPLOYED,
    INFORMAL,
    branch_for,
    parse_score,
    product_for_sub,
)

# --- Step names (readable screen IDs, in order) ---
STEP_LOAN_PURPOSE = "loan_purpose"        # was M1: purpose + sub-purpose
STEP_LOAN_AMOUNT = "loan_amount"          # was M2: how much wanted
STEP_WORK_TYPE = "work_type"              # was M3: job label + salaried/self/informal
STEP_MONTHLY_INCOME = "monthly_income"    # was M4: self + co-earner income
STEP_CURRENT_LOANS = "current_loans"      # was M5: old EMI + bounce history
STEP_MONTHLY_EXPENSES = "monthly_expenses"  # was M6: household expenses
STEP_AGE = "age"                          # was M7
STEP_CREDIT_SCORE = "credit_score"        # was M8
STEP_SAFETY_BACKUP = "safety_backup"      # was M9: buffer if income stops
STEP_EXISTING_OFFER = "existing_offer"    # was S1: loan offer to compare

# Branch follow-ups (max 5, all skippable)
STEP_JOB_STABILITY = "job_stability"              # was A-S1: vintage + employer
STEP_CARD_USAGE = "card_usage"                    # was A-S3: credit-card utilisation
STEP_YEARLY_ITR = "yearly_itr"                    # was A-B2: ITR per year
STEP_PROPERTY_COLLATERAL = "property_collateral"  # was A-B3: shop/house value
STEP_BUSINESS_AGE = "business_age"                # was A-B1: business vintage
STEP_BUSINESS_EXTRA_INCOME = "business_extra_income"  # was A-B5
STEP_VEHICLE_EXTRA_INCOME = "vehicle_extra_income"    # was A-C4
STEP_APP_LOANS_DETAIL = "app_loans_detail"            # was A-C3
STEP_RESULTS = "results"                      # was DONE

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

# Old short codes ("M1", "A-B3", "a"/"b"/"c") still accepted where answers
# come from outside, so old tests and saved data keep working.
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
    # Cross-branch injections: sub-purpose or size earns the question a place here.
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
    # Backward compat: also accept old "A-B3"/"A-C3" callers in tests.
    return steps


def _normalize_step(sid: str) -> str:
    return OLD_TO_NEW_STEP.get(sid, sid)


def _steps(ans: dict) -> list:
    return MUST_STEPS + _branch_steps(ans) + [STEP_RESULTS]


def _is_salaried(ans: dict) -> bool:
    return branch_for(ans) == SALARIED


def _nav(back=True, skip=False, nxt="Continue") -> str:
    import streamlit as st
    cols = st.columns(3 if skip else 2)
    out = ""
    if back and cols[0].button("Back"):
        out = "back"
    i = 1
    if skip and cols[i].button("Skip"):
        out = "skip"
        i = 2 if skip else 1
    if cols[i if skip else 1].button(nxt):
        out = "next"
    return out


def _go(nav: str) -> None:
    import streamlit as st
    if nav == "back":
        st.session_state.step = max(0, st.session_state.step - 1)
        st.rerun()
    elif nav in ("next", "skip"):
        st.session_state.step += 1
        st.rerun()


def main() -> None:
    import streamlit as st
    if "step" not in st.session_state:
        st.session_state.step = 0
    if "ans" not in st.session_state:
        st.session_state.ans = {}
    ans = st.session_state.ans
    steps = _steps(ans)
    s = min(st.session_state.step, len(steps) - 1)
    st.session_state.step = s
    sid = _normalize_step(steps[s])

    st.set_page_config(page_title="Borrower Copilot", layout="centered")
    st.title("Borrower Copilot")
    st.caption("Self-check before you walk into a lender. No login, nothing stored.")
    st.progress((s + 1) / len(steps))
    st.caption(f"Step {s + 1} of {len(steps)}")

    if sid == STEP_LOAN_PURPOSE:
        st.subheader("What do you need the loan for?")
        p = st.radio("Purpose", PURPOSES, horizontal=True)
        sub_code, sub_label = "", ""
        if p == "Other":
            other = st.text_input("Describe in your words", "")
        else:
            opts = SUB_OPTIONS[p]
            pick = st.radio("Which one fits best?", [l for _c, l, _pr in opts])
            sub_code = next(c for c, l, _pr in opts if l == pick)
            sub_label = pick
        nav = _nav(back=False)
        if nav == "next":
            amap = {"Home": "home", "Vehicle": "vehicle", "Education": "education",
                    "Personal use": "personal", "Business": "business",
                    "Other": ((other.strip() if p == "Other" else "") or "other")}
            ans["purpose"] = amap[p]
            ans["purpose_label"] = p if p != "Other" else (other.strip() or "Other")
            ans["sub_purpose"] = sub_code
            ans["sub_label"] = sub_label or ans["purpose_label"]
            ans["product"] = product_for_sub(sub_code) if sub_code else "unknown"
            _go(nav)

    elif sid == STEP_LOAN_AMOUNT:
        st.subheader("How much do you want? (Rs.)")
        v = st.number_input("Amount", min_value=0, value=int(ans.get("wanted", 0)), step=10000)
        nav = _nav()
        if nav == "back":
            _go(nav)
        elif nav == "next":
            if v <= 0:
                st.warning("Enter an amount above 0 to continue.")
            else:
                ans["wanted"] = v
                _go(nav)

    elif sid == STEP_WORK_TYPE:
        st.subheader("What do you do?")
        ans["job_label"] = st.text_input("Occupation", ans.get("job_label", ""),
                                         placeholder="e.g. kirana store")
        st.subheader("How do you get paid?")
        t = st.radio("Income type", [SALARIED, SELF_EMPLOYED, INFORMAL], format_func=lambda x: {
            SALARIED: "Fixed salary in bank",
            SELF_EMPLOYED: "Own shop/business, file ITR",
            INFORMAL: "Daily/weekly/gig cash"}[x])
        nav = _nav()
        if nav == "back":
            _go(nav)
        elif nav == "next":
            ans["income_type"] = t
            _go(nav)

    elif sid == STEP_MONTHLY_INCOME:
        st.subheader("Your net monthly in-hand income? (Rs.)")
        t_now = branch_for(ans)
        if t_now == INFORMAL:
            lo = st.number_input("LOW month income", min_value=0,
                                 value=int(ans.get("income_self", 0)), step=1000)
            hi = st.number_input("HIGH month income", min_value=0,
                                 value=int(ans.get("income_high", 0)), step=1000)
        else:
            lo = st.number_input("Yours", min_value=0,
                                 value=int(ans.get("income_self", 0)), step=1000)
            hi = 0
        has_co = st.radio("Does anyone else earn in family?", ["No", "Yes"], horizontal=True)
        co, ch = 0, "no"
        if has_co == "Yes":
            co = st.number_input("Their monthly income", min_value=0,
                                 value=int(ans.get("co_income", 0)), step=1000)
            ch = {"Steady": "no", "Stopped": "stopped"}[
                st.radio("Is that income steady right now?", ["Steady", "Stopped"], horizontal=True)]
        nav = _nav()
        if nav == "back":
            _go(nav)
        elif nav == "next":
            ans["income_self"] = lo
            ans["income_high"] = hi
            ans["co_income"] = co
            ans["co_active"] = has_co == "Yes"
            ans["co_changed"] = ch
            _go(nav)

    elif sid == STEP_CURRENT_LOANS:
        st.subheader("Total EMI + app-loan + BNPL you pay per month? (Rs.)")
        v = st.number_input("Old EMI", min_value=0, value=int(ans.get("old_emi", 0)), step=500)
        b, bc = "no", 0
        if v > 0:
            b = st.radio("Any EMI bounced in last 12 months?", ["no", "yes", "unknown"], horizontal=True)
            bc = st.number_input("How many bounces?", min_value=1,
                                 value=int(ans.get("bounce_count", 1) or 1)) if b == "yes" else 1
        nav = _nav()
        if nav == "back":
            _go(nav)
        elif nav == "next":
            ans["old_emi"] = v
            ans["bounce"] = b
            ans["bounce_count"] = int(bc)
            if v == 0:
                ans["bounce_note"] = "no current loans, bounce screen skipped"
            else:
                ans.pop("bounce_note", None)
            _go(nav)

    elif sid == STEP_MONTHLY_EXPENSES:
        if "_exp_pending" in ans:
            st.subheader(f"We assumed Rs.{ans['_exp_pending']:,.0f} monthly spending. Correct?")
            c1, c2 = st.columns(2)
            if c1.button("Yes, continue"):
                ans.pop("_exp_pending", None)
                st.session_state.step += 1
                st.rerun()
            if c2.button("Edit"):
                ans.pop("_exp_pending", None)
                st.rerun()
        else:
            st.subheader("Total household expenses per month incl rent? (Rs.)")
            v = st.number_input("Expenses", min_value=0, value=int(ans.get("expenses", 0)), step=1000)
            nav = _nav()
            if nav == "back":
                _go(nav)
            elif nav == "next":
                if v <= 0:
                    inc0 = normalize_income(ans).get("income_safe", 0) or 0
                    ans["_exp_pending"] = round(config.EXPENSE_ESTIMATE_PCT * inc0, 2)
                    ans["expenses"] = 0
                    st.rerun()
                else:
                    ans["expenses"] = v
                    _go(nav)

    elif sid == STEP_AGE:
        st.subheader("Your age?")
        v = st.number_input("Age", min_value=18, max_value=70, value=int(ans.get("age", 35)))
        try:
            _m = max_tenure_months(int(v), _is_salaried(ans),
                                   str(ans.get("product", "personal")))
            if _m <= 84:
                st.info(f"Lenders cap tenure around {_m // 12} years at this age, so EMIs run higher.")
        except (TypeError, ValueError):
            pass
        nav = _nav()
        if nav == "back":
            _go(nav)
        elif nav == "next":
            ans["age"] = int(v)
            _go(nav)

    elif sid == STEP_CREDIT_SCORE:
        if "_score_pending" in ans:
            band, label = ans["_score_pending"]
            st.subheader(f"We read this as: {label}. Correct?")
            c1, c2 = st.columns(2)
            if c1.button("Yes, continue"):
                ans["score"] = band
                ans.pop("_score_pending", None)
                ans.pop("score_raw", None)
                st.session_state.step += 1
                st.rerun()
            if c2.button("Edit"):
                ans.pop("_score_pending", None)
                st.rerun()
        else:
            st.subheader("Credit score?")
            raw = st.text_input("Type your score", ans.get("score_raw", ""),
                                placeholder="e.g. 780, or 'don't know'")
            nav = _nav()
            if nav == "back":
                _go(nav)
            elif nav == "next":
                ans["score_raw"] = raw
                ans["_score_pending"] = list(parse_score(raw))
                st.rerun()

    elif sid == STEP_SAFETY_BACKUP:
        st.subheader("If income stops for 2 months, how will you pay EMI?")
        bf = st.radio("Backup", ["none", "family", "1-2", "3+"], format_func=lambda x: {
            "none": "No backup", "family": "Family/friend covers 1-2 EMIs",
            "1-2": "Savings 1-2 months", "3+": "Savings 3+ months"}[x])
        nav = _nav()
        if nav == "back":
            _go(nav)
        elif nav == "next":
            ans["buffer"] = bf
            _go(nav)

    elif sid == STEP_EXISTING_OFFER:
        st.subheader("Have you already got a loan offer?")
        has = st.radio("Offer?", ["Skip", "Yes"], horizontal=True)
        if has == "Yes":
            ans["offer_rate"] = st.number_input("Offer rate %", min_value=0.0,
                                                value=float(ans.get("offer_rate", 14.0)))
            ans["offer_fee"] = st.number_input("Processing fee %", min_value=0.0,
                                               value=float(ans.get("offer_fee", 1.0)))
            try:
                _pm = max_tenure_months(int(ans.get("age", 35)),
                                        _is_salaried(ans),
                                        str(ans.get("product", "personal")))
                _pm = _pm or 60
                _std = _pm if str(ans.get("product", "personal")) in ("home", "lap") else min(_pm, 60)
            except (TypeError, ValueError):
                _std = 60
            ans["offer_tenure"] = st.number_input("Offer tenure (months)", min_value=6,
                                                  value=int(ans.get("offer_tenure", _std)))
        nav = _nav(back=True, skip=False, nxt="Continue")
        if nav == "back":
            _go(nav)
        elif nav == "next":
            if has == "Skip":
                for k in ("offer_rate", "offer_fee", "offer_tenure"):
                    ans.pop(k, None)
            _go(nav)

    elif sid == STEP_JOB_STABILITY:
        st.subheader("How long in your current job?")
        v = st.radio("Job vintage", ["<1yr", "1-3yr", "5yr+"], horizontal=True)
        e = st.radio("Employer type?", ["Small company / Other", "MNC / Govt / Large co."],
                     horizontal=True, index=0)
        nav = _nav(skip=True)
        if nav == "back":
            _go(nav)
        elif nav == "skip":
            ans.pop("job_vintage", None)
            ans.pop("employer", None)
            _go(nav)
        elif nav == "next":
            ans["job_vintage"] = v
            ans["employer"] = "mnc" if e.startswith("MNC") else "other"
            _go(nav)

    elif sid == STEP_CARD_USAGE:
        st.subheader("How much of your credit card limit do you use?")
        v = st.radio("Card use", ["No card", "<30%", "30-70%", ">70%"], horizontal=True)
        nav = _nav(skip=True)
        if nav == "back":
            _go(nav)
        elif nav == "skip":
            ans.pop("card_util", None)
            _go(nav)
        elif nav == "next":
            ans["card_util"] = None if v == "No card" else v
            _go(nav)

    elif sid == STEP_YEARLY_ITR:
        st.subheader("What does your ITR show per year? (Rs.)")
        v = st.number_input("ITR annual", min_value=0, value=int(ans.get("itr_annual", 0)), step=10000)
        nav = _nav(skip=True)
        if nav == "back":
            _go(nav)
        elif nav == "skip":
            ans.pop("itr_annual", None)
            _go(nav)
        elif nav == "next":
            ans["itr_annual"] = v
            _go(nav)

    elif sid == STEP_PROPERTY_COLLATERAL:
        st.subheader("Do you own a shop or house free of any loan?")
        v = st.number_input("Its value in Rs. (0 if none)", min_value=0,
                            value=int(ans.get("collateral_value", 0)), step=50000)
        free, ctype = False, "residential"
        if v > 0:
            free = st.radio("Loan-free?", ["No", "Yes"], horizontal=True) == "Yes"
            ctype = st.radio("Property type?", ["residential", "commercial"], horizontal=True)
        nav = _nav(skip=True)
        if nav == "back":
            _go(nav)
        elif nav == "skip":
            for k in ("collateral_value", "collateral_free", "collateral_type"):
                ans.pop(k, None)
            _go(nav)
        elif nav == "next":
            ans["collateral_value"] = v
            if v > 0:
                ans["collateral_free"] = free
                ans["collateral_type"] = ctype
            else:
                ans.pop("collateral_free", None)
                ans.pop("collateral_type", None)
            _go(nav)

    elif sid == STEP_BUSINESS_AGE:
        st.subheader("How old is your business?")
        v = st.radio("Business vintage", ["<2yr", "2-10yr", "10yr+"], horizontal=True)
        nav = _nav(skip=True)
        if nav == "back":
            _go(nav)
        elif nav == "skip":
            ans.pop("biz_vintage", None)
            _go(nav)
        elif nav == "next":
            ans["biz_vintage"] = v
            _go(nav)

    elif sid == STEP_BUSINESS_EXTRA_INCOME:
        st.subheader("Will this loan earn you extra every month? How much? (Rs.)")
        v = st.number_input("Extra per month (0 if none)", min_value=0,
                            value=int(ans.get("biz_extra_income", 0)), step=1000)
        nav = _nav(skip=True)
        if nav == "back":
            _go(nav)
        elif nav == "skip":
            ans.pop("biz_extra_income", None)
            _go(nav)
        elif nav == "next":
            ans["biz_extra_income"] = v
            _go(nav)

    elif sid == STEP_VEHICLE_EXTRA_INCOME:
        st.subheader("Will this asset increase your income? By how much per month? (Rs.)")
        v = st.number_input("Extra per month (0 if none)", min_value=0,
                            value=int(ans.get("scooter_extra_income", 0)), step=500)
        nav = _nav(skip=True)
        if nav == "back":
            _go(nav)
        elif nav == "skip":
            ans.pop("scooter_extra_income", None)
            _go(nav)
        elif nav == "next":
            ans["scooter_extra_income"] = v
            _go(nav)

    elif sid == STEP_APP_LOANS_DETAIL:
        st.subheader("App loans outstanding? (Rs. and rate %)")
        o = st.number_input("Outstanding (0 if none)", min_value=0,
                            value=int(ans.get("app_outstanding", 0)), step=1000)
        r = 0.0
        if o > 0:
            r = st.number_input("Rate %", min_value=0.0,
                                value=float(ans.get("app_rate", 0.0)))
        nav = _nav(skip=True)
        if nav == "back":
            _go(nav)
        elif nav == "skip":
            for k in ("app_outstanding", "app_rate"):
                ans.pop(k, None)
            _go(nav)
        elif nav == "next":
            ans["app_outstanding"] = o
            if o > 0:
                ans["app_rate"] = r
            else:
                ans.pop("app_rate", None)
            _go(nav)

    else:  # results
        ans.pop("_score_pending", None)
        ans.pop("_exp_pending", None)
        ba = {k: v for k, v in ans.items()
              if k in ("job_vintage", "employer", "card_util", "itr_annual", "collateral_value",
                       "biz_vintage", "biz_extra_income", "scooter_extra_income",
                       "app_outstanding", "app_rate")
              and v not in (None, "", "skip")}
        ans["branch_answers"] = ba
        o = compute(ans)
        _for = f"For: {ans.get('purpose_label', '')} — {ans.get('sub_label', '')}"
        if ans.get("job_label", "").strip():
            _for += f" ({ans['job_label'].strip()})"
        st.caption(_for)
        st.header(f"Verdict: {o['verdict']['verdict']}")
        st.write(o["verdict"]["reason"])
        st.caption(f"Flip: {o['verdict']['flip']}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Bank may sanction", f"Rs.{o['amount']['lender']:,.0f}")
        c2.metric("Safe for you", f"Rs.{o['amount']['use']:,.0f}")
        c3.metric("EMI ceiling", f"Rs.{o['ceiling']:,.0f}")
        st.write(f"Fair rate: {o['rate']['low']}% - {o['rate']['high']}% "
                 f"(APR {o['fair_apr'][0]}% - {o['fair_apr'][1]}%).")
        st.write(f"Your EMI for wanted Rs.{o['amount']['wanted']:,.0f}: Rs.{o['new_emi']:,.0f} "
                 f"over {o['std_months']} months. Stress: {'passes' if o['stress_pass'] else 'fails'}.")
        st.caption(o["why"]["o2"] + " " + o["why"]["o3"] + " " + o["why"]["o4"])
        _rng = ""
        if float(ans.get("income_high", 0) or 0) > 0:
            _rng = (f", income range Rs.{float(ans.get('income_self', 0)):,.0f}"
                    f"–{float(ans.get('income_high', 0)):,.0f}")
        st.caption(f"Counted: old EMI Rs.{float(ans.get('old_emi', 0)):,.0f}"
                   f"{' (' + ans['bounce_note'] + ')' if ans.get('bounce_note') else ''}, "
                   f"spending Rs.{o.get('expenses_used', 0):,.0f}"
                   f"{' (assumed — edit in expenses step)' if o.get('estimated_exp') else ''}"
                   f"{_rng}.")
        if o["rate"]["unknown"] and "collateral" not in " ".join(o["rate"]["notes"]):
            st.info("No credit history: a secured option (loan against house/shop or gold) can tighten this band.")
        st.subheader("Negotiation Card")
        for line in o["card"]["lines"]:
            st.write("- " + line)
        st.caption(f"Confidence: {o['confidence']['level']}. Ranges are ranges; fewer answers = wider band.")
        if st.button("Restart"):
            st.session_state.step = 0
            st.session_state.ans = {}
            st.rerun()


if __name__ == "__main__":
    main()
