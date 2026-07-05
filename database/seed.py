"""Seed default data - includes Amazon, Flipkart, Wikipedia & SauceDemo projects
with sample execution history matching the dashboard screenshot."""
from __future__ import annotations
import hashlib
import json
from database.db_manager import init_db, execute, fetchone


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def create_project(name: str, url: str, browser: str, description: str) -> int:
    existing = fetchone("SELECT id FROM projects WHERE name=?", (name,))
    if existing:
        return existing["id"]
    return execute(
        "INSERT INTO projects (name, url, browser, description) VALUES (?,?,?,?)",
        (name, url, browser, description),
    )


def create_test_case(project_id: int, name: str, steps: list[dict],
                     enabled: int = 1, module: str = "General",
                     group_name: str = "Default") -> int:
    existing = fetchone(
        "SELECT id FROM test_cases WHERE project_id=? AND name=?",
        (project_id, name)
    )
    if existing:
        return existing["id"]
    return execute(
        "INSERT INTO test_cases (project_id, name, steps_json, enabled, module, group_name) VALUES (?,?,?,?,?,?)",
        (project_id, name, json.dumps(steps), enabled, module, group_name),
    )


def create_website_profile(name: str, url: str, description: str) -> int:
    existing = fetchone("SELECT id FROM website_profiles WHERE name=?", (name,))
    if existing:
        return existing["id"]
    return execute(
        "INSERT INTO website_profiles (name, url, description) VALUES (?,?,?)",
        (name, url, description),
    )


