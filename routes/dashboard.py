from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func
from models import Item
from extensions import db

dashboard_bp = Blueprint("dashboard_bp", __name__)

@dashboard_bp.route("/")
@login_required
def dashboard():
    # گروه‌بندی بر اساس category
    category_data = (
        db.session.query(Item.category, func.count(Item.id))
        .group_by(Item.category)
        .all()
    )

    return render_template(
        "dashboard_panel/dashboard.html",
        category_data=category_data
    )

