# Smart Retry & Flaky Test Detection Framework

An enterprise-style Selenium test automation platform: **fully generalized —
any website via dynamic Projects, not predefined profiles or dropdowns** —
with automatic retries, statistical flaky-test detection, a visual test
builder, execution history, a live Flask dashboard, and a REST API.

## Architecture note: Projects replaced Website Profiles

Earlier iterations of this project used a "Website Profiles" dropdown
(SauceDemo, OrangeHRM, etc.). That's gone from the primary workflow. The
current model:

- **Project** = just a name + a URL. `POST /projects/create` with any
  website — no predefined site knowledge required anywhere in the code.
- **Test Case** = an ordered list of steps (`core/step_definitions.py` /
  `core/step_executor.py`), built visually at `/projects/<id>/tests/new`.
  22 step types: navigation, click / double-click / right-click, type text,
  clear, select dropdown, checkbox, wait, scroll, hover, press key, switch
  frame / window, screenshot checkpoint, 6 assertion types, and custom
  JavaScript. Every step is data (locator type + value + input + timeout),
  not code — so it works against any site's DOM.
- **Run a Project** (`POST /projects/<id>/run`) drives one real Selenium
  session through every enabled test case's steps via the same
  `SmartRetryEngine` + `EvidenceCollector` + `FlakyDetector` used everywhere
  else, then lands on the same flakiness-verdict page
  (`/run/results/<project_name>`) that Quick Run uses.
- The old `website_profiles` table/blueprint/Quick-Run-by-domain feature
  still exists and still works (kept for backward compatibility and as a
  zero-setup instant check), but it's no longer the primary nav item —
  **Projects** is.

## Status

| Module | Status |
|---|---|
| Projects — generalized "any website" entity | Done |
| Visual Test Builder — 22 dynamic step types, add/reorder/remove, edit existing | Done |
| Step Executor — interprets steps against any site's DOM at runtime | Done |
| Project Runner — runs every enabled test case through retry/evidence/flaky pipeline | Done |
| Flask app + auth (login/logout/sessions) | Done |
| Smart Retry Engine (exponential backoff, per-attempt persistence) | Done |
| Flaky Test Detection (flip-rate + retry-save scoring, 3-way classification) | Done |
| Evidence Collector (screenshots, console logs, stack traces, OS/browser) | Done |
| WebDriver Factory (Chrome/Edge/Firefox, headless toggle) | Done |
| Analytics service (KPIs, trends, module breakdown, top failures) | Done |
| Dashboard UI (dark/light theme, KPI tiles, 3 live Chart.js charts) | Done |
| Execution History (search/filter/sort/delete/export CSV) | Done |
| Reporting Engine — HTML / PDF / JSON / CSV (Module 5) | Done |
| AI Failure Analysis via Ollama + heuristic fallback (Module 6) | Done |
| Quick Run — paste any URL, N-iteration generic flaky check, no project needed | Done |
| Live Console, AI Analysis browser, legacy Test Cases list, Settings, Profile | Done |
| REST API (`/api/v1/...`) | Done |

### What was verified in this sandbox vs. what needs your machine
This sandbox has no browser and no network, so a real Selenium session
could not be run end-to-end here. What was verified, against the real
SQLite database via Flask's test client:

- Full Project CRUD (create with URL auto-normalization, duplicate-name
  rejection, delete cascades test cases).
- The Test Builder: created a 5-step login-style test case (open URL, type
  username, type password, click login, assert URL contains /dashboard),
  confirmed it persisted correctly, confirmed the edit page pre-fills every
  field, confirmed updates save.
- Malformed step JSON is rejected cleanly (no crash).
- Running an empty project (no test cases) degrades gracefully with a clear
  message instead of trying to launch a browser for nothing.
