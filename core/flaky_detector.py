"""Flaky test detection based on execution history."""
from __future__ import annotations
from database.db_manager import fetchall, execute


def calculate_flaky_score(test_case_id: int) -> dict:
    rows = fetchall(
        """SELECT status FROM executions 
           WHERE test_case_id=? ORDER BY started_at DESC LIMIT 10""",
        (test_case_id,)
    )
    if not rows:
        return {"score": 0.0, "verdict": "stable", "total": 0}

    statuses = [r["status"] for r in rows]
    total = len(statuses)
    flips = sum(1 for s in statuses if s in ("flaky",))
    fails = sum(1 for s in statuses if s == "fail")

    # Score = % of non-passing runs
    score = ((flips + fails) / total) * 100 if total > 0 else 0

    if score == 0:
        verdict = "stable"
    elif score < 30:
        verdict = "flaky"
    else:
        verdict = "chronic"

    execute(
        """INSERT OR REPLACE INTO flaky_scores (test_case_id, score, verdict, last_calculated)
           VALUES (?,?,?,datetime('now'))""",
        (test_case_id, score, verdict)
    )

    return {"score": round(score, 1), "verdict": verdict, "total": total}
