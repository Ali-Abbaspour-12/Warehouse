from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from models import User
from flask import abort
from flask_login import current_user
from functools import wraps



login_bp = Blueprint("login_bp", __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)  # 403 Forbidden
        return f(*args, **kwargs)
    return decorated_function


@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard_bp.dashboard"))

        flash(" نام کاربری یا رمز عبور اشتباه است")
        return redirect(url_for("login_bp.login"))

    return render_template("login.html")


@login_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login_bp.login"))
