from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from database.db_manager import fetchall, fetchone, execute

history_bp = Blueprint("history", __name__, url_prefix="/history")

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@history_bp.route("/")
@login_required
def index():
    page = int(request.args.get("page", 1))
    per_page = 20
    offset = (page - 1) * per_page
    search = request.args.get("q", "")
    status_filter = request.args.get("status", "")

    query = "SELECT * FROM executions WHERE 1=1"
    params = []
    if search:
        query += " AND test_name LIKE ?"
        params.append(f"%{search}%")
    if status_filter:
        query += " AND status=?"
        params.append(status_filter)
    query += " ORDER BY started_at DESC LIMIT ? OFFSET ?"
    params += [per_page, offset]

    executions = fetchall(query, tuple(params))
    total = fetchone("SELECT COUNT(*) as c FROM executions")["c"]
    total_pages = (total + per_page - 1) // per_page

    return render_template("history/index.html", executions=executions,
                           page=page, total_pages=total_pages, search=search, status_filter=status_filter)


@history_bp.route("/<int:exec_id>")
@login_required
def detail(exec_id):
    execution = fetchone("SELECT * FROM executions WHERE id=?", (exec_id,))
    retries = fetchall("SELECT * FROM retries WHERE execution_id=? ORDER BY attempt_number", (exec_id,))
    ai = fetchone("SELECT * FROM ai_analysis WHERE execution_id=?", (exec_id,))
    return render_template("history/detail.html", execution=execution, retries=retries, ai=ai)


@history_bp.route("/<int:exec_id>/delete", methods=["POST"])
@login_required
def delete(exec_id):
    execute("DELETE FROM executions WHERE id=?", (exec_id,))
    return redirect(url_for("history.index"))
