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

    from config import settings
    screenshots = []
    prefix = f"exec_{exec_id}_"
    if settings.EVIDENCE_DIR.exists():
        for f in settings.EVIDENCE_DIR.iterdir():
            if f.is_file() and f.name.startswith(prefix) and f.suffix.lower() in ('.png', '.jpg'):
                screenshots.append({
                    "name": f.name,
                    "url": url_for('history.serve_evidence', filename=f.name)
                })
    screenshots.sort(key=lambda x: x["name"])

    return render_template("history/detail.html", execution=execution, retries=retries, ai=ai, screenshots=screenshots)


@history_bp.route("/evidence/<path:filename>")
def serve_evidence(filename):
    from flask import send_from_directory
    from config import settings
    return send_from_directory(settings.EVIDENCE_DIR, filename)


@history_bp.route("/evidence")
@login_required
def evidence_list():
    from config import settings
    by_execution = {}
    
    if settings.EVIDENCE_DIR.exists():
        for f in settings.EVIDENCE_DIR.iterdir():
            if f.is_file() and f.name.startswith("exec_") and f.suffix.lower() in ('.png', '.jpg'):
                parts = f.name.split("_")
                if len(parts) >= 2:
                    try:
                        exec_id = int(parts[1])
                        if exec_id not in by_execution:
                            by_execution[exec_id] = []
                        by_execution[exec_id].append({
                            "name": f.name,
                            "url": url_for('history.serve_evidence', filename=f.name)
                        })
                    except ValueError:
                        continue

    evidence_data = []
    for exec_id, screenshots in by_execution.items():
        exec_info = fetchone("SELECT e.*, p.name as project_name FROM executions e LEFT JOIN projects p ON e.project_id=p.id WHERE e.id=?", (exec_id,))
        if exec_info:
            screenshots.sort(key=lambda x: x["name"])
            evidence_data.append({
                "execution": exec_info,
                "screenshots": screenshots
            })
            
    evidence_data.sort(key=lambda x: x["execution"]["id"], reverse=True)
    return render_template("history/evidence.html", evidence_data=evidence_data)


@history_bp.route("/<int:exec_id>/delete", methods=["POST"])
@login_required
def delete(exec_id):
    execute("DELETE FROM executions WHERE id=?", (exec_id,))
    return redirect(url_for("history.index"))
