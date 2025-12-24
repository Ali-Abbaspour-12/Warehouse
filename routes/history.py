from flask import Blueprint, render_template,request,redirect,url_for,flash,session
from models import ItemHistory
from extensions import db
from .login import admin_required
from flask_login import login_required
from werkzeug.utils import secure_filename
import os
import pandas as pd
from sqlalchemy import event
import json,os


history_bp = Blueprint("history_bp", __name__,url_prefix="/history")



@history_bp.route("/history")
@login_required
def history():
    args = request.args

    field_mapping = {
        "property_code": ItemHistory.property_code,
        "project_code": ItemHistory.project_code,
        "warehouse_location": ItemHistory.warehouse_location,
        "row": ItemHistory.row,
        "user": ItemHistory.user,
        "company": ItemHistory.company,
        "category": ItemHistory.category,
        "personnel_code": ItemHistory.personnel_code,
        "current_location": ItemHistory.current_location,
        "system_identification_code": ItemHistory.system_identification_code,
        "model": ItemHistory.model,
        "serial_number": ItemHistory.serial_number,
        "recipient_delivery": ItemHistory.recipient_delivery,
        "closed": ItemHistory.closed,
        "description":ItemHistory.description,
        "unit":ItemHistory.unit,
        "closed_time":ItemHistory.closed_time

    }

    query = ItemHistory.query
    has_filter = False

    for arg_key, model_field in field_mapping.items():
        value = args.get(arg_key)
        if value:
            has_filter = True
            query = query.filter(model_field.ilike(f"%{value}%"))

    if not has_filter:
        return render_template("item_panel/history/history.html", items=[])

    # مرتب‌سازی نزولی بر اساس property_code
    histories = query.order_by(ItemHistory.property_code.desc()).all()

    return render_template("item_panel/history/history.html", histories=histories)



@history_bp.route("/suggest", methods=["GET"])
@login_required
def suggest():
    args = request.args

    field = args.get("field")
    value = args.get("value", "")

    # مپ فیلدها
    field_mapping = {
        "property_code": ItemHistory.property_code,
        "project_code": ItemHistory.project_code,
        "warehouse_location": ItemHistory.warehouse_location,
        "row": ItemHistory.row,
        "user": ItemHistory.user,
        "company": ItemHistory.company,
        "category": ItemHistory.category,
        "personnel_code": ItemHistory.personnel_code,
        "current_location": ItemHistory.current_location,
        "system_identification_code": ItemHistory.system_identification_code,
        "model": ItemHistory.model,
        "serial_number": ItemHistory.serial_number,
        "recipient_delivery": ItemHistory.recipient_delivery,
        "closed": ItemHistory.closed,
        "description":ItemHistory.description,
        "unit":ItemHistory.unit,
        "closed_time":ItemHistory.closed_time
    }

    if field not in field_mapping:
        return {"error": "invalid field"}, 400

    query = ItemHistory.query

    # فیلتر سایر فیلدها
    for key, column in field_mapping.items():
        if key == field:
            continue
        v = args.get(key)
        if v:
            query = query.filter(column.ilike(f"%{v}%"))

    # دریافت پیشنهادات
    suggestions = (
        query.with_entities(field_mapping[field])
        .filter(field_mapping[field].ilike(f"%{value}%"))
        .distinct()
        .order_by(field_mapping[field])
        .all()
    )

    return {"suggestions": [s[0] for s in suggestions if s[0]]}


@history_bp.route("/suggest_all", methods=["GET"])
@login_required
def suggest_all():
    args = request.args

    field = args.get("field")
    value = args.get("value", "")

    field_mapping = {
        "property_code": ItemHistory.property_code,
        "project_code": ItemHistory.project_code,
        "warehouse_location": ItemHistory.warehouse_location,
        "row": ItemHistory.row,
        "user": ItemHistory.user,
        "company": ItemHistory.company,
        "category": ItemHistory.category,
        "personnel_code": ItemHistory.personnel_code,
        "current_location": ItemHistory.current_location,
        "system_identification_code": ItemHistory.system_identification_code,
        "model": ItemHistory.model,
        "serial_number": ItemHistory.serial_number,
        "recipient_delivery": ItemHistory.recipient_delivery,
        "closed": ItemHistory.closed,
        "description":ItemHistory.description,
        "unit":ItemHistory.unit,
        "closed_time":ItemHistory.closed_time
    }

    if field not in field_mapping:
        return {"error": "invalid field"}, 400

    column = field_mapping[field]

    suggestions = (
        ItemHistory.query.with_entities(column)
        .filter(column.isnot(None))
        .filter(column.ilike(f"%{value}%"))
        .distinct()
        .order_by(column)
        .all()
    )

    return {"suggestions": [s[0] for s in suggestions if s[0]]}