def create_execution(project_id, test_case_id, test_name, status,
                     passed, failed, flaky, duration_seconds, retry_count,
                     browser="chrome", error_message=None, url=None,
                     started_at=None, finished_at=None, log_output=None) -> int:
    existing = fetchone(
        "SELECT id FROM executions WHERE project_id=? AND test_case_id=? AND test_name=? AND status=? AND duration_seconds=?",
        (project_id, test_case_id, test_name, status, duration_seconds),
    )
    if existing:
        return existing["id"]
    return execute(
        """INSERT INTO executions
           (project_id, test_case_id, test_name, url, status, pass, fail, flaky,
            duration_seconds, retry_count, browser, error_message, started_at, finished_at, log_output)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (project_id, test_case_id, test_name, url, status, passed, failed, flaky,
         duration_seconds, retry_count, browser, error_message,
         started_at or "2026-07-05T20:36:00",
         finished_at or "2026-07-05T20:36:30",
         log_output or ""),
    )


def run_all():
    init_db()

    # ── Admin user ─────────────────────────────────────────────────────────────
    if not fetchone("SELECT id FROM users WHERE username=?", ("admin",)):
        execute(
            "INSERT INTO users (username, password_hash, email, role) VALUES (?,?,?,?)",
            ("admin", hash_password("Admin@123"), "admin@smartqa.local", "admin"),
        )
        print("Created admin user  ->  admin / Admin@123")

    # ── Website Profiles ───────────────────────────────────────────────────────
    create_website_profile("Wikipedia",  "https://www.wikipedia.org",  "Free online encyclopedia")
    create_website_profile("Flipkart",   "https://www.flipkart.com",   "Indian e-commerce marketplace")
    create_website_profile("Amazon",     "https://www.amazon.in",      "Global e-commerce marketplace")
    create_website_profile("SauceDemo",  "https://www.saucedemo.com",  "Demo shop for automation testing")
    create_website_profile("OrangeHRM",  "https://opensource-demo.orangehrmlive.com", "HR Management demo app")
    create_website_profile("DemoQA",     "https://demoqa.com",         "QA automation practice site")

    # ══════════════════════════════════════════════════════════════════════════
    # PROJECT 1 — Wikipedia (PASS)
    # ══════════════════════════════════════════════════════════════════════════
    wiki_id = create_project(
        "Wiki Search Test",
        "https://www.wikipedia.org",
        "chrome",
        "Stable Wikipedia search flow — always passes"
    )
    wiki_steps = [
        {"action": "open_url",           "input_value": "https://en.wikipedia.org"},
        {"action": "type_text",          "locator_type": "name", "locator_value": "search", "input_value": "Artificial Intelligence", "timeout": 10},
        {"action": "press_key",          "locator_type": "name", "locator_value": "search", "input_value": "ENTER", "timeout": 10},
        {"action": "wait",               "input_value": "2"},
        {"action": "assert_title_contains", "input_value": "Artificial intelligence", "timeout": 10},
        {"action": "screenshot"},
    ]
    wiki_tc_id = create_test_case(wiki_id, "Wiki Search Test", wiki_steps, 1, "Search", "Stable")

    # ══════════════════════════════════════════════════════════════════════════
    # PROJECT 2 — Flipkart (FLAKY)
    # ══════════════════════════════════════════════════════════════════════════
    flipkart_id = create_project(
        "Flipkart Flaky Search",
        "https://www.flipkart.com",
        "chrome",
        "Flaky test — fails on attempt 1, passes on attempt 2 via JS trick"
    )
    flipkart_steps = [
        {"action": "open_url", "input_value": "https://www.flipkart.com"},
        {
            "action": "custom_js",
            "input_value": (
                "if (!localStorage.getItem('flaky_test')) {"
                "  localStorage.setItem('flaky_test', '1');"
                "  throw 'Simulating a random page load timeout!';"
                "} else {"
                "  localStorage.removeItem('flaky_test');"
                "}"
            ),
        },
        {"action": "type_text",  "locator_type": "name", "locator_value": "q", "input_value": "smartphone", "timeout": 15},
        {"action": "press_key",  "locator_type": "name", "locator_value": "q", "input_value": "ENTER", "timeout": 10},
        {"action": "wait",       "input_value": "3"},
        {"action": "screenshot"},
    ]
    flipkart_tc_id = create_test_case(flipkart_id, "Flipkart Flaky Search", flipkart_steps, 1, "Search", "Flaky")

    # ══════════════════════════════════════════════════════════════════════════
    # PROJECT 3 — Amazon (FLAKY)
    # ══════════════════════════════════════════════════════════════════════════
    amazon_id = create_project(
        "Amazon Search Product",
        "https://www.amazon.in",
        "chrome",
        "Amazon product search — may be flaky due to CAPTCHA or slow load"
    )
    amazon_steps = [
        {"action": "open_url",           "input_value": "https://www.amazon.in"},
        {"action": "wait",               "input_value": "2"},
        {"action": "assert_title_contains", "input_value": "Amazon", "timeout": 15},
        {"action": "type_text",          "locator_type": "id", "locator_value": "twotabsearchtextbox", "input_value": "iPhone 16", "timeout": 15},
        {"action": "press_key",          "locator_type": "id", "locator_value": "twotabsearchtextbox", "input_value": "ENTER", "timeout": 10},
        {"action": "wait",               "input_value": "3"},
        {"action": "screenshot"},
    ]
    amazon_tc_id = create_test_case(amazon_id, "Amazon Search Product", amazon_steps, 1, "Search", "Flaky")

    # ══════════════════════════════════════════════════════════════════════════
    # PROJECT 4 — SauceDemo (PASS)
    # ══════════════════════════════════════════════════════════════════════════
    sauce_id = create_project(
        "SauceDemo Login Flow",
        "https://www.saucedemo.com",
        "chrome",
        "Full login and product listing verification"
    )
    sauce_steps = [
        {"action": "open_url",           "input_value": "https://www.saucedemo.com"},
        {"action": "type_text",          "locator_type": "id", "locator_value": "user-name",    "input_value": "standard_user",  "timeout": 10},
        {"action": "type_text",          "locator_type": "id", "locator_value": "password",     "input_value": "secret_sauce",   "timeout": 10},
        {"action": "click",              "locator_type": "id", "locator_value": "login-button",                                  "timeout": 10},
        {"action": "assert_url_contains","input_value": "inventory",                                                              "timeout": 10},
        {"action": "screenshot"},
    ]
    sauce_tc_id = create_test_case(sauce_id, "SauceDemo Login Test", sauce_steps, 1, "Login", "Smoke")

    # ══════════════════════════════════════════════════════════════════════════
    # PROJECT 5 — OrangeHRM (PASS)
    # ══════════════════════════════════════════════════════════════════════════
    hrm_id = create_project(
        "OrangeHRM Login",
        "https://opensource-demo.orangehrmlive.com",
        "chrome",
        "HR portal login verification"
    )
    hrm_steps = [
        {"action": "open_url",  "input_value": "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"},
        {"action": "type_text", "locator_type": "name", "locator_value": "username", "input_value": "Admin", "timeout": 15},
        {"action": "type_text", "locator_type": "name", "locator_value": "password", "input_value": "admin123", "timeout": 10},
        {"action": "click",     "locator_type": "css",  "locator_value": "button[type='submit']", "timeout": 10},
        {"action": "assert_url_contains", "input_value": "dashboard", "timeout": 15},
        {"action": "screenshot"},
    ]
    hrm_tc_id = create_test_case(hrm_id, "OrangeHRM Login Test", hrm_steps, 1, "Login", "Smoke")

    # ══════════════════════════════════════════════════════════════════════════
    # Sample Execution History (matches dashboard screenshot)
    # ══════════════════════════════════════════════════════════════════════════
    if fetchone("SELECT COUNT(*) as c FROM executions")["c"] == 0:
        # Flipkart — 2 flaky runs
        create_execution(flipkart_id, flipkart_tc_id, "Flipkart Flaky Search", "flaky", 0, 0, 1, 17.4, 1, "chrome",
                         "Simulating a random page load timeout!", "https://www.flipkart.com",
                         "2026-07-05T20:50:00", "2026-07-05T20:50:17",
                         "[Attempt 1] Browser started (chrome)\n  Step 01 [open_url]: Opened https://www.flipkart.com\n  Step 02 [custom_js]: EXCEPTION: Simulating a random page load timeout!\n  ✗ Failed at step 2\n  ↺ Retry in 1.0s …\n[Attempt 2] Reusing existing browser\n  Step 01 [open_url]: Opened https://www.flipkart.com\n  Step 02 [custom_js]: JS executed: None\n  Step 03 [type_text]: Typed into q\n  Step 04 [press_key]: Pressed ENTER\n  Step 05 [wait]: Waited 3.0s\n  📷 Final screenshot: /evidence/...")

        create_execution(flipkart_id, flipkart_tc_id, "Flipkart Flaky Search", "flaky", 0, 0, 1, 19.1, 1, "chrome",
                         "Timeout during popup close", "https://www.flipkart.com",
                         "2026-07-05T20:50:30", "2026-07-05T20:50:49",
                         "[Attempt 1] Browser started (chrome)\n  ✗ Failed at step 2: Simulating a random page load timeout!\n  ↺ Retry in 1.0s …\n[Attempt 2] Reusing existing browser\n  All steps passed.\n  📷 Final screenshot")

        # Amazon — 2 flaky runs
        create_execution(amazon_id, amazon_tc_id, "Amazon Search Product", "flaky", 0, 0, 1, 20.7, 1, "chrome",
                         "Search results loaded slowly - retry succeeded", "https://www.amazon.in",
                         "2026-07-05T20:42:00", "2026-07-05T20:42:20",
                         "[Attempt 1] Browser started (chrome)\n  ✗ Failed at step 3: Title 'Sorry!' doesn't contain 'Amazon'\n  ↺ Retry in 1.0s …\n[Attempt 2] Reusing existing browser\n  All steps passed.")

        create_execution(amazon_id, amazon_tc_id, "Amazon Search Product", "flaky", 0, 0, 1, 18.0, 1, "chrome",
                         "Network delay on first attempt", "https://www.amazon.in",
                         "2026-07-05T20:39:00", "2026-07-05T20:39:18",
                         "[Attempt 1] Network slow — retry triggered\n[Attempt 2] All steps passed.")

        # Wikipedia — 1 pass
        create_execution(wiki_id, wiki_tc_id, "Wiki Search Test", "pass", 1, 0, 0, 10.3, 0, "chrome",
                         None, "https://en.wikipedia.org",
                         "2026-07-05T20:36:00", "2026-07-05T20:36:10",
                         "[Attempt 1] Browser started (chrome)\n  All steps passed.\n  📷 Final screenshot")

        # SauceDemo — 1 pass
        create_execution(sauce_id, sauce_tc_id, "SauceDemo Login Test", "pass", 1, 0, 0, 8.5, 0, "chrome",
                         None, "https://www.saucedemo.com",
                         "2026-07-05T20:30:00", "2026-07-05T20:30:08",
                         "[Attempt 1] Browser started (chrome)\n  All steps passed.\n  📷 Final screenshot")

        # OrangeHRM — 1 pass
        create_execution(hrm_id, hrm_tc_id, "OrangeHRM Login Test", "pass", 1, 0, 0, 12.1, 0, "chrome",
                         None, "https://opensource-demo.orangehrmlive.com",
                         "2026-07-05T20:28:00", "2026-07-05T20:28:12",
                         "[Attempt 1] Browser started (chrome)\n  All steps passed.\n  📷 Final screenshot")

        # A couple of failures
        create_execution(amazon_id, amazon_tc_id, "Amazon Search Product", "fail", 0, 1, 0, 45.0, 3, "chrome",
                         "Message: invalid argument (Session info: chrome=149.0) StackTrace: chromedriver!GetHandleVerifier",
                         "https://www.amazon.in",
                         "2026-07-05T20:24:00", "2026-07-05T20:24:45",
                         "[Attempt 1] EXCEPTION: invalid argument\n[Attempt 2] EXCEPTION: invalid argument\n[Attempt 3] EXCEPTION: invalid argument")

        create_execution(flipkart_id, flipkart_tc_id, "Flipkart Flaky Search", "fail", 0, 1, 0, 35.2, 3, "chrome",
                         "WebDriverException: Chrome not reachable",
                         "https://www.flipkart.com",
                         "2026-07-05T20:20:00", "2026-07-05T20:20:35",
                         "[Attempt 1] EXCEPTION: WebDriverException\n[Attempt 2] EXCEPTION: WebDriverException\n[Attempt 3] EXCEPTION: WebDriverException")

        print("Created sample execution history")

    print("\n[OK] Seed complete!")
    print("   Login: admin / Admin@123")
    print("   Projects: Wiki, Flipkart, Amazon, SauceDemo, OrangeHRM")
    print("   Execution history: 9 runs seeded")


if __name__ == "__main__":
    run_all()
