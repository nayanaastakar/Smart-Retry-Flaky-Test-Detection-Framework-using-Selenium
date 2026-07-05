from flask import Blueprint, render_template, redirect, url_for, session
from database.db_manager import fetchall, fetchone
reports_bp = Blueprint("reports", __name__, url_prefix="/reports")
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated
@reports_bp.route("/")
@login_required
def index():
    executions = fetchall("SELECT * FROM executions ORDER BY started_at DESC LIMIT 20")
    return render_template("reports/index.html", executions=executions)
