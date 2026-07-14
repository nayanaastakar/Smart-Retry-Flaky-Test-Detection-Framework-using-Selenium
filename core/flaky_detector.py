"""Flaky test detection based on execution history."""
from __future__ import annotations
from database.db_manager import fetchall, execute


def calculate_flaky_score(test_case_id: int) -> dict:
    rows = fetchall(
        """SELECT status, retry_count FROM executions 
           WHERE test_case_id=? ORDER BY started_at DESC LIMIT 10""",
        (test_case_id,)
    )
    if not rows:
        return {"score": 0.0, "verdict": "stable", "total": 0}

    total = len(rows)
    flaky_count = 0
    fail_count = 0

    for r in rows:
        status = r["status"]
        retries = r["retry_count"] or 0

        if status == "flaky":
            # Explicitly marked flaky (passed after at least 1 retry)
            flaky_count += 1
        elif status == "fail":
            fail_count += 1
        elif status == "pass" and retries > 0:
            # Passed but needed retries — this IS flaky behaviour
            flaky_count += 1

    # Score = weighted non-clean-pass ratio
    # Flaky counts half as much as a full fail (it did eventually pass)
    score = ((flaky_count * 0.7 + fail_count) / total) * 100 if total > 0 else 0

    if score == 0:
        verdict = "stable"
    elif score < 40:
        verdict = "flaky"
    else:
        verdict = "chronic"

    execute(
        """INSERT OR REPLACE INTO flaky_scores (test_case_id, score, verdict, last_calculated)
           VALUES (?,?,?,datetime('now'))""",
        (test_case_id, round(score, 1), verdict)
    )

    return {"score": round(score, 1), "verdict": verdict, "total": total}
