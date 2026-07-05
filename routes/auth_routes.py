from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import hashlib
from database.db_manager import fetchone, execute
from datetime import datetime

auth_bp = Blueprint("auth", __name__)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = fetchone("SELECT * FROM users WHERE username=?", (username,))
        if user and user["password_hash"] == hash_password(password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            execute("UPDATE users SET last_login=? WHERE id=?", (datetime.utcnow().isoformat(), user["id"]))
            return redirect(url_for("dashboard.index"))
        flash("Invalid credentials", "error")
    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
