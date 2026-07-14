from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify, flash
from database.db_manager import fetchall, fetchone, execute
import json
from config import settings

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

    error = execution["error_message"] or ""
    log_output = execution["log_output"] or ""
    test_name = execution["test_name"] or ""

    # Check if Gemini API is enabled and key is set
    if settings.AI_ENABLED and settings.GEMINI_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=settings.GEMINI_API_KEY)

            system_instruction = (
                "You are an expert QA automation triage bot. "
                "Analyze the provided automated test failure logs and details. "
                "Return a raw JSON object containing these exact keys:\n"
                "  root_cause: A precise explanation of why the test failed.\n"
                "  suggested_fix: Actionable steps the developer/tester should take to fix the test or application.\n"
                "  severity: One of: low, medium, high, critical.\n"
                "  confidence_score: A numeric float value between 50.0 and 100.0 indicating your confidence in this analysis.\n"
                "  recommendations: A short sentence of recommendations.\n\n"
                "Rules:\n"
                "- Return ONLY raw JSON. No markdown formatting, no backticks, no explanations outside the JSON.\n"
                "- Set higher confidence_score (e.g. 90-99%) for clear errors like Timeouts, ElementNotInteractable, or AssertionError.\n"
                "- Set lower confidence_score (e.g. 60-80%) if the error is vague or logs are sparse.\n"
                "- Base the root cause specifically on the error message and execution log provided."
            )

            prompt = (
                f"Test Name: {test_name}\n"
                f"Error Message: {error}\n"
                f"Execution Logs:\n{log_output}"
            )

            # Try primary model, fallback if it is unavailable (503/429/etc)
            response = None
            models_to_try = [settings.GEMINI_MODEL, "gemini-3.1-flash-lite", "gemini-3-flash-preview"]
            last_error = None
            for m in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=m,
                        contents=f"{system_instruction}\n\nInput Failure Details:\n{prompt}"
                    )
                    break
                except Exception as e:
                    last_error = e
                    continue
                    
            if response is None:
                raise last_error or Exception("All Gemini models were unavailable.")

            raw_text = response.text.strip()
            # Strip markdown if present
            if raw_text.startswith("```"):
                parts = raw_text.split("```")
                raw_text = parts[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
            raw_text = raw_text.strip()

            analysis_result = json.loads(raw_text)

            root_cause = analysis_result.get("root_cause", "AI failed to extract root cause.")
            fix = analysis_result.get("suggested_fix", "Review logs and screenshots manually.")
            severity = analysis_result.get("severity", "medium").lower()
            confidence = float(analysis_result.get("confidence_score", 95.0))
            recommendations = analysis_result.get("recommendations", "Review logs and screenshots for details")

            execute(
                """INSERT OR REPLACE INTO ai_analysis 
                   (execution_id, root_cause, suggested_fix, severity, confidence_score, recommendations, model_used)
                   VALUES (?,?,?,?,?,?,?)""",
                (exec_id, root_cause, fix, severity, confidence, recommendations, "gemini-3.5-flash")
            )
            flash("AI Analysis complete using Gemini!", "success")
            return redirect(url_for("ai_analysis.index"))

        except Exception as e:
            # Fallback to local heuristic if Gemini fails
            pass

    # Heuristic Fallback
    error_lower = error.lower()
    if "timeout" in error_lower:
        root_cause = "Element wait timeout - element may not exist or page load is slow."
        fix = "Increase the timeout value in the test step. If the page is slow, add an explicit wait for page load. If the element locator changed, update the locator."
        severity = "high"
        confidence = 90.0
    elif "no such element" in error_lower or "unable to locate" in error_lower:
        root_cause = "Element not found - the locator is incorrect, or the element is not yet attached to the DOM."
        fix = "Use the DOM inspector to verify the locator (XPath/CSS/ID). Ensure the element isn't inside an iframe, or add a wait step before this action."
        severity = "high"
        confidence = 88.0
    elif "stale element" in error_lower:
        root_cause = "Stale element reference - the DOM was updated or refreshed after the element was initially found."
        fix = "Do not cache elements across page loads. Re-fetch the element immediately before interacting with it, or add a brief wait."
        severity = "medium"
        confidence = 85.0
    elif "element not interactable" in error_lower:
        root_cause = "Element not interactable - it exists in the DOM but is hidden, disabled, or covered by another element (like a modal or overlay)."
        fix = "Check if an overlay/modal is blocking the element. You may need to scroll to the element, wait for it to become visible, or close the blocking modal first."
        severity = "medium"
        confidence = 82.0
    elif "invalid selector" in error_lower:
        root_cause = "Invalid selector - the provided XPath or CSS selector has a syntax error."
        fix = "Review the selector string. Check for missing quotes, brackets, or invalid XPath syntax. Test the selector manually in your browser's console."
        severity = "high"
        confidence = 95.0
    elif "assertionerror" in error_lower:
        root_cause = "Validation failure - the application did not return the expected state or text."
        if "welcome" in error_lower or "dashboard" in error_lower or "login" in error_lower:
            fix = "Check if the test credentials are valid. The authentication step might have failed."
        else:
            fix = "Verify if the application's UI or data has legitimately changed. If the new behavior is correct, update the test assertion string."
        severity = "critical"
        confidence = 97.0
    elif "webdriverexception" in error_lower or "fatal" in error_lower:
        root_cause = "Fatal WebDriver Error - the browser crashed or the driver connection was lost."
        fix = "Ensure your ChromeDriver matches your installed Chrome browser version. Check server resources (RAM/CPU) if the browser is crashing under load."
        severity = "critical"
        confidence = 92.0
    elif error:
        root_cause = f"Test failure: {error.split('Stacktrace:')[0][:150]}..."
        fix = "Review the test steps, execution logs, and application state at the time of failure."
        severity = "medium"
        confidence = 70.0
    else:
        root_cause = "Unknown failure - no error message recorded."
        fix = "Enable detailed logging and re-run the test to capture the failure reason."
        severity = "low"
        confidence = 50.0

    execute(
        """INSERT OR REPLACE INTO ai_analysis 
           (execution_id, root_cause, suggested_fix, severity, confidence_score, recommendations, model_used)
           VALUES (?,?,?,?,?,?,?)""",
        (exec_id, root_cause, fix, severity, confidence, "Review logs and screenshots for details", "heuristic")
    )
    flash("Analysis complete (Heuristic Fallback)", "success")
    return redirect(url_for("ai_analysis.index"))
