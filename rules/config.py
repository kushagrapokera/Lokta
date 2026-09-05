"""Single source of truth. Mirrors RULES.md / THRESHOLDS_SEPT2026.md.
Only file edited in live follow-up. No other module may define numbers."""

REPO_RATE = 5.25

# Base fair bands (min, max) Sept 2026, best profile. Source in THRESHOLDS Sec 0.
BASE_BANDS = {
    "home": (8.40, 9.80),
    "personal_bank": (10.0, 18.0),
    "lap_bank": (9.5, 11.5),
    "two_wheeler": (10.5, 24.0),
    "business": (11.0, 24.0),
    "gold": (9.0, 12.0),
}

# Max EMI share caps — LOCKED (THRESHOLDS Sec 1).
MAX_EMI_SHARE_SALARIED = 0.55
MAX_EMI_SHARE_SELF_EMPLOYED = 0.45
MAX_EMI_SHARE_INFORMAL = 0.30
MAX_EMI_SHARE_INFORMAL_WITH_BUFFER = 0.35

# O1/O2 thresholds — LOCKED.
WANT_VS_SAFE_BORROW_LESS = 1.5
STRESS_INCOME_DROP = 0.20
STRESS_RATE_HIKE = 2.0
HIGH_COST_RATE = 25.0

# O3 adjustments (my judgement, THRESHOLDS Sec 3).
ADJ_SCORE_750_PLUS = -1.0
ADJ_SCORE_700_750 = -0.5
ADJ_SCORE_650_700 = 0.5
ADJ_SCORE_BELOW_650 = 1.5
ADJ_UNKNOWN_WIDEN = 2.0
ADJ_JOB_STABLE = -0.5
ADJ_JOB_NEW = 0.5
ADJ_BOUNCE_ONE = 1.0
ADJ_BOUNCE_MULTI = 2.0
ADJ_CARD_HIGH = 1.0
ADJ_LAP_RESIDENTIAL = -4.0
ADJ_LAP_COMMERCIAL = -3.0
BAND_MIN_WIDTH = 1.5

# Missing-expenses fallback — LOCKED. Never treat missing spend as zero.
EXPENSE_ESTIMATE_PCT = 0.40

# Wanted above this multiple of monthly safe income surfaces the collateral
# question outside the self-employed branch (LAP alternative). My judgement.
LAP_SUGGEST_INCOME_MULT = 10

# Tenure caps.
RETIRE_AGE = 65
RETIRE_AGE_SALARIED = 60
PRODUCT_MAX_TENURE_YRS = {
    "home": 30,
    "lap": 20,
    "personal": 5,
    "two_wheeler": 7,
    "business": 5,
    "gold": 3,
}
