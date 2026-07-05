from flask import Blueprint, render_template, redirect, url_for, session
settings_bp = Blueprint("settings", __name__, url_prefix="/settings")
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated
@settings_bp.route("/")
@login_required
def index():
    from config import settings
    return render_template("settings/index.html", settings=settings)
