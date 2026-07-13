from flask import Blueprint, render_template, redirect, url_for, session
from database.db_manager import fetchone, fetchall

dashboard_bp = Blueprint("dashboard", __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@dashboard_bp.route("/")
@login_required
def index():
    stats = {
        "total": fetchone("SELECT COUNT(*) as c FROM executions")["c"],
        "passed": fetchone("SELECT COUNT(*) as c FROM executions WHERE status='pass'")["c"],
        "failed": fetchone("SELECT COUNT(*) as c FROM executions WHERE status='fail'")["c"],
        "flaky": fetchone("SELECT COUNT(*) as c FROM executions WHERE status='flaky'")["c"],
        "projects": fetchone("SELECT COUNT(*) as c FROM projects")["c"],
        "test_cases": fetchone("SELECT COUNT(*) as c FROM test_cases")["c"],
    }
    # Convert sqlite3.Row → plain dict so Jinja2 tojson filter works
    rows = fetchall("SELECT * FROM executions ORDER BY started_at DESC LIMIT 100")
    recent = [
        {
            "id": r["id"],
            "test_name": r["test_name"],
            "status": r["status"],
            "retry_count": r["retry_count"] or 0,
            "duration_seconds": r["duration_seconds"] or 0,
            "browser": r["browser"] or "chrome",
            "started_at": r["started_at"] or "",
        }
        for r in rows
    ]
    return render_template("dashboard/index.html", stats=stats, recent=recent)
