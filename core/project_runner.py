"""Project runner: runs test cases through SmartRetryEngine."""
from __future__ import annotations
import json
import logging
import os
import time
import traceback
from datetime import datetime
from pathlib import Path

from config import settings
from database.db_manager import execute, fetchone, fetchall

log = logging.getLogger(__name__)


def _take_screenshot(driver, execution_id: int, step_num: int, attempt: int) -> str | None:
    try:
        # Small delay to ensure the browser has actually rendered the current frame
        # (prevents completely blank/white images if taken instantly during a page transition)
        time.sleep(0.5)
        
        ts = int(time.time())
        fname = f"exec_{execution_id}_step{step_num}_attempt{attempt}_{ts}.png"
        path = settings.EVIDENCE_DIR / fname
        path.parent.mkdir(parents=True, exist_ok=True)
        driver.save_screenshot(str(path))
        return str(path)
    except Exception as e:
        log.warning("Screenshot failed: %s", e)
        return None


def run_single_test_case(test_case_id: int) -> dict:
    """Run a single test case with smart retry. Returns result dict."""
    row = fetchone("SELECT * FROM test_cases WHERE id=?", (test_case_id,))
    if not row:
        return {"pass": 0, "error": "Test case not found"}

    test_name = row["name"]
    steps = json.loads(row["steps_json"] or "[]")
    browser = "chrome"
    
    # Get project browser
    if row["project_id"]:
        proj = fetchone("SELECT browser, url FROM projects WHERE id=?", (row["project_id"],))
        if proj:
            browser = proj["browser"]

    # Create execution record
    exec_id = execute(
        """INSERT INTO executions (project_id, test_case_id, test_name, status, browser, started_at)
           VALUES (?,?,?,?,?,?)""",
        (row["project_id"], test_case_id, test_name, "running", browser, datetime.utcnow().isoformat())
    )

    from core.step_executor import execute_step

    last_error = None
    passed = False
    screenshot_path = None
    logs = []
    attempt = 0

    driver = None
    try:
        from core.driver_factory import create_driver
        driver = create_driver(browser)
        # Speed up: limit page load and script timeouts
        driver.set_page_load_timeout(30)
        driver.set_script_timeout(15)

        for attempt in range(settings.MAX_RETRIES + 1):
            try:
                logs.append(f"[Attempt {attempt+1}] " + ("Browser launched" if attempt == 0 else "Reusing existing browser"))
                
                step_results = []
                all_passed = True

                for i, step in enumerate(steps):
                    action = step.get("action", "")
                    result = execute_step(driver, step)
                    logs.append(f"  Step {i+1} [{action}]: {result['message']}")

                    # Take screenshot only if requested
                    if result.get("take_screenshot"):
                        sc = _take_screenshot(driver, exec_id, i+1, attempt+1)
                        if sc:
                            screenshot_path = sc

                    if not result["success"]:
                        # Capture where it went wrong
                        sc = _take_screenshot(driver, exec_id, i+1, attempt+1)
                        if sc:
                            screenshot_path = sc
                        all_passed = False
                        last_error = result["message"]
                        break

                if all_passed:
                    passed = True
                    logs.append(f"[Attempt {attempt+1}] PASSED")
                    break
                else:
                    logs.append(f"[Attempt {attempt+1}] FAILED: {last_error}")

            except Exception as e:
                last_error = str(e)
                # Capture exception screenshot
                sc = _take_screenshot(driver, exec_id, len(steps), attempt+1)
                if sc:
                    screenshot_path = sc
                logs.append(f"[Attempt {attempt+1}] EXCEPTION: {last_error}")
                log.exception("Attempt %d failed for test %s", attempt+1, test_name)
                
            # Save retry record
            execute(
                """INSERT INTO retries (execution_id, attempt_number, status, error_message)
                   VALUES (?,?,?,?)""",
                (exec_id, attempt+1, "pass" if passed else "fail", last_error)
            )

            if passed:
                break

            if attempt < settings.MAX_RETRIES:
                delay = settings.RETRY_DELAY_SECONDS * (settings.RETRY_BACKOFF_MULTIPLIER ** attempt)
                time.sleep(delay)

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

    # Determine flaky: passed on retry (not first attempt)
    flaky = passed and attempt > 0
    status = "pass" if passed else "fail"
    if flaky:
        status = "flaky"

    # (We no longer delete screenshots on pass so that explicit 'Take Screenshot' steps are preserved)


    log_output = "\n".join(logs)

    # Update execution
    execute(
        """UPDATE executions SET status=?, pass=?, fail=?, flaky=?, retry_count=?,
           error_message=?, screenshot_path=?, log_output=?, finished_at=?
           WHERE id=?""",
        (
            status, 1 if passed else 0, 0 if passed else 1, 1 if flaky else 0,
            attempt, last_error, screenshot_path, log_output,
            datetime.utcnow().isoformat(), exec_id
        )
    )

    try:
        from core.flaky_detector import calculate_flaky_score
        calculate_flaky_score(test_case_id)
    except Exception as e:
        log.warning("Failed to calculate flaky score: %s", e)



    return {
        "pass": 1 if passed else 0,
        "flaky": 1 if flaky else 0,
        "status": status,
        "retries": attempt,
        "execution_id": exec_id,
        "screenshot_path": screenshot_path,
        "error": last_error,
        "logs": log_output,
    }


def run_project(project_id: int) -> dict:
    """Run all enabled test cases for a project."""
    test_cases = fetchall(
        "SELECT id FROM test_cases WHERE project_id=? AND enabled=1 ORDER BY id",
        (project_id,)
    )
    if not test_cases:
        return {"error": "No enabled test cases", "results": []}

    results = []
    for tc in test_cases:
        result = run_single_test_case(tc["id"])
        results.append(result)

    total = len(results)
    passed = sum(1 for r in results if r.get("pass"))
    failed = total - passed

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "results": results,
    }
