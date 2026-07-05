import json
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database.db_manager import fetchone, fetchall, execute
from core.step_definitions import STEP_TYPES, LOCATOR_TYPES

projects_bp = Blueprint("projects", __name__, url_prefix="/projects")


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@projects_bp.route("/")
@login_required
def index():
    projects = fetchall("SELECT * FROM projects ORDER BY created_at DESC")
    return render_template("projects/index.html", projects=projects)


@projects_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        url = request.form.get("url", "").strip()
        browser = request.form.get("browser", "chrome")
        description = request.form.get("description", "")
        if not name or not url:
            flash("Name and URL are required", "error")
            return render_template("projects/create.html")
        existing = fetchone("SELECT id FROM projects WHERE name=?", (name,))
        if existing:
            flash("Project name already exists", "error")
            return render_template("projects/create.html")
        pid = execute(
            "INSERT INTO projects (name, url, browser, description) VALUES (?,?,?,?)",
            (name, url, browser, description)
        )
        flash("Project created", "success")
        return redirect(url_for("projects.detail", project_id=pid))
    return render_template("projects/create.html")


@projects_bp.route("/<int:project_id>")
@login_required
def detail(project_id):
    project = fetchone("SELECT * FROM projects WHERE id=?", (project_id,))
    if not project:
        flash("Project not found", "error")
        return redirect(url_for("projects.index"))
    test_cases = fetchall("SELECT * FROM test_cases WHERE project_id=? ORDER BY id", (project_id,))
    recent_runs = fetchall(
        "SELECT * FROM executions WHERE project_id=? ORDER BY started_at DESC LIMIT 10",
        (project_id,)
    )
    return render_template("projects/detail.html", project=project, test_cases=test_cases, recent_runs=recent_runs)


@projects_bp.route("/<int:project_id>/delete", methods=["POST"])
@login_required
def delete(project_id):
    execute("DELETE FROM projects WHERE id=?", (project_id,))
    flash("Project deleted", "success")
    return redirect(url_for("projects.index"))


@projects_bp.route("/<int:project_id>/run", methods=["POST"])
@login_required
def run(project_id):
    from core.project_runner import run_project
    try:
        result = run_project(project_id)
        flash(f"Run complete: {result.get('passed',0)}/{result.get('total',0)} passed", "success")
    except Exception as e:
        flash(f"Run failed: {e}", "error")
    return redirect(url_for("projects.detail", project_id=project_id))


@projects_bp.route("/<int:project_id>/tests/new", methods=["GET", "POST"])
@login_required
def new_test(project_id):
    project = fetchone("SELECT * FROM projects WHERE id=?", (project_id,))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        steps_json = request.form.get("steps_json", "[]")
        module = request.form.get("module", "General")
        group_name = request.form.get("group_name", "Default")
        try:
            steps = json.loads(steps_json)
        except Exception:
            steps = []
        tc_id = execute(
            "INSERT INTO test_cases (project_id, name, steps_json, enabled, module, group_name) VALUES (?,?,?,?,?,?)",
            (project_id, name, json.dumps(steps), 1, module, group_name)
        )
        flash("Test case created", "success")
        return redirect(url_for("projects.detail", project_id=project_id))
    return render_template("test_cases/builder.html", project=project, test_case=None,
                           step_types=STEP_TYPES, locator_types=LOCATOR_TYPES)


@projects_bp.route("/<int:project_id>/tests/<int:tc_id>/edit", methods=["GET", "POST"])
@login_required
def edit_test(project_id, tc_id):
    project = fetchone("SELECT * FROM projects WHERE id=?", (project_id,))
    tc = fetchone("SELECT * FROM test_cases WHERE id=? AND project_id=?", (tc_id, project_id))
    if not tc:
        flash("Test case not found", "error")
        return redirect(url_for("projects.detail", project_id=project_id))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        steps_json = request.form.get("steps_json", "[]")
        module = request.form.get("module", "General")
        group_name = request.form.get("group_name", "Default")
        try:
            steps = json.loads(steps_json)
        except Exception:
            steps = []
        execute(
            "UPDATE test_cases SET name=?, steps_json=?, module=?, group_name=? WHERE id=?",
            (name, json.dumps(steps), module, group_name, tc_id)
        )
        flash("Test case updated", "success")
        return redirect(url_for("projects.detail", project_id=project_id))
    steps_list = json.loads(tc["steps_json"] or "[]")
    return render_template("test_cases/builder.html", project=project, test_case=tc,
                           steps_list=steps_list, step_types=STEP_TYPES, locator_types=LOCATOR_TYPES)


@projects_bp.route("/<int:project_id>/tests/<int:tc_id>/delete", methods=["POST"])
@login_required
def delete_test(project_id, tc_id):
    execute("DELETE FROM test_cases WHERE id=? AND project_id=?", (tc_id, project_id))
    flash("Test case deleted", "success")
    return redirect(url_for("projects.detail", project_id=project_id))


@projects_bp.route("/<int:project_id>/tests/<int:tc_id>/run", methods=["POST"])
@login_required
def run_test(project_id, tc_id):
    from core.project_runner import run_single_test_case
    try:
        result = run_single_test_case(tc_id)
        status = "PASSED" if result.get("pass") else "FAILED"
        flash(f"Test {status} (retries: {result.get('retries', 0)})", "success" if result.get("pass") else "error")
    except Exception as e:
        flash(f"Run failed: {e}", "error")
    return redirect(url_for("projects.detail", project_id=project_id))
