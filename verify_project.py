"""verify_project.py - Automated project self-testing script for PASS, FAIL, FLAKY cases and AI analysis."""
from __future__ import annotations
import json
import os
import sqlite3
import sys
import time
from database.db_manager import execute, fetchone, fetchall
from core.project_runner import run_single_test_case

# Clear existing test runs to avoid confusion
print("Clearing historical Sandbox runs...")
execute("DELETE FROM executions WHERE test_name LIKE 'Local Sandbox%'")
execute("DELETE FROM test_cases WHERE name LIKE 'Local Sandbox%'")
execute("DELETE FROM projects WHERE name='Sandbox Test Project'")

# 1. Create a new project pointing to our local sandbox website
print("Creating Sandbox Test Project...")
project_id = execute(
    "INSERT INTO projects (name, url, browser, description) VALUES (?, ?, ?, ?)",
    ("Sandbox Test Project", "http://localhost:8080/static/test_site.html", "chrome", "Fast automated testing sandbox")
)

# 2. Insert PASS, FAIL, FLAKY test cases
print("Inserting test cases...")

# PASS Test Case: uses Wait step to ensure success on Attempt 1
pass_steps = [
    {"action": "open_url", "input_value": "http://localhost:8080/static/test_site.html", "timeout": 10},
    {"action": "type_text", "locator_type": "id", "locator_value": "search-input", "input_value": "SandboxPass", "timeout": 10},
    {"action": "click", "locator_type": "id", "locator_value": "search-btn", "timeout": 10},
    {"action": "wait", "input_value": "1.8", "timeout": 10},
    {"action": "assert_text", "input_value": "Results for SandboxPass", "timeout": 10},
    {"action": "screenshot", "timeout": 10}
]
pass_id = execute(
    "INSERT INTO test_cases (project_id, name, steps_json, enabled) VALUES (?, ?, ?, 1)",
    (project_id, "Local Sandbox PASS Test", json.dumps(pass_steps))
)

# FAIL Test Case: asserts text that doesn't exist (permanently fails)
fail_steps = [
    {"action": "open_url", "input_value": "http://localhost:8080/static/test_site.html", "timeout": 10},
    {"action": "type_text", "locator_type": "id", "locator_value": "search-input", "input_value": "SandboxFail", "timeout": 10},
    {"action": "click", "locator_type": "id", "locator_value": "search-btn", "timeout": 10},
    {"action": "assert_text", "input_value": "NonExistentText", "timeout": 10},
    {"action": "screenshot", "timeout": 10}
]
fail_id = execute(
    "INSERT INTO test_cases (project_id, name, steps_json, enabled) VALUES (?, ?, ?, 1)",
    (project_id, "Local Sandbox FAIL Test", json.dumps(fail_steps))
)

# FLAKY Test Case: asserts immediately without Wait (Attempt 1 fails, Attempt 2 passes)
flaky_steps = [
    {"action": "open_url", "input_value": "http://localhost:8080/static/test_site.html", "timeout": 10},
    {"action": "type_text", "locator_type": "id", "locator_value": "search-input", "input_value": "SandboxFlaky", "timeout": 10},
    {"action": "click", "locator_type": "id", "locator_value": "search-btn", "timeout": 10},
    {"action": "assert_text", "input_value": "Results for SandboxFlaky", "timeout": 10},
    {"action": "screenshot", "timeout": 10}
]
flaky_id = execute(
    "INSERT INTO test_cases (project_id, name, steps_json, enabled) VALUES (?, ?, ?, 1)",
    (project_id, "Local Sandbox FLAKY Test", json.dumps(flaky_steps))
)

# 3. Execute the tests
print("\n=== RUNNING PASS TEST CASE ===")
t0 = time.time()
pass_res = run_single_test_case(pass_id)
print(f"PASS Test finished in {time.time() - t0:.2f}s. Status: {pass_res['status']}, Retries: {pass_res['retries']}")

print("\n=== RUNNING FAIL TEST CASE ===")
t0 = time.time()
fail_res = run_single_test_case(fail_id)
print(f"FAIL Test finished in {time.time() - t0:.2f}s. Status: {fail_res['status']}, Retries: {fail_res['retries']}")

print("\n=== RUNNING FLAKY TEST CASE ===")
t0 = time.time()
flaky_res = run_single_test_case(flaky_id)
print(f"FLAKY Test finished in {time.time() - t0:.2f}s. Status: {flaky_res['status']}, Retries: {flaky_res['retries']}")

# 4. Perform AI Analysis on Fail & Flaky executions
print("\n=== PERFORMING AI ANALYSIS ===")
from app import app
from flask import session
from routes.ai_analysis_routes import analyze

with app.test_request_context():
    session["user_id"] = 1  # Bypass login_required
    
    if fail_res.get("execution_id"):
        print(f"Analyzing FAIL Execution ID {fail_res['execution_id']}...")
        try:
            analyze(fail_res["execution_id"])
        except Exception as ex:
            print(f"FAIL Analysis Error: {ex}")
        
    if flaky_res.get("execution_id"):
        print(f"Analyzing FLAKY Execution ID {flaky_res['execution_id']}...")
        try:
            analyze(flaky_res["execution_id"])
        except Exception as ex:
            print(f"FLAKY Analysis Error: {ex}")

# 5. Output Verification Results
print("\n=== VERIFICATION RESULTS ===")
executions = fetchall(
    """SELECT id, test_name, status, retry_count, screenshot_path 
       FROM executions WHERE test_case_id IN (?, ?, ?) ORDER BY id""",
    (pass_id, fail_id, flaky_id)
)

for e in executions:
    print(f"\nTest: {e['test_name']}")
    print(f"  Status: {e['status']}")
    print(f"  Retries: {e['retry_count']}")
    print(f"  Screenshot Generated: {e['screenshot_path'] is not None} ({os.path.basename(e['screenshot_path']) if e['screenshot_path'] else 'None'})")
    
    # Check AI analysis
    ai = fetchone("SELECT * FROM ai_analysis WHERE execution_id=?", (e["id"],))
    if ai:
        print(f"  AI Root Cause: {ai['root_cause']}")
        print(f"  AI Suggested Fix: {ai['suggested_fix']}")
        print(f"  AI Confidence Score: {ai['confidence_score']}%")
    else:
        print("  AI Analysis: None (Passed tests do not require analysis)")

print("\nVerification complete!")
