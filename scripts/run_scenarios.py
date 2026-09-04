"""Batch-review scenarios. Real engine outputs only — no hand editing.
Run: conda run -n lokta python scripts/run_scenarios.py"""

import json
import pathlib

from rules.engine import compute

SCENARIOS = [
    {"id": "S1-kunal-fresher", "who": "Kunal, 24, Bengaluru, salaried fresher (<1yr startup), high card use.",
     "blanks": "S1 skipped.",
     "answers": {"purpose": "personal", "product": "personal", "wanted": 300000,
                 "income_type": "a", "income_self": 45000, "co_income": 0, "co_active": False,
                 "old_emi": 0, "bounce": "no", "expenses": 22000, "age": 24, "score": "700-750",
                 "buffer": "1-2", "job_vintage": "<1yr", "employer": "startup", "card_util": ">70%",
                 "branch_answers": {"A-S1": "<1yr", "A-S3": ">70%"}}},
    {"id": "S2-lakshmi-near-retire", "who": "Lakshmi, 55, Chennai, salaried teacher, wants home loan near retirement.",
     "blanks": "S1 skipped.",
     "answers": {"purpose": "home", "product": "home", "wanted": 3000000,
                 "income_type": "a", "income_self": 90000, "co_income": 0, "co_active": False,
                 "old_emi": 10000, "bounce": "no", "expenses": 40000, "age": 55, "score": "750+",
                 "buffer": "3+", "job_vintage": "5yr+", "employer": "govt", "card_util": "<30%",
                 "branch_answers": {"A-S1": "5yr+"}}},
    {"id": "S3-arjun-clinic-lap", "who": "Arjun, 40, Pune, private clinic 12yr, residential flat 80L loan-free, ITR 12L/yr.",
     "blanks": "Offer skipped.",
     "answers": {"purpose": "business", "product": "lap", "wanted": 2500000,
                 "income_type": "b", "income_self": 120000, "co_income": 0, "co_active": False,
                 "itr_annual": 1200000, "old_emi": 15000, "bounce": "no", "expenses": 55000, "age": 40,
                 "score": "700-750", "buffer": "3+", "biz_vintage": "10yr+", "collateral_value": 8000000,
                 "collateral_free": True, "collateral_type": "residential", "biz_extra_income": 40000,
                 "branch_answers": {"A-B1": "10yr+", "A-B2": "12L", "A-B3": "80L"}}},
    {"id": "S4-divya-freelancer", "who": "Divya, 30, Mumbai freelancer, no collateral, unsecured business loan.",
     "blanks": "Score unknown, offer skipped, no collateral details.",
     "answers": {"purpose": "business", "product": "business", "wanted": 500000,
                 "income_type": "b", "income_self": 70000,
                 "old_emi": 5000, "bounce": "no", "expenses": 35000, "age": 30,
                 "score": "unknown", "buffer": "1-2", "itr_annual": 600000,
                 "biz_vintage": "2-10yr", "biz_extra_income": 10000,
                 "branch_answers": {"A-B1": "2-10yr"}}},
    {"id": "S5-chotu-rider-productive", "who": "Chotu, 28, Lucknow delivery rider, scooter loan with proven extra + brother backup.",
     "blanks": "Score no_history, offer skipped.",
     "answers": {"purpose": "vehicle", "product": "two_wheeler", "wanted": 140000,
                 "income_type": "c", "income_self": 30000, "co_income": 0, "co_active": False,
                 "old_emi": 2000, "bounce": "no", "expenses": 18000, "age": 28, "score": "no_history",
                 "buffer": "family", "scooter_extra_income": 12000,
                 "branch_answers": {"A-C2": "none", "A-C4": "+12k"}}},
    {"id": "S6-farah-homemaker-gold", "who": "Farah, 50, Hyderabad homemaker, no self income, husband 25k active, gold ornaments, wants 2L gold loan.",
     "blanks": "Score unknown, offer skipped.",
     "answers": {"purpose": "other", "product": "gold", "wanted": 200000,
                 "income_type": "c", "income_self": 0, "co_income": 25000, "co_active": True,
                 "co_changed": "no", "old_emi": 0, "bounce": "no", "expenses": 20000, "age": 50,
                 "score": "unknown", "buffer": "1-2", "branch_answers": {}}},
    {"id": "S7-vikram-forgetful", "who": "Vikram, 36, Delhi salaried, does not remember bounce, score unknown, wants car 8L.",
     "blanks": "Bounce unknown, score unknown, offer skipped.",
     "answers": {"purpose": "vehicle", "product": "car", "wanted": 800000,
                 "income_type": "a", "income_self": 95000, "co_income": 0, "co_active": False,
                 "old_emi": 8000, "bounce": "unknown", "expenses": 45000, "age": 36, "score": "unknown",
                 "buffer": "1-2", "job_vintage": "1-3yr", "employer": "large", "card_util": "30-70%",
                 "branch_answers": {"A-S1": "1-3yr"}}},
    {"id": "S8-joseph-age-cap", "who": "Joseph, 60, Kochi self-employed trader, age-cap tenure test, wants business 8L.",
     "blanks": "Offer skipped.",
     "answers": {"purpose": "business", "product": "business", "wanted": 800000,
                 "income_type": "b", "income_self": 80000,
                 "old_emi": 5000, "bounce": "no", "expenses": 35000, "age": 60,
                 "score": "700-750", "buffer": "1-2", "itr_annual": 720000,
                 "biz_vintage": "10yr+", "biz_extra_income": 12000,
                 "branch_answers": {"A-B1": "10yr+"}}},
]


