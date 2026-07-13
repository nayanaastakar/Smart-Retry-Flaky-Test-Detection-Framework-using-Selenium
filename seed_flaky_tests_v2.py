"""
seed_flaky_tests_v2.py - 10 flaky test cases on 10 DIFFERENT websites.
Run: .venv\Scripts\python.exe seed_flaky_tests_v2.py
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from database.db_manager import fetchone, execute

# ── 1. Delete old project if exists, then recreate ──────────
old = fetchone("SELECT id FROM projects WHERE name=?", ("Flaky Demo Suite",))
if old:
    execute("DELETE FROM test_cases WHERE project_id=?", (old["id"],))
    execute("DELETE FROM projects WHERE id=?", (old["id"],))
    print("Removed old Flaky Demo Suite.")

project_id = execute(
    "INSERT INTO projects (name, url, browser, description) VALUES (?,?,?,?)",
    ("Flaky Demo Suite",
     "https://the-internet.herokuapp.com",
     "chrome",
     "10 flaky test cases on 10 different real public websites")
)
print(f"Created project id={project_id}")

# ──────────────────────────────────────────────────────────────────────
# SENTENCE USED:  (what you would type in AI Generator)
# TARGET SITE:    (different for each test case)
# ──────────────────────────────────────────────────────────────────────
TEST_CASES = [

    # ─── 1. Google Search ──────────────────────────────────────────────
    # Sentence: "Go to Google, search for Selenium testing, and verify results appear"
    {
        "name": "TC-01 | Google — Search and Verify Results",
        "module": "Search",
        "steps": [
            {"action": "open_url",           "input_value": "https://www.google.com",         "timeout": 15},
            {"action": "wait",               "input_value": "2",                               "timeout": 5},
            {"action": "type_text",          "locator_type": "name",  "locator_value": "q",
             "input_value": "Selenium automated testing",                                       "timeout": 10},
            {"action": "press_key",          "locator_type": "name",  "locator_value": "q",
             "input_value": "ENTER",                                                            "timeout": 10},
            {"action": "wait",               "input_value": "3",                               "timeout": 10},
            {"action": "assert_url_contains","input_value": "search",                          "timeout": 10},
            {"action": "assert_text",        "input_value": "Selenium",                        "timeout": 10},
            {"action": "screenshot",                                                            "timeout": 5},
        ]
    },

    # ─── 2. Wikipedia ──────────────────────────────────────────────────
    # Sentence: "Open Wikipedia, search for Artificial Intelligence, and verify the article loads"
    {
        "name": "TC-02 | Wikipedia — Search Article and Verify Content",
        "module": "Navigation",
        "steps": [
            {"action": "open_url",           "input_value": "https://en.wikipedia.org",       "timeout": 15},
            {"action": "wait",               "input_value": "2",                               "timeout": 5},
            {"action": "assert_title_contains","input_value": "Wikipedia",                     "timeout": 10},
            {"action": "type_text",          "locator_type": "id", "locator_value": "searchInput",
             "input_value": "Artificial Intelligence",                                          "timeout": 10},
            {"action": "press_key",          "locator_type": "id", "locator_value": "searchInput",
             "input_value": "ENTER",                                                            "timeout": 10},
            {"action": "wait",               "input_value": "3",                               "timeout": 10},
            {"action": "assert_url_contains","input_value": "Artificial_intelligence",         "timeout": 15},
            {"action": "assert_text",        "input_value": "intelligence",                    "timeout": 10},
            {"action": "screenshot",                                                            "timeout": 5},
        ]
    },

    # ─── 3. GitHub ─────────────────────────────────────────────────────
    # Sentence: "Go to GitHub, search for selenium python repository, and open the first result"
    {
        "name": "TC-03 | GitHub — Search Repository and Verify Page",
        "module": "Navigation",
        "steps": [
            {"action": "open_url",           "input_value": "https://github.com",              "timeout": 15},
            {"action": "wait",               "input_value": "2",                               "timeout": 5},
            {"action": "assert_title_contains","input_value": "GitHub",                        "timeout": 10},
            {"action": "type_text",
             "locator_type": "xpath",
             "locator_value": "//input[@placeholder='Search or jump to...']",
             "input_value": "selenium python",                                                  "timeout": 10},
            {"action": "press_key",
             "locator_type": "xpath",
             "locator_value": "//input[@placeholder='Search or jump to...']",
             "input_value": "ENTER",                                                            "timeout": 10},
            {"action": "wait",               "input_value": "3",                               "timeout": 10},
            {"action": "assert_url_contains","input_value": "search",                          "timeout": 10},
            {"action": "assert_text",        "input_value": "selenium",                        "timeout": 10},
            {"action": "screenshot",                                                            "timeout": 5},
        ]
    },

    # ─── 4. W3Schools ──────────────────────────────────────────────────
    # Sentence: "Open W3Schools, navigate to the HTML tutorial, and verify the page title"
    {
        "name": "TC-04 | W3Schools — Navigate HTML Tutorial Page",
        "module": "Navigation",
        "steps": [
            {"action": "open_url",            "input_value": "https://www.w3schools.com/html/", "timeout": 15},
            {"action": "wait",                "input_value": "2",                               "timeout": 5},
            {"action": "assert_title_contains","input_value": "HTML",                           "timeout": 10},
            {"action": "assert_text",         "input_value": "HTML Tutorial",                  "timeout": 10},
            {"action": "scroll_page",         "input_value": "500",                            "timeout": 5},
            {"action": "wait",                "input_value": "1",                              "timeout": 5},
            {"action": "assert_text",         "input_value": "HTML",                           "timeout": 10},
            {"action": "screenshot",                                                            "timeout": 5},
        ]
    },

    # ─── 5. Books to Scrape ────────────────────────────────────────────
    # Sentence: "Open books.toscrape.com, browse the catalogue, and verify books are listed"
    {
        "name": "TC-05 | Books to Scrape — Browse Catalogue and Verify Listing",
        "module": "E-Commerce",
        "steps": [
            {"action": "open_url",            "input_value": "https://books.toscrape.com",     "timeout": 15},
            {"action": "wait",                "input_value": "2",                              "timeout": 5},
            {"action": "assert_title_contains","input_value": "Books",                         "timeout": 10},
            {"action": "assert_text",         "input_value": "1000 books found",               "timeout": 10},
            {"action": "scroll_page",         "input_value": "400",                            "timeout": 5},
            {"action": "assert_element_visible",
             "locator_type": "css", "locator_value": "article.product_pod",                    "timeout": 10},
            {"action": "screenshot",                                                            "timeout": 5},
        ]
    },

    # ─── 6. Quotes to Scrape ───────────────────────────────────────────
    # Sentence: "Go to quotes.toscrape.com, search for Einstein quotes, and verify a quote appears"
    {
        "name": "TC-06 | Quotes to Scrape — Search Author and Verify Quote",
        "module": "Search",
        "steps": [
            {"action": "open_url",  "input_value": "https://quotes.toscrape.com",              "timeout": 15},
            {"action": "wait",      "input_value": "2",                                         "timeout": 5},
            {"action": "assert_title_contains","input_value": "Quotes",                         "timeout": 10},
            {"action": "click",
             "locator_type": "xpath",
             "locator_value": "//a[contains(text(),'Albert Einstein')]",                         "timeout": 10},
            {"action": "wait",      "input_value": "2",                                         "timeout": 5},
            {"action": "assert_url_contains","input_value": "Einstein",                         "timeout": 10},
            {"action": "assert_text","input_value": "imagination",                              "timeout": 10},
            {"action": "screenshot",                                                             "timeout": 5},
        ]
    },

    # ─── 7. The Internet (Heroku) – Dynamic Loading ────────────────────
    # Sentence: "Go to the Heroku test app, click Start to load dynamic content, and verify it appears"
    {
        "name": "TC-07 | Herokuapp — Dynamic Content Loading Test",
        "module": "Dynamic Content",
        "steps": [
            {"action": "open_url",            "input_value": "https://the-internet.herokuapp.com/dynamic_loading/1", "timeout": 15},
            {"action": "wait",                "input_value": "2",                              "timeout": 5},
            {"action": "click",
             "locator_type": "xpath",
             "locator_value": "//button[text()='Start']",                                       "timeout": 10},
            {"action": "wait_for_element",
             "locator_type": "id", "locator_value": "finish",                                   "timeout": 20},
            {"action": "assert_text",         "input_value": "Hello World!",                   "timeout": 15},
            {"action": "screenshot",                                                            "timeout": 5},
        ]
    },

    # ─── 8. DemoQA — Form Fill ─────────────────────────────────────────
    # Sentence: "Open DemoQA, fill out the text box form with name and email, and submit it"
    {
        "name": "TC-08 | DemoQA — Fill Text Box Form and Submit",
        "module": "Form Submission",
        "steps": [
            {"action": "open_url",  "input_value": "https://demoqa.com/text-box",              "timeout": 15},
            {"action": "wait",      "input_value": "2",                                         "timeout": 5},
            {"action": "type_text",
             "locator_type": "id", "locator_value": "userName",
             "input_value": "Nayana Astakar",                                                   "timeout": 10},
            {"action": "type_text",
             "locator_type": "id", "locator_value": "userEmail",
             "input_value": "nayana@example.com",                                               "timeout": 10},
            {"action": "type_text",
             "locator_type": "id", "locator_value": "currentAddress",
             "input_value": "123 Main Street, Bengaluru",                                       "timeout": 10},
            {"action": "scroll_page","input_value": "300",                                      "timeout": 5},
            {"action": "click",
             "locator_type": "id", "locator_value": "submit",                                   "timeout": 10},
            {"action": "wait",      "input_value": "2",                                         "timeout": 5},
            {"action": "assert_element_visible",
             "locator_type": "id", "locator_value": "output",                                   "timeout": 10},
            {"action": "screenshot",                                                             "timeout": 5},
        ]
    },

    # ─── 9. Stack Overflow ─────────────────────────────────────────────
    # Sentence: "Go to Stack Overflow, search for selenium flaky tests, and verify questions appear"
    {
        "name": "TC-09 | Stack Overflow — Search Question and Verify Results",
        "module": "Search",
        "steps": [
            {"action": "open_url",           "input_value": "https://stackoverflow.com",       "timeout": 15},
            {"action": "wait",               "input_value": "2",                               "timeout": 5},
            {"action": "assert_title_contains","input_value": "Stack Overflow",                "timeout": 10},
            {"action": "type_text",
             "locator_type": "id", "locator_value": "q",
             "input_value": "selenium flaky tests",                                             "timeout": 10},
            {"action": "press_key",
             "locator_type": "id", "locator_value": "q",
             "input_value": "ENTER",                                                            "timeout": 10},
            {"action": "wait",               "input_value": "3",                               "timeout": 10},
            {"action": "assert_url_contains","input_value": "search",                          "timeout": 10},
            {"action": "assert_text",        "input_value": "selenium",                        "timeout": 10},
            {"action": "screenshot",                                                            "timeout": 5},
        ]
    },

    # ─── 10. Automation Exercise ───────────────────────────────────────
    # Sentence: "Open Automation Exercise site, click on Products, and verify the product list loads"
    {
        "name": "TC-10 | AutomationExercise — Browse Products Page",
        "module": "E-Commerce",
        "steps": [
            {"action": "open_url",            "input_value": "https://automationexercise.com", "timeout": 15},
            {"action": "wait",                "input_value": "2",                              "timeout": 5},
            {"action": "assert_title_contains","input_value": "Automation",                    "timeout": 10},
            {"action": "click",
             "locator_type": "xpath",
             "locator_value": "//a[@href='/products']",                                         "timeout": 10},
            {"action": "wait",                "input_value": "2",                              "timeout": 5},
            {"action": "assert_url_contains", "input_value": "products",                       "timeout": 10},
            {"action": "assert_text",         "input_value": "All Products",                   "timeout": 10},
            {"action": "type_text",
             "locator_type": "id", "locator_value": "search_product",
             "input_value": "dress",                                                            "timeout": 10},
            {"action": "click",
             "locator_type": "id", "locator_value": "submit_search",                           "timeout": 10},
            {"action": "wait",                "input_value": "2",                              "timeout": 5},
            {"action": "assert_text",         "input_value": "Searched Products",              "timeout": 10},
            {"action": "screenshot",                                                            "timeout": 5},
        ]
    },
]

# ── 3. Insert ────────────────────────────────────────────────
inserted = 0
for tc in TEST_CASES:
    execute(
        "INSERT INTO test_cases (project_id, name, steps_json, enabled, module) VALUES (?,?,?,1,?)",
        (project_id, tc["name"], json.dumps(tc["steps"]), tc.get("module", "General"))
    )
    print(f"  Inserted: {tc['name']}")
    inserted += 1

print("\n" + "-"*60)
print(f"Done! {inserted} test cases seeded.")
print(f"Open: http://localhost:8080/projects/{project_id}")
