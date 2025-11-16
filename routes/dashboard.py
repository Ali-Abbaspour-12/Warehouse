from flask import Blueprint, render_template
from flask_login import login_required
from .login import admin_required


dashboard_bp = Blueprint("dashboard_bp", __name__)

@dashboard_bp.route("/")
@login_required
def dashboard():
    return render_template("dashboard_panel/dashboard.html")
