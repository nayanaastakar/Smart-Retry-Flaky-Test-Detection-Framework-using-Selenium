from flask import Blueprint, render_template, redirect, url_for, session
from database.db_manager import fetchall
test_cases_bp = Blueprint("test_cases", __name__, url_prefix="/test-cases")

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated

@test_cases_bp.route("/")
@login_required
def index():
    # Left join flaky_scores to retrieve computed flakiness score and verdict
    query = """
        SELECT tc.*, p.name as project_name, fs.score as flaky_score, fs.verdict as flaky_verdict
        FROM test_cases tc 
        LEFT JOIN projects p ON tc.project_id=p.id
        LEFT JOIN flaky_scores fs ON tc.id=fs.test_case_id
        ORDER BY tc.id DESC
    """
    rows = fetchall(query)
    # Convert sqlite3.Row to standard dict for flawless Jinja2 property access
    test_cases = [dict(r) for r in rows]
    return render_template("test_cases/index.html", test_cases=test_cases)
