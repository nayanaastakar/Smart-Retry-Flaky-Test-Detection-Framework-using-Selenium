# SmartRetry — Flaky Test Detection Framework

> **Automatically detect, retry, and diagnose flaky Selenium tests with AI-powered root cause analysis.**

---

## What is SmartRetry?

SmartRetry is a full-stack QA automation platform built with **Python Flask + Selenium**.  
It solves one of the biggest problems in software testing — **flaky tests** — by:

1. **Automatically retrying** failed tests using an exponential backoff strategy
2. **Detecting flaky patterns** by analysing pass/fail flip rates across multiple runs
3. **Providing AI-powered diagnosis** with a specific root cause and actionable fix for every failure

---

## Technology Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11, Flask 3.x |
| **Browser Automation** | Selenium WebDriver 4.x |
| **Database** | SQLite (via custom `db_manager`) |
| **Frontend** | Bootstrap 5.3, Chart.js 4, Bootstrap Icons |
| **AI Analysis** | Heuristic rule engine (7 failure categories) |
| **Auth** | Flask session-based authentication |
| **Driver Management** | Custom 64-bit ChromeDriver validator |

---

## Features

| Module | Description |
|---|---|
| 🔁 **Smart Retry Engine** | Exponential backoff retry with per-attempt persistence |
| 🧠 **AI Failure Analysis** | 7-category heuristic engine: Timeout, Element not found, Stale element, Interactability, Selector errors, Assertion failures, WebDriver crashes |
| 📊 **Dashboard** | Live KPI tiles, donut chart, 7-day trend line chart |
| 🏗️ **Visual Test Builder** | 22 step types, no code needed — click, type, assert, wait, scroll, JS |
| 🤖 **AI Test Generator** | Describe a test in English → auto-generate steps |
| 📋 **Templates** | 8 pre-built templates (Login, Search, Cart, Registration, Form, Social, etc.) |
| 📈 **Reports** | Export full execution history as CSV or JSON |
| 🖼️ **Evidence** | Screenshot capture at each step for failed tests |
| 📡 **REST API** | `/api/v1/` endpoints for external integrations |
| 🖥️ **Live Console** | Real-time test execution log viewer |

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/nayanaastakar/Smart-Retry-Flaky-Test-Detection-Framework-using-Selenium.git
cd Smart-Retry-Flaky-Test-Detection-Framework-using-Selenium

# 2. Create & activate virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

Open **http://localhost:8080** and log in:

```
Username: admin
Password: Admin@123
```

> ⚠️ **Requires Google Chrome** installed on your machine. ChromeDriver is managed automatically.

---

## How to Use

### 1. Create a Project
Sidebar → **Projects** → **New Project**  
Enter any name and a target URL (e.g. `https://www.saucedemo.com`)

### 2. Build a Test Case
Open the project → **New Test Case** → use the **Visual Step Builder**  
Add steps: Open URL → Type Text → Click → Assert Text → Take Screenshot

Or use:
- **🤖 AI Generate** — describe your test in plain English
- **📋 Templates** — pick from 8 ready-made flows

### 3. Run & Analyse
Click **Run All Tests** on the project page.  
The **Smart Retry Engine** automatically retries failed steps.  
View results in **History** → click **Analyze with AI** on any failure.

### 4. Export Reports
Go to **Reports** → click **Export CSV** or **Export JSON** to download your data.

---

## Project Structure

```
smartretry/
├── app.py                    # Application entry point & Jinja2 filters
├── config.py                 # Settings (port, secret key, directories)
├── requirements.txt
│
├── core/
│   ├── driver_factory.py     # ChromeDriver management & 64-bit validation
│   ├── step_executor.py      # Executes 22 step types against any DOM
│   ├── project_runner.py     # Smart Retry Engine + Flaky Detector pipeline
│   ├── flaky_detector.py     # Flaky score calculation & verdict (stable/flaky/chronic)
│   └── step_definitions.py   # Step metadata used by the visual builder
│
├── routes/
│   ├── projects_routes.py    # Projects CRUD + Test Builder + Run endpoints
│   ├── ai_analysis_routes.py # AI heuristic analysis engine
│   ├── reports_routes.py     # Report views + CSV/JSON export
│   ├── history_routes.py     # Execution history & evidence
│   └── ...                   # auth, dashboard, console, settings, profile
│
├── templates/
│   ├── base.html             # Responsive sidebar layout with hamburger menu
│   ├── auth/login.html       # Animated login page
│   ├── dashboard/index.html  # Charts + KPI tiles
│   ├── ai_analysis/          # AI diagnosis with confidence bars
│   ├── reports/              # Export-enabled reports table
│   └── test_cases/builder.html  # Visual step builder
│
└── database/
    └── db_manager.py         # Raw SQLite wrapper (fetchone, fetchall, execute)
```

---

## AI Analysis — Error Categories

| Error Type | Severity | Root Cause |
|---|---|---|
| Timeout | 🟠 High | Element load too slow or page unresponsive |
| Element Not Found | 🟠 High | Wrong locator or element not in DOM yet |
| Stale Element | 🟡 Medium | DOM refreshed after element was captured |
| Not Interactable | 🟡 Medium | Element hidden or covered by overlay |
| Invalid Selector | 🟠 High | XPath/CSS syntax error |
| Assertion Error | 🔴 Critical | Expected text/state not found (e.g. login failed) |
| WebDriver Crash | 🔴 Critical | Chrome version mismatch or resource exhaustion |

---

## REST API

Base URL: `http://localhost:8080/api/v1/`

| Endpoint | Method | Description |
|---|---|---|
| `/executions` | GET | List all executions |
| `/executions/<id>` | GET | Get execution details |
| `/projects` | GET | List all projects |

---

## License

MIT — free to use, modify and distribute.
