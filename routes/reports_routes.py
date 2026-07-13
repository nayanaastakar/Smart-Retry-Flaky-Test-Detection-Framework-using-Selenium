import csv
import io
import json
from flask import Blueprint, render_template, redirect, url_for, session, Response
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
    executions = fetchall(
        "SELECT * FROM executions ORDER BY started_at DESC LIMIT 100"
    )
    return render_template("reports/index.html", executions=executions)


@reports_bp.route("/export/csv")
@login_required
def export_csv():
    executions = fetchall("SELECT * FROM executions ORDER BY started_at DESC")
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Test Name", "Status", "Retries", "Duration (s)", "Browser", "Started At", "Error"])
    for e in executions:
        writer.writerow([
            e["id"],
            e["test_name"],
            e["status"],
            e["retry_count"] or 0,
            round(e["duration_seconds"] or 0, 2),
            e["browser"] or "chrome",
            e["started_at"] or "",
            (e["error_message"] or "").split("Stacktrace:")[0][:200].strip()
        ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=smartretry_report.csv"}
    )


@reports_bp.route("/export/json")
@login_required
def export_json():
    executions = fetchall("SELECT * FROM executions ORDER BY started_at DESC")
    data = []
    for e in executions:
        data.append({
            "id": e["id"],
            "test_name": e["test_name"],
            "status": e["status"],
            "retry_count": e["retry_count"] or 0,
            "duration_seconds": round(e["duration_seconds"] or 0, 2),
            "browser": e["browser"] or "chrome",
            "started_at": e["started_at"] or "",
            "error": (e["error_message"] or "").split("Stacktrace:")[0][:200].strip()
        })
    return Response(
        json.dumps({"total": len(data), "executions": data}, indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=smartretry_report.json"}
    )