def main() -> None:
    out_dir = pathlib.Path("docs")
    out_dir.mkdir(exist_ok=True)
    results = []
    for s in SCENARIOS:
        o = compute(s["answers"])
        results.append({"id": s["id"], "who": s["who"], "blanks": s["blanks"],
                        "answers": s["answers"], "outputs": o})
    (out_dir / "scenario_results.json").write_text(json.dumps(results, indent=1, default=str))

    lines = ["# Scenario results — batch review (engine-generated, no hand edits)",
             "", f"Engine: rules/engine.py. Tests: `python -m pytest tests/ -q`.",
             "", "## Summary",
             "", "| ID | Verdict | Ceiling | Wanted EMI | Fair band | Conf | Handling note |",
             "|----|---------|---------|------------|-----------|------|---------------|"]
    for r in results:
        o = r["outputs"]
        note = ("estimated spend" if o.get("estimated_exp") else "as answered")
        if o["confidence"]["level"] == "Low":
            note += ", wide band"
        lines.append(f"| {r['id']} | {o['verdict']['verdict']} | {o['ceiling']:,.0f} | "
                     f"{o['new_emi']:,.0f} | {o['rate']['low']}-{o['rate']['high']} | "
                     f"{o['confidence']['level']} | {note} |")
    for r in results:
        o = r["outputs"]
        lines += ["", f"## {r['id']} — {r['who']}", "", f"Blanks: {r['blanks']}", "",
                  "### Answers (questions filled on their behalf)",
                  "", "```json", json.dumps(r["answers"], indent=1, default=str), "```", "",
                  "### Outputs",
                  "", f"- O1: {o['verdict']['verdict']} — {o['verdict']['reason']}",
                  f"  Flip: {o['verdict']['flip']}",
                  f"- O2: lender {o['amount']['lender']:,.0f} / safe {o['amount']['safe']:,.0f} / use {o['amount']['use']:,.0f} (wanted {o['amount']['wanted']:,.0f})",
                  f"- O3: {o['rate']['low']}–{o['rate']['high']}% (base {o['rate']['base']}, adj {o['rate']['adj']}; {'; '.join(o['rate']['notes']) or 'no adjustments'})",
                  f"- O4: ceiling {o['ceiling']:,.0f} (FOIR cap {o['foir_cap']*100:.0f}%), EMI {o['new_emi']:,.0f}/{o['std_months']}mo, surplus {o['surplus']:,.0f}, stress {'passes' if o['stress_pass'] else 'fails'}",
                  f"- Confidence: {o['confidence']['level']} ({o['confidence']['unknowns']} unknowns)"
                  + ("; spend assumed 40%, fill actual" if o.get("estimated_exp") else ""),
                  "- Card:"] + [f"  - {l}" for l in o["card"]["lines"]]
    (out_dir / "SCENARIO_RESULTS.md").write_text("\n".join(lines) + "\n")
    print(f"wrote docs/SCENARIO_RESULTS.md + docs/scenario_results.json for {len(results)} scenarios")


if __name__ == "__main__":
    main()