- Running a project with test cases correctly attempts a real Selenium
  session and fails gracefully with a clear "Selenium isn't installed"
  message in this sandbox (expected, since Selenium isn't installed here)
  instead of a 500 error.
- A static consistency check confirming all 22 step types shown in the
  builder UI have a real corresponding execution handler, and vice versa.

Two real bugs were caught and fixed during this verification, not left in
the delivered code: the edit page was missing a `steps_list` conversion
(would have crashed on first click), and `run_project()` imported Selenium
before checking whether there were any test cases to run (would have made
even an empty project require Selenium installed just to say it's empty).
Both are fixed and covered by the tests above.

What still needs your machine: an actual browser driving an actual website
end-to-end. The code path is proven up to the Selenium boundary; run it
once locally with Chrome, Firefox, or Edge installed to confirm the last
mile.

---

## Quick start

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # edit SECRET_KEY
python app.py --init-db          # creates schema, runs migrations, seeds admin user
python -m utils.generate_demo_data   # optional: populate dashboard with simulated history
python app.py
```

Open **http://localhost:5000** and log in:
```
Username: admin
Password: Admin@123
```

## Using the generalized workflow

1. Sidebar -> **Projects** -> **Create Project**. Give it any name and any URL.
2. Open the project -> **New Test Case** -> use the visual step builder to
   describe a flow (open a page, type into a field, click a button, assert
   something). Add as many steps as you need, in any order, reorder with
   the up/down arrows.
3. Save, then either run that one test case (play icon) or **Run All Tests**
   on the project page.
4. You land on `/run/results/<project_name>` -- a stability verdict (Stable /
   Flaky / Chronic Failure) built from real execution history, with a
   per-check breakdown (pass count, fail count, flip count, flaky score).
5. Run it again (more times, or after fixing something) and the verdict
   updates -- flakiness is a run-to-run property, so the more you run it,
   the more reliable the score.

For a one-off check with no setup at all, the **Run Tests** button
available from the dashboard still works exactly as before: paste a URL,
pick how many times to run, get the same kind of verdict page, using a
fixed generic battery (page loads, title present, links present, no broken
images, no severe console errors) instead of custom steps.

## Project structure (files added/changed for this generalization)

```
core/
├── step_definitions.py    # Selenium-free step metadata (powers the builder UI)
├── step_executor.py       # Interprets step JSON against any Selenium driver
└── project_runner.py      # Runs a project's (or a single test case's) steps
                            # through SmartRetryEngine + EvidenceCollector + FlakyDetector

routes/
└── projects_routes.py     # Projects CRUD, Test Builder pages, run-all

templates/
├── projects/index.html    # Project list/create
├── projects/detail.html   # Project dashboard: test cases, flaky summary, recent runs
└── test_cases/builder.html  # Visual step editor (add/reorder/remove steps)

database/db_manager.py     # projects table + test_cases.project_id/steps_json,
                            # with a safe ALTER-TABLE migration for existing databases
```

## Security note on the Test Builder

There is deliberately no "run arbitrary Python code" step type. The
reference spec this was built from asked for one; it was intentionally
omitted because letting user-submitted step data execute arbitrary Python
on the host is a remote-code-execution hole, not a testing feature. Custom
JavaScript is supported (`custom_js` step, via `driver.execute_script`),
since that only runs inside the browser sandbox -- the same capability any
Selenium script already has, no additional risk introduced.

## Roadmap (not yet built)

- AI locator healing (suggesting a fixed locator when one breaks)
- Drag-and-drop step reordering (currently up/down buttons -- functional,
  less flashy)
- File upload/download steps, execution video recording, network log capture
- SQLAlchemy ORM migration (currently raw parameterized SQL, which is
  simpler and sufficient at this scale but doesn't match the reference
  spec's tech stack ask)
- JWT-based auth, registration, forgot-password (currently server-side
  session auth, which is simpler and safer for a self-hosted tool)
- Swagger/OpenAPI documentation for the REST API
- Marketing-style landing page with pricing cards/testimonials
- True push-based Live Console (WebSocket/SSE) instead of 2s polling
- Parallel test execution across multiple projects/browsers at once

Say which of these matters most and it's next.
