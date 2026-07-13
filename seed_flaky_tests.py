"""
seed_flaky_tests.py — Seeds 10 realistic flaky test cases into SmartRetry.
Run: .venv\Scripts\python.exe seed_flaky_tests.py
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from database.db_manager import fetchone, execute

# ── 1. Ensure a "Flaky Demo" project exists ──────────────────
existing = fetchone("SELECT id FROM projects WHERE name=?", ("Flaky Demo Suite",))
if existing:
    project_id = existing["id"]
    print(f"Reusing existing project id={project_id}")
else:
    project_id = execute(
        "INSERT INTO projects (name, url, browser, description) VALUES (?,?,?,?)",
        ("Flaky Demo Suite", "https://www.saucedemo.com", "chrome",
         "10 realistic flaky test cases demonstrating common instability patterns")
    )
    print(f"Created project id={project_id}")

# ── 2. Define 10 test cases ──────────────────────────────────
TEST_CASES = [
    # ── TC-1: Login with valid credentials ─────────────────────
    {
        "name": "TC-01: Standard Login — Valid Credentials",
        "module": "Authentication",
        "steps": [
            {"action": "open_url",          "input_value": "https://www.saucedemo.com", "timeout": 10},
            {"action": "wait",              "input_value": "1", "timeout": 5},
            {"action": "type_text",         "locator_type": "id", "locator_value": "user-name",  "input_value": "standard_user",  "timeout": 10},
            {"action": "type_text",         "locator_type": "id", "locator_value": "password",   "input_value": "secret_sauce",    "timeout": 10},
            {"action": "click",             "locator_type": "id", "locator_value": "login-button", "timeout": 10},
            {"action": "wait",              "input_value": "2", "timeout": 5},
            {"action": "assert_url_contains","input_value": "inventory",  "timeout": 10},
            {"action": "screenshot",        "timeout": 5},
        ]
    },

    # ── TC-2: Login with wrong password (should fail assertion) ─
    {
        "name": "TC-02: Login — Invalid Password (Validation Test)",
        "module": "Authentication",
        "steps": [
            {"action": "open_url",    "input_value": "https://www.saucedemo.com", "timeout": 10},
            {"action": "type_text",   "locator_type": "id", "locator_value": "user-name", "input_value": "standard_user",   "timeout": 10},
            {"action": "type_text",   "locator_type": "id", "locator_value": "password",  "input_value": "wrong_password",  "timeout": 10},
            {"action": "click",       "locator_type": "id", "locator_value": "login-button", "timeout": 10},
            {"action": "assert_text", "input_value": "Epic sadface: Username and password do not match", "timeout": 10},
            {"action": "screenshot",  "timeout": 5},
        ]
    },

    # ── TC-3: Product listing loads ─────────────────────────────
    {
        "name": "TC-03: Product Inventory — Page Load & Count",
        "module": "E-Commerce",
        "steps": [
            {"action": "open_url",               "input_value": "https://www.saucedemo.com", "timeout": 10},
            {"action": "type_text",              "locator_type": "id", "locator_value": "user-name", "input_value": "standard_user", "timeout": 10},
            {"action": "type_text",              "locator_type": "id", "locator_value": "password",  "input_value": "secret_sauce",  "timeout": 10},
            {"action": "click",                  "locator_type": "id", "locator_value": "login-button", "timeout": 10},
            {"action": "wait",                   "input_value": "2", "timeout": 5},
            {"action": "assert_element_visible", "locator_type": "class", "locator_value": "inventory_list", "timeout": 15},
            {"action": "assert_text",            "input_value": "Sauce Labs Backpack", "timeout": 10},
            {"action": "screenshot",             "timeout": 5},
        ]
    },

    # ── TC-4: Add to Cart ───────────────────────────────────────
    {
        "name": "TC-04: Add Product to Cart",
        "module": "E-Commerce",
        "steps": [
            {"action": "open_url",  "input_value": "https://www.saucedemo.com", "timeout": 10},
            {"action": "type_text", "locator_type": "id", "locator_value": "user-name", "input_value": "standard_user", "timeout": 10},
            {"action": "type_text", "locator_type": "id", "locator_value": "password",  "input_value": "secret_sauce",  "timeout": 10},
            {"action": "click",     "locator_type": "id", "locator_value": "login-button",                              "timeout": 10},
            {"action": "wait",      "input_value": "2",                                                                  "timeout": 5},
            {"action": "click",     "locator_type": "id", "locator_value": "add-to-cart-sauce-labs-backpack",            "timeout": 10},
            {"action": "assert_element_visible", "locator_type": "class", "locator_value": "shopping_cart_badge",       "timeout": 10},
            {"action": "assert_text", "input_value": "1",                                                                "timeout": 5},
            {"action": "screenshot",                                                                                     "timeout": 5},
        ]
    },

    # ── TC-5: Sort products ─────────────────────────────────────
    {
        "name": "TC-05: Sort Products — Price Low to High",
        "module": "E-Commerce",
        "steps": [
            {"action": "open_url",          "input_value": "https://www.saucedemo.com", "timeout": 10},
            {"action": "type_text",         "locator_type": "id", "locator_value": "user-name", "input_value": "standard_user", "timeout": 10},
            {"action": "type_text",         "locator_type": "id", "locator_value": "password",  "input_value": "secret_sauce",  "timeout": 10},
            {"action": "click",             "locator_type": "id", "locator_value": "login-button",                              "timeout": 10},
            {"action": "wait",              "input_value": "2",                                                                  "timeout": 5},
            {"action": "select_dropdown",   "locator_type": "class", "locator_value": "product_sort_container", "input_value": "lohi", "timeout": 10},
            {"action": "wait",              "input_value": "1",                                                                  "timeout": 5},
            {"action": "assert_text",       "input_value": "Sauce Labs Onesie",                                                  "timeout": 10},
            {"action": "screenshot",                                                                                              "timeout": 5},
        ]
    },

    # ── TC-6: Open product detail ───────────────────────────────
    {
        "name": "TC-06: Product Detail Page Navigation",
        "module": "E-Commerce",
        "steps": [
            {"action": "open_url",               "input_value": "https://www.saucedemo.com", "timeout": 10},
            {"action": "type_text",              "locator_type": "id", "locator_value": "user-name", "input_value": "standard_user", "timeout": 10},
            {"action": "type_text",              "locator_type": "id", "locator_value": "password",  "input_value": "secret_sauce",  "timeout": 10},
            {"action": "click",                  "locator_type": "id", "locator_value": "login-button",                              "timeout": 10},
            {"action": "wait",                   "input_value": "2",                                                                  "timeout": 5},
            {"action": "click",                  "locator_type": "id", "locator_value": "item_4_title_link",                          "timeout": 10},
            {"action": "wait",                   "input_value": "1",                                                                  "timeout": 5},
            {"action": "assert_url_contains",    "input_value": "inventory-item",                                                     "timeout": 10},
            {"action": "assert_text",            "input_value": "Sauce Labs Backpack",                                                "timeout": 10},
            {"action": "screenshot",                                                                                                   "timeout": 5},
        ]
    },

    # ── TC-7: Cart → Checkout flow ──────────────────────────────
    {
        "name": "TC-07: Checkout Flow — Step 1 Form",
        "module": "Checkout",
        "steps": [
            {"action": "open_url",  "input_value": "https://www.saucedemo.com",                              "timeout": 10},
            {"action": "type_text", "locator_type": "id", "locator_value": "user-name", "input_value": "standard_user", "timeout": 10},
            {"action": "type_text", "locator_type": "id", "locator_value": "password",  "input_value": "secret_sauce",  "timeout": 10},
            {"action": "click",     "locator_type": "id", "locator_value": "login-button",                               "timeout": 10},
            {"action": "wait",      "input_value": "2",                                                                   "timeout": 5},
            {"action": "click",     "locator_type": "id", "locator_value": "add-to-cart-sauce-labs-backpack",             "timeout": 10},
            {"action": "click",     "locator_type": "class", "locator_value": "shopping_cart_link",                       "timeout": 10},
            {"action": "click",     "locator_type": "id", "locator_value": "checkout",                                    "timeout": 10},
            {"action": "type_text", "locator_type": "id", "locator_value": "first-name", "input_value": "John",           "timeout": 10},
            {"action": "type_text", "locator_type": "id", "locator_value": "last-name",  "input_value": "Doe",            "timeout": 10},
            {"action": "type_text", "locator_type": "id", "locator_value": "postal-code","input_value": "560001",         "timeout": 10},
            {"action": "click",     "locator_type": "id", "locator_value": "continue",                                    "timeout": 10},
            {"action": "assert_url_contains", "input_value": "checkout-step-two",                                         "timeout": 10},
            {"action": "screenshot",                                                                                       "timeout": 5},
        ]
    },

    # ── TC-8: Locked-out user error ─────────────────────────────
    {
        "name": "TC-08: Locked User — Access Denied Message",
        "module": "Authentication",
        "steps": [
            {"action": "open_url",    "input_value": "https://www.saucedemo.com", "timeout": 10},
            {"action": "type_text",   "locator_type": "id", "locator_value": "user-name", "input_value": "locked_out_user", "timeout": 10},
            {"action": "type_text",   "locator_type": "id", "locator_value": "password",  "input_value": "secret_sauce",    "timeout": 10},
            {"action": "click",       "locator_type": "id", "locator_value": "login-button",                                "timeout": 10},
            {"action": "assert_text", "input_value": "Sorry, this user has been locked out",                                "timeout": 10},
            {"action": "screenshot",  "timeout": 5},
        ]
    },

    # ── TC-9: Logout flow ───────────────────────────────────────
    {
        "name": "TC-09: Logout and Redirect to Login",
        "module": "Authentication",
        "steps": [
            {"action": "open_url",  "input_value": "https://www.saucedemo.com", "timeout": 10},
            {"action": "type_text", "locator_type": "id", "locator_value": "user-name", "input_value": "standard_user", "timeout": 10},
            {"action": "type_text", "locator_type": "id", "locator_value": "password",  "input_value": "secret_sauce",  "timeout": 10},
            {"action": "click",     "locator_type": "id", "locator_value": "login-button",                              "timeout": 10},
            {"action": "wait",      "input_value": "2",                                                                  "timeout": 5},
            {"action": "click",     "locator_type": "id", "locator_value": "react-burger-menu-btn",                      "timeout": 10},
            {"action": "wait",      "input_value": "1",                                                                  "timeout": 5},
            {"action": "click",     "locator_type": "id", "locator_value": "logout_sidebar_link",                        "timeout": 10},
            {"action": "assert_url_contains", "input_value": "saucedemo.com",                                            "timeout": 10},
            {"action": "assert_element_visible", "locator_type": "id", "locator_value": "login-button",                  "timeout": 10},
            {"action": "screenshot",                                                                                      "timeout": 5},
        ]
    },

    # ── TC-10: Wikipedia search (flaky due to network) ──────────
    {
        "name": "TC-10: Wikipedia — Search & Verify Result",
        "module": "Navigation",
        "steps": [
            {"action": "open_url",            "input_value": "https://en.wikipedia.org/wiki/Main_Page", "timeout": 15},
            {"action": "wait",                "input_value": "2",                                        "timeout": 5},
            {"action": "assert_title_contains","input_value": "Wikipedia",                               "timeout": 10},
            {"action": "type_text",           "locator_type": "id", "locator_value": "searchInput", "input_value": "Selenium (software)", "timeout": 10},
            {"action": "press_key",           "locator_type": "id", "locator_value": "searchInput", "input_value": "ENTER", "timeout": 10},
            {"action": "wait",                "input_value": "3",                                        "timeout": 10},
            {"action": "assert_url_contains", "input_value": "Selenium",                                 "timeout": 15},
            {"action": "assert_text",         "input_value": "automated testing",                        "timeout": 10},
            {"action": "screenshot",                                                                      "timeout": 5},
        ]
    },
]

# ── 3. Insert test cases ─────────────────────────────────────
inserted = 0
skipped  = 0
for tc in TEST_CASES:
    existing_tc = fetchone(
        "SELECT id FROM test_cases WHERE project_id=? AND name=?",
        (project_id, tc["name"])
    )
    if existing_tc:
        print(f"  SKIP (already exists): {tc['name']}")
        skipped += 1
        continue

    execute(
        "INSERT INTO test_cases (project_id, name, steps_json, enabled, module) VALUES (?,?,?,1,?)",
        (project_id, tc["name"], json.dumps(tc["steps"]), tc.get("module", "General"))
    )
    print(f"  OK Inserted: {tc['name']}")
    inserted += 1

print(f"\n" + "-"*55)
print(f"Done! {inserted} inserted, {skipped} skipped.")
print(f"Open http://localhost:8080/projects/{project_id} to run them.")
