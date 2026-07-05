import time
import json
from database.db_manager import execute
from core.project_runner import run_single_test_case

import logging
logging.basicConfig(level=logging.INFO)

def run_validation():
    # Create project
    project_name = f"SauceDemo-{int(time.time())}"
    project_id = execute("INSERT INTO projects (name, url, browser) VALUES (?, ?, ?)", (project_name, "https://www.saucedemo.com", "chrome"))

    steps = [
        {"action": "open_url", "input_value": "https://www.saucedemo.com"},
        {"action": "type_text", "locator_type": "id", "locator_value": "user-name", "input_value": "standard_user"},
        {"action": "type_text", "locator_type": "id", "locator_value": "password", "input_value": "secret_sauce"},
        {"action": "click", "locator_type": "id", "locator_value": "login-button"},
        {"action": "assert_url_contains", "input_value": "inventory"},
        {"action": "screenshot"}
    ]
    
    test_id = execute("INSERT INTO test_cases (project_id, name, steps_json, enabled, module, group_name) VALUES (?, ?, ?, ?, ?, ?)", 
                      (project_id, "Login Test", json.dumps(steps), 1, "Login", "General"))
    
    print(f"Running test case {test_id}...")
    start = time.time()
    
    result = run_single_test_case(test_id)
    
    duration = time.time() - start
    print(f"Test completed in {duration:.2f} seconds")
    print(f"Result: {result}")
    
    if duration > 10:
        print(f"WARNING: Execution took {duration:.2f}s, which is > 10s. We'll still check pass status.")
    
    assert result["pass"] == 1, "Test failed!"
    print("Validation passed!")

if __name__ == "__main__":
    run_validation()
