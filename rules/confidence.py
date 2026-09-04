"""High/Med/Low + widen rules. Unknown never zero."""


def confidence(answers: dict, extra_unknowns: int = 0) -> dict:
    unknowns = int(extra_unknowns or 0)
    score = str(answers.get("score", "unknown")).lower()
    if score in ("unknown", "dontknow", "don't know", "no_history", "no history", ""):
        unknowns += 1
    if str(answers.get("bounce", "no")).lower() in ("unknown", "dontremember", "don't remember"):
        unknowns += 1
    if not answers.get("income_self"):
        unknowns += 1
    branch = str(answers.get("income_type", "a")).lower()
    filled = 0
    for k in (answers.get("branch_answers", {}) or {}):
        if answers["branch_answers"][k] not in (None, "", "unknown", "skip"):
            filled += 1
    if branch in ("b", "self", "self-employed", "business") and filled < 2:
        unknowns += 1
    if branch in ("c", "informal") and filled < 2:
        unknowns += 1
    level = "High" if unknowns == 0 else ("Medium" if unknowns <= 2 else "Low")
    return {"level": level, "unknowns": unknowns}
