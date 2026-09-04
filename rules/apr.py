"""APR: EMI on P, solve same EMI on (P-fee) by binary search 0-50%."""

from rules.emi import emi


def apr(nominal_rate_pct: float, fee_pct: float, months: int) -> float:
    try:
        fee_pct = float(fee_pct or 0)
    except (TypeError, ValueError):
        fee_pct = 0.0
    if months <= 0:
        return round(float(nominal_rate_pct or 0), 2)
    if fee_pct <= 0:
        return round(float(nominal_rate_pct or 0), 2)
    p = 100000.0
    fee_amt = p * fee_pct / 100.0
    target = emi(p, float(nominal_rate_pct), months)
    received = p - fee_amt
    lo, hi = 0.0, 50.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if emi(received, mid, months) < target:
            lo = mid
        else:
            hi = mid
    return round((lo + hi) / 2, 2)
