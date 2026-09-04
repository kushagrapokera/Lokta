"""Borrower Copilot — Streamlit UI. Flow only, no numbers here. All math in rules/."""

from rules import config
from rules.engine import compute
from rules.emi import max_tenure_months
from rules.income import normalize_income
from rules.questions import SUB_OPTIONS, branch_for, parse_score, product_for_sub

MUST = ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "S1"]
PURPOSES = list(SUB_OPTIONS.keys()) + ["Other"]


def _branch_steps(ans: dict) -> list:
    b = branch_for(ans)
    if b == "b":
        steps = ["A-B2", "A-B3", "A-B1", "A-B5"]
    elif b == "c":
        steps = ["A-C4", "A-C3"]
    else:
        steps = ["A-S1", "A-S3"]
    # Cross-branch injections: sub-purpose or size earns the question a place here.
    if ans.get("sub_purpose") == "home_lap" and "A-B3" not in steps:
        steps = steps + ["A-B3"]
    if ans.get("sub_purpose") == "personal_consolidate" and "A-C3" not in steps:
        steps = steps + ["A-C3"]
    try:
        inc = normalize_income(ans).get("income_safe", 0) or 0
        if inc > 0 and float(ans.get("wanted", 0) or 0) > config.LAP_SUGGEST_INCOME_MULT * float(inc) \
                and "A-B3" not in steps:
            steps = steps + ["A-B3"]
    except (TypeError, ValueError):
        pass
    return steps


def _steps(ans: dict) -> list:
    return MUST + _branch_steps(ans) + ["DONE"]


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
    sid = steps[s]

    st.set_page_config(page_title="Borrower Copilot", layout="centered")
    st.title("Borrower Copilot")
    st.caption("Self-check before you walk into a lender. No login, nothing stored.")
    st.progress((s + 1) / len(steps))
    st.caption(f"Step {s + 1} of {len(steps)}")

    if sid == "M1":
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

    elif sid == "M2":
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

    elif sid == "M3":
        st.subheader("What do you do?")
        ans["job_label"] = st.text_input("Occupation", ans.get("job_label", ""),
                                         placeholder="e.g. kirana store")
        st.subheader("How do you get paid?")
        t = st.radio("Income type", ["a", "b", "c"], format_func=lambda x: {
            "a": "a) Fixed salary in bank", "b": "b) Own shop/business, file ITR",
            "c": "c) Daily/weekly/gig cash"}[x])
        nav = _nav()
        if nav == "back":
            _go(nav)
        elif nav == "next":
            ans["income_type"] = t
            _go(nav)

    elif sid == "M4":
        st.subheader("Your net monthly in-hand income? (Rs.)")
        t_now = ans.get("income_type", "a")
        if t_now == "c":
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

    elif sid == "M5":
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

    elif sid == "M6":
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

    elif sid == "M7":
        st.subheader("Your age?")
        v = st.number_input("Age", min_value=18, max_value=70, value=int(ans.get("age", 35)))
        try:
            _m = max_tenure_months(int(v), str(ans.get("income_type", "a")).startswith("a"),
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

    elif sid == "M8":
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

    elif sid == "M9":
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

    elif sid == "S1":
        st.subheader("Have you already got a loan offer?")
        has = st.radio("Offer?", ["Skip", "Yes"], horizontal=True)
        if has == "Yes":
            ans["offer_rate"] = st.number_input("Offer rate %", min_value=0.0,
                                                value=float(ans.get("offer_rate", 14.0)))
            ans["offer_fee"] = st.number_input("Processing fee %", min_value=0.0,
                                               value=float(ans.get("offer_fee", 1.0)))
            try:
                _pm = max_tenure_months(int(ans.get("age", 35)),
                                        str(ans.get("income_type", "a")).startswith("a"),
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

    elif sid == "A-S1":
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

    elif sid == "A-S3":
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

    elif sid == "A-B2":
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

    elif sid == "A-B3":
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

    elif sid == "A-B1":
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

    elif sid == "A-B5":
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

    elif sid == "A-C4":
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

    elif sid == "A-C3":
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

    else:  # DONE
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
