from flask import redirect,render_template,flash,Blueprint,url_for
from models import db,Item

settings_bp = Blueprint("settings_bp", __name__)


@settings_bp.route("/settings")
def settings():
    return render_template("settings_panel/settings.html")



@settings_bp.route("/delete_all_records")
def delete_all_records():
    Item.query.delete()
    db.session.commit()
    flash("همه ریکورد ها حذف شدند","success")
    return redirect(url_for("settings_bp.settings"))
