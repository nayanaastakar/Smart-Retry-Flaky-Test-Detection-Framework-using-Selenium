from flask import Blueprint, render_template, redirect, url_for, session
console_bp = Blueprint("console", __name__, url_prefix="/console")
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated
@console_bp.route("/")
@login_required
def index():
    return render_template("console/index.html")
