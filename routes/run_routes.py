from flask import Blueprint, render_template, request, redirect, url_for, session, flash
run_bp = Blueprint("run", __name__, url_prefix="/run")
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated
@run_bp.route("/")
@login_required
def index():
    return render_template("run/index.html")
@run_bp.route("/results/<project_name>")
@login_required
def results(project_name):
    from database.db_manager import fetchall
    executions = fetchall(
        "SELECT e.* FROM executions e JOIN projects p ON e.project_id=p.id WHERE p.name=? ORDER BY e.started_at DESC LIMIT 20",
        (project_name,)
    )
    return render_template("run/results.html", project_name=project_name, executions=executions)
