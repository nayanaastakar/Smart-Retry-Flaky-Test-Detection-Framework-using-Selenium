"""Seed default data."""
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


def create_test_case(project_id: int, name: str, steps: list[dict], enabled: int = 1, module: str = "General", group_name: str = "Default") -> int:
    existing = fetchone("SELECT id FROM test_cases WHERE project_id=? AND name=?", (project_id, name))
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


def create_execution(project_id: int, test_case_id: int, test_name: str, status: str, passed: int, failed: int, flaky: int, duration_seconds: float, retry_count: int, browser: str = "chrome", error_message: str | None = None, url: str | None = None) -> int:
    existing = fetchone(
        "SELECT id FROM executions WHERE project_id=? AND test_case_id=? AND test_name=? AND status=?",
        (project_id, test_case_id, test_name, status),
    )
    if existing:
        return existing["id"]
    return execute(
        "INSERT INTO executions (project_id, test_case_id, test_name, url, status, pass, fail, flaky, duration_seconds, retry_count, browser, error_message) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            project_id,
            test_case_id,
            test_name,
            url,
            status,
            passed,
            failed,
            flaky,
            duration_seconds,
            retry_count,
            browser,
            error_message,
        ),
    )


def run_all():
    init_db()

    # Admin user
    existing = fetchone("SELECT id FROM users WHERE username=?", ("admin",))
    if not existing:
        execute(
            "INSERT INTO users (username, password_hash, email, role) VALUES (?,?,?,?)",
            ("admin", hash_password("Admin@123"), "admin@smartqa.local", "admin"),
        )
        print("Created admin user (admin / Admin@123)")

    # Website profiles
    create_website_profile("SauceDemo", "https://www.saucedemo.com", "Demo e-commerce site for automation testing")
    create_website_profile("Flipkart", "https://www.flipkart.com", "Demo retail search and purchase flows")
    create_website_profile("Amazon", "https://www.amazon.com", "Demo product search and checkout flows")
    create_website_profile("Wikipedia", "https://www.wikipedia.org", "Demo documentation search flow")

    # Demo projects and test cases
    sauce_project_id = create_project("SauceDemo Demo", "https://www.saucedemo.com", "chrome", "Demo login flow")
    login_steps = [
        {"action": "open_url", "input_value": "https://www.saucedemo.com"},
        {"action": "type_text", "locator_type": "id", "locator_value": "user-name", "input_value": "standard_user"},
        {"action": "type_text", "locator_type": "id", "locator_value": "password", "input_value": "secret_sauce"},
        {"action": "click", "locator_type": "id", "locator_value": "login-button"},
        {"action": "assert_url_contains", "input_value": "inventory"},
        {"action": "screenshot"},
    ]
    sauce_test_id = create_test_case(sauce_project_id, "Login Test", login_steps, 1, "Login", "Smoke")

    flipkart_project_id = create_project("Flipkart Flaky Search", "https://www.flipkart.com", "chrome", "Flaky search test for Flipkart")
    flipkart_steps = [
        {"action": "open_url", "input_value": "https://www.flipkart.com"},
        {"action": "click", "locator_type": "css_selector", "locator_value": "button[type='submit']"},
        {"action": "type_text", "locator_type": "css_selector", "locator_value": "input[name='q']", "input_value": "laptop"},
        {"action": "press_key", "locator_type": "css_selector", "locator_value": "input[name='q']", "input_value": "ENTER"},
        {"action": "assert_url_contains", "input_value": "search"},
        {"action": "screenshot"},
    ]
    flipkart_test_id = create_test_case(flipkart_project_id, "Flipkart Search Flow", flipkart_steps, 1, "Search", "Flaky")

    amazon_project_id = create_project("Amazon Search Product", "https://www.amazon.com", "chrome", "Product search flow for Amazon")
    amazon_steps = [
        {"action": "open_url", "input_value": "https://www.amazon.com"},
        {"action": "type_text", "locator_type": "id", "locator_value": "twotabsearchtextbox", "input_value": "smartphone"},
        {"action": "click", "locator_type": "id", "locator_value": "nav-search-submit-button"},
        {"action": "assert_url_contains", "input_value": "s?k=smartphone"},
        {"action": "screenshot"},
    ]
    amazon_test_id = create_test_case(amazon_project_id, "Amazon Search Flow", amazon_steps, 1, "Search", "Flaky")

    wiki_project_id = create_project("Wiki Search Test", "https://www.wikipedia.org", "chrome", "Search flow for Wikipedia")
    wiki_steps = [
        {"action": "open_url", "input_value": "https://www.wikipedia.org"},
        {"action": "type_text", "locator_type": "id", "locator_value": "searchInput", "input_value": "Selenium"},
        {"action": "click", "locator_type": "css_selector", "locator_value": "button.pure-button"},
        {"action": "assert_url_contains", "input_value": "Selenium"},
        {"action": "screenshot"},
    ]
    wiki_test_id = create_test_case(wiki_project_id, "Wikipedia Search Test", wiki_steps, 1, "Search", "General")

    # Sample execution history
    existing_executions = fetchone("SELECT COUNT(*) as c FROM executions")["c"]
    if existing_executions == 0:
        create_execution(flipkart_project_id, flipkart_test_id, "Flipkart Flaky Search", "flaky", 0, 0, 1, 17.4, 1, "chrome", "Element not clickable on first try", "https://www.flipkart.com")
        create_execution(flipkart_project_id, flipkart_test_id, "Flipkart Flaky Search", "flaky", 0, 0, 1, 19.1, 1, "chrome", "Timeout during search", "https://www.flipkart.com")
        create_execution(amazon_project_id, amazon_test_id, "Amazon Search Product", "flaky", 0, 0, 1, 20.7, 1, "chrome", "Search results loaded slowly", "https://www.amazon.com")
        create_execution(amazon_project_id, amazon_test_id, "Amazon Search Product", "flaky", 0, 0, 1, 18.0, 1, "chrome", "Retry succeeded after network delay", "https://www.amazon.com")
        create_execution(wiki_project_id, wiki_test_id, "Wiki Search Test", "pass", 1, 0, 0, 10.3, 0, "chrome", None, "https://www.wikipedia.org")
        print("Created sample execution history")

    print("Seed complete.")


if __name__ == "__main__":
    run_all()
