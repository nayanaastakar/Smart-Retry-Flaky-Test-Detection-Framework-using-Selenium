from flask import Blueprint, jsonify, request, session
from database.db_manager import fetchall, fetchone, execute
api_bp = Blueprint("api", __name__)

@api_bp.route("/executions")
def executions():
    rows = fetchall("SELECT * FROM executions ORDER BY started_at DESC LIMIT 50")
    return jsonify([dict(r) for r in rows])

@api_bp.route("/projects")
def projects():
    rows = fetchall("SELECT * FROM projects ORDER BY created_at DESC")
    return jsonify([dict(r) for r in rows])

@api_bp.route("/stats")
def stats():
    return jsonify({
        "total": fetchone("SELECT COUNT(*) as c FROM executions")["c"],
        "passed": fetchone("SELECT COUNT(*) as c FROM executions WHERE status='pass'")["c"],
        "failed": fetchone("SELECT COUNT(*) as c FROM executions WHERE status='fail'")["c"],
        "flaky": fetchone("SELECT COUNT(*) as c FROM executions WHERE status='flaky'")["c"],
    })
