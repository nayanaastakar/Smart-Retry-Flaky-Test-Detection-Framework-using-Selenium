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
    error_lower = error.lower()
    
    if "timeout" in error_lower:
        root_cause = "Element wait timeout - element may not exist or page load is slow."
        fix = "Increase the timeout value in the test step. If the page is slow, add an explicit wait for page load. If the element locator changed, update the locator."
        severity = "high"
    elif "no such element" in error_lower or "unable to locate" in error_lower:
        root_cause = "Element not found - the locator is incorrect, or the element is not yet attached to the DOM."
        fix = "Use the DOM inspector to verify the locator (XPath/CSS/ID). Ensure the element isn't inside an iframe, or add a wait step before this action."
        severity = "high"
    elif "stale element" in error_lower:
        root_cause = "Stale element reference - the DOM was updated or refreshed after the element was initially found."
        fix = "Do not cache elements across page loads. Re-fetch the element immediately before interacting with it, or add a brief wait."
        severity = "medium"
    elif "element not interactable" in error_lower:
        root_cause = "Element not interactable - it exists in the DOM but is hidden, disabled, or covered by another element (like a modal or overlay)."
        fix = "Check if an overlay/modal is blocking the element. You may need to scroll to the element, wait for it to become visible, or close the blocking modal first."
        severity = "medium"
    elif "invalid selector" in error_lower:
        root_cause = "Invalid selector - the provided XPath or CSS selector has a syntax error."
        fix = "Review the selector string. Check for missing quotes, brackets, or invalid XPath syntax. Test the selector manually in your browser's console."
        severity = "high"
    elif "assertionerror" in error_lower:
        root_cause = "Validation failure - the application did not return the expected state or text."
        if "welcome" in error_lower or "dashboard" in error_lower or "login" in error_lower:
            fix = "Check if the test credentials are valid. The authentication step might have failed."
        else:
            fix = "Verify if the application's UI or data has legitimately changed. If the new behavior is correct, update the test assertion string."
        severity = "critical"
    elif "webdriverexception" in error_lower or "fatal" in error_lower:
        root_cause = "Fatal WebDriver Error - the browser crashed or the driver connection was lost."
        fix = "Ensure your ChromeDriver matches your installed Chrome browser version. Check server resources (RAM/CPU) if the browser is crashing under load."
        severity = "critical"
    elif error:
        root_cause = f"Test failure: {error.split('Stacktrace:')[0][:150]}..."
        fix = "Review the test steps, execution logs, and application state at the time of failure."
        severity = "medium"
    else:
        root_cause = "Unknown failure - no error message recorded."
        fix = "Enable detailed logging and re-run the test to capture the failure reason."
        severity = "low"
    execute(
        """INSERT OR REPLACE INTO ai_analysis 
           (execution_id, root_cause, suggested_fix, severity, confidence_score, recommendations, model_used)
           VALUES (?,?,?,?,?,?,?)""",
        (exec_id, root_cause, fix, severity, 97.0, "Review logs and screenshots for details", "heuristic")
    )
    flash("Analysis complete", "success")
    return redirect(url_for("ai_analysis.index"))
