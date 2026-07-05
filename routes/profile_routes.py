from flask import Blueprint, render_template, redirect, url_for, session
profile_bp = Blueprint("profile", __name__, url_prefix="/profile")
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated
@profile_bp.route("/")
@login_required
def index():
    from database.db_manager import fetchone
    user = fetchone("SELECT * FROM users WHERE id=?", (session["user_id"],))
    return render_template("profile/index.html", user=user)
