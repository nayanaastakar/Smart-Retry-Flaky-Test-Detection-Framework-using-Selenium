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
    test_cases = fetchall("SELECT tc.*, p.name as project_name FROM test_cases tc LEFT JOIN projects p ON tc.project_id=p.id ORDER BY tc.id DESC")
    return render_template("test_cases/index.html", test_cases=test_cases)
