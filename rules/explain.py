"""One-sentence why per number."""


def explain(o: dict) -> dict:
    return {
        "o2": f"Use Rs.{o.get('amount', {}).get('use', 0):,.0f} because bank sees "
              f"Rs.{o.get('amount', {}).get('lender', 0):,.0f} but safe is "
              f"Rs.{o.get('amount', {}).get('safe', 0):,.0f}.",
        "o3": f"Fair {o.get('rate', {}).get('low', '?')}-{o.get('rate', {}).get('high', '?')}% "
              f"because {'; '.join((o.get('rate', {}).get('notes', []) or [])[:2]) or 'your profile'}.",
        "o4": f"Ceiling Rs.{o.get('ceiling', 0):,.0f} because income x FOIR minus old EMI; "
              f"stress {'passes' if o.get('stress_pass') else 'fails'}."
              + (" Expenses assumed 40% of income — fill actual spending for a tighter result."
                 if o.get("estimated_exp") else "")
              + (" Old EMIs not given — ceiling may be overstated, confirm existing loans."
                 if o.get("old_emi_unknown") else "")
              + ("" if o.get("age_given", True) else " Age assumed 35 — tenure rechecks when filled."),
    }
