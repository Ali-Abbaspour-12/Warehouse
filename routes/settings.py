from flask import redirect,render_template,flash,Blueprint,url_for
from models import Item,ItemHistory
from extensions import db
from .login import admin_required
from flask_login import login_required
from sqlalchemy import inspect,text
from extensions import db




settings_bp = Blueprint("settings_bp", __name__)


def get_all_tables():
    return db.metadata.tables.keys()


@settings_bp.route("/settings")
@admin_required
@login_required
def settings():
    # گرفتن نام تمام جداول
    tables = list(db.metadata.tables.keys())

    # تعداد رکوردهای هر جدول
    table_info = []
    for table_name in tables:
        count = db.session.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
        table_info.append({"name": table_name, "count": count})

    return render_template("settings_panel/settings.html", tables=table_info)


@settings_bp.route("/delete_records/<table_name>")
@admin_required
@login_required
def delete_records(table_name):
    try:
        db.session.execute(text(f"DELETE FROM {table_name}"))
        db.session.commit()
        flash(f"تمام رکوردهای جدول {table_name} حذف شد", "success")
    except Exception as e:
        flash(f"خطا در حذف رکوردها: {e}", "danger")

    return redirect(url_for("settings_bp.settings"))



@settings_bp.route("/drop_table/<table_name>")
@admin_required
@login_required
def drop_table(table_name):
    try:
        db.session.execute(text(f"DROP TABLE {table_name}"))
        db.session.commit()
        flash(f"جدول {table_name} حذف شد", "success")
    except Exception as e:
        flash(f"خطا در حذف جدول: {e}", "danger")

    return redirect(url_for("settings_bp.settings"))