from flask import redirect,render_template,flash,Blueprint,url_for
from models import Item,ItemHistory
from extensions import db
from .login import admin_required
from flask_login import login_required

settings_bp = Blueprint("settings_bp", __name__)


@settings_bp.route("/settings")
@admin_required
@login_required
def settings():
    return render_template("settings_panel/settings.html")



@settings_bp.route("/delete_all_records")
@admin_required
@login_required
def delete_all_records():
    Item.query.delete()
    ItemHistory.query.delete()
    db.session.commit()
    flash("همه ریکورد ها حذف شدند","success")
    return redirect(url_for("settings_bp.settings"))
