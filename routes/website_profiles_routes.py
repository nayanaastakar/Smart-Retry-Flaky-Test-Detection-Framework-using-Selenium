from flask import Blueprint, render_template, redirect, url_for, session
from database.db_manager import fetchall
website_profiles_bp = Blueprint("website_profiles", __name__, url_prefix="/website-profiles")
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated
@website_profiles_bp.route("/")
@login_required
def index():
    profiles = fetchall("SELECT * FROM website_profiles ORDER BY created_at DESC")
    return render_template("website_profiles/index.html", profiles=profiles)
