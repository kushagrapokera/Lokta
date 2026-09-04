"""Negotiation Card builder. One screen for the branch."""

from rules.apr import apr


def _f(x, default=0.0) -> float:
    try:
        v = float(x)
        return v if v >= 0 else default
    except (TypeError, ValueError):
        return default


def build_card(answers: dict, o: dict) -> dict:
    fair = o.get("rate", {})
    offer_rate = answers.get("offer_rate")
    try:
        offer_rate = float(offer_rate) if offer_rate not in (None, "") else None
    except (TypeError, ValueError):
        offer_rate = None
    lines = [
        f"Fair for your profile: {fair.get('low', '?')}% - {fair.get('high', '?')}%",
        f"EMI ceiling: Rs.{o.get('ceiling', 0):,.0f}/month. Do not cross it.",
        f"Why: {'; '.join((fair.get('notes', []) or [])[:3]) or 'based on your answers'}.",
    ]
    if offer_rate is not None:
        fee = _f(answers.get("offer_fee", 0))
        tenure = int(answers.get("offer_tenure", 0) or 0) or o.get("std_months", 60)
        oapr = apr(offer_rate, fee, tenure)
        flo, fhi = o.get("fair_apr", [fair.get("low", 0), fair.get("high", 0)])
        flag = "FAIR" if flo <= oapr <= fhi else ("COSTLY" if oapr > fhi else "GOOD")
        lines.append(f"Lender quotes {offer_rate}% + {fee}% fee over {tenure}mo "
                     f"(APR ~{oapr}%) => {flag} vs fair APR {flo}-{fhi}%.")
    else:
        lines.append("No offer entered: show this card before accepting any quote.")
    warn = o.get("verdict", {}).get("verdict", "")
    lines.append(f"Warning: {o.get('verdict', {}).get('reason', '')} [{warn}]")
    return {"lines": lines[:5]}
