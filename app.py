"""app.py - Application entry point."""
from __future__ import annotations
import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, render_template

from config import settings
from database.db_manager import init_db


def configure_logging() -> None:
    settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(settings.LOGS_DIR / "app.log"),
        ],
    )


def create_app() -> Flask:
    configure_logging()
    settings.ensure_directories()
    init_db()

    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=settings.SESSION_LIFETIME_DAYS)
    app.config["JSON_SORT_KEYS"] = False

    # Custom Jinja2 filters
    @app.template_filter("from_json")
    def from_json_filter(value):
        try:
            return json.loads(value) if value else []
        except Exception:
            return []

    @app.template_filter("localtime")
    def localtime_filter(value):
        if not value: return "-"
        try:
            dt = datetime.strptime(value[:19].replace("T", " "), "%Y-%m-%d %H:%M:%S")
            dt = dt + timedelta(hours=5, minutes=30)
            return dt.strftime("%Y-%m-%d %I:%M %p")
        except Exception:
            return value[:16]

    @app.template_filter("basename")
    def basename_filter(value):
        return Path(value).name if value else ""

    @app.template_filter("clean_error")
    def clean_error_filter(value):
        if not value: return "Unknown Error"
        import re
        
        # 1. Remove everything after "Stacktrace:"
        if "Stacktrace:" in value:
            value = value.split("Stacktrace:")[0]
            
        # 2. Extract the actual message
        lines = [line.strip() for line in value.split('\n') if line.strip()]
        if not lines:
            return "Fatal Error: Browser or Driver crashed unexpectedly."
            
        if lines[0] == "Message:" and len(lines) > 1:
            msg = lines[1]
        else:
            msg = lines[0]
            if msg.startswith("Message:"):
                msg = msg.replace("Message:", "").strip()
                
        if not msg:
            msg = "Fatal Error: Browser or Driver crashed unexpectedly."

        msg = re.sub(r'\(Session info:.*?\)', '', msg).strip()
        msg_lower = msg.lower()
        
        if "no such element" in msg_lower or "unable to locate element" in msg_lower:
            return "Element not found. (Reason: The locator is incorrect, or the element hasn't loaded yet)"
        if "timeout" in msg_lower:
            return "Timeout. (Reason: The page or element took too long to load)"
        if "element not interactable" in msg_lower:
            return "Element not interactable. (Reason: The element exists but is hidden or covered by another element)"
        if "stale element" in msg_lower:
            return "Stale element. (Reason: The page refreshed or the DOM changed after finding the element)"
        if "invalid selector" in msg_lower:
            return "Invalid selector. (Reason: The XPath or CSS selector has a syntax error)"
        if "assertionerror" in msg_lower:
            if "welcome" in msg_lower or "dashboard" in msg_lower or "login" in msg_lower:
                return "Login Failed. (Reason: Invalid username or password, or dashboard didn't load)"
            return f"Validation Failed. (Reason: {msg.replace('AssertionError:', '').strip()})"
        if "webdriverexception" in msg_lower or "fatal error" in msg_lower or "fatal" in msg_lower:
            return "Fatal Error. (Reason: Browser crashed or WebDriver failed to initialize)"
            
        return msg[:150] + ("..." if len(msg) > 150 else "")

    # Blueprints
    from routes.auth_routes import auth_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.history_routes import history_bp
    from routes.settings_routes import settings_bp
    from routes.api_routes import api_bp
    from routes.profile_routes import profile_bp
    from routes.reports_routes import reports_bp
    from routes.run_routes import run_bp
    from routes.test_cases_routes import test_cases_bp
    from routes.website_profiles_routes import website_profiles_bp
    from routes.console_routes import console_bp
    from routes.ai_analysis_routes import ai_analysis_bp
    from routes.projects_routes import projects_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    app.register_blueprint(profile_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(run_bp)
    app.register_blueprint(test_cases_bp)
    app.register_blueprint(website_profiles_bp)
    app.register_blueprint(console_bp)
    app.register_blueprint(ai_analysis_bp)
    app.register_blueprint(projects_bp)

    @app.context_processor
    def inject_globals():
        return {
            "company_name": settings.COMPANY_NAME,
            "app_name": settings.REPORT_LOGO_TEXT,
        }

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        logging.getLogger("smart_retry.app").exception("Unhandled server error")
        return render_template("errors/500.html"), 500

    return app


app = create_app()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--init-db", action="store_true")
    args = parser.parse_args()

    if args.init_db:
        from database.seed import run_all
        run_all()

    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
