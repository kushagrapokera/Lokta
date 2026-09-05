"""One-sentence why per number."""


def explain(o: dict) -> dict:
    amount_reason = (
        f"Use Rs.{o.get('amount', {}).get('use', 0):,.0f} because bank sees "
        f"Rs.{o.get('amount', {}).get('lender', 0):,.0f} but safe is "
        f"Rs.{o.get('amount', {}).get('safe', 0):,.0f}."
    )
    rate_reason = (
        f"Fair {o.get('rate', {}).get('low', '?')}-{o.get('rate', {}).get('high', '?')}% "
        f"because {'; '.join((o.get('rate', {}).get('notes', []) or [])[:2]) or 'your profile'}."
    )
    ceiling_reason = (
        f"Ceiling Rs.{o.get('ceiling', 0):,.0f} because income x max EMI share minus old EMI; "
        f"stress {'passes' if o.get('stress_pass') else 'fails'}."
        + (" Expenses assumed 40% of income — fill actual spending for a tighter result."
           if o.get("estimated_exp") else "")
        + (" Old EMIs not given — ceiling may be overstated, confirm existing loans."
           if o.get("old_emi_unknown") else "")
        + ("" if o.get("age_given", True) else " Age assumed 35 — tenure rechecks when filled.")
    )
    return {
        "amount_reason": amount_reason,
        "rate_reason": rate_reason,
        "ceiling_reason": ceiling_reason,
    }
