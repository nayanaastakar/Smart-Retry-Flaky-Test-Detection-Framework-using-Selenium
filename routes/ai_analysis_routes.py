from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify, flash
from database.db_manager import fetchall, fetchone, execute
ai_analysis_bp = Blueprint("ai_analysis", __name__, url_prefix="/ai-analysis")
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated
@ai_analysis_bp.route("/")
@login_required
def index():
    analyses = fetchall("SELECT a.*, e.test_name, e.status FROM ai_analysis a JOIN executions e ON a.execution_id=e.id ORDER BY a.analyzed_at DESC LIMIT 20")
    pending = fetchall("SELECT * FROM executions WHERE status IN ('fail','flaky') AND id NOT IN (SELECT execution_id FROM ai_analysis) ORDER BY started_at DESC LIMIT 5")
    return render_template("ai_analysis/index.html", analyses=analyses, pending=pending)

@ai_analysis_bp.route("/analyze/<int:exec_id>", methods=["POST"])
@login_required
def analyze(exec_id):
    execution = fetchone("SELECT * FROM executions WHERE id=?", (exec_id,))
    if not execution:
        flash("Execution not found", "error")
        return redirect(url_for("ai_analysis.index"))
    # Heuristic analysis (no Ollama required)
    error = execution["error_message"] or ""
    if "TimeoutException" in error or "timeout" in error.lower():
        root_cause = "Element wait timeout - element may not exist or page load is slow"
        fix = "Increase timeout, check locator, or add explicit waits"
        severity = "high"
    elif "NoSuchElement" in error or "no such element" in error.lower():
        root_cause = "Element not found - locator may be incorrect or element is dynamic"
        fix = "Review and update the element locator"
        severity = "high"
    elif "StaleElement" in error:
        root_cause = "Stale element reference - DOM was updated after element was found"
        fix = "Re-find the element or add a wait before interaction"
        severity = "medium"
    elif error:
        root_cause = f"Test failure: {error[:200]}"
        fix = "Review test steps and application state"
        severity = "medium"
    else:
        root_cause = "Unknown failure - no error message recorded"
        fix = "Enable detailed logging and re-run the test"
        severity = "low"
    execute(
        """INSERT OR REPLACE INTO ai_analysis 
           (execution_id, root_cause, suggested_fix, severity, confidence_score, recommendations, model_used)
           VALUES (?,?,?,?,?,?,?)""",
        (exec_id, root_cause, fix, severity, 0.75, "Review logs and screenshots for details", "heuristic")
    )
    flash("Analysis complete", "success")
    return redirect(url_for("ai_analysis.index"))
