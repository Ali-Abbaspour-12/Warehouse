from flask import render_template,redirect,request,url_for,Blueprint,send_file
from models import Item
from extensions import db
from openpyxl import load_workbook
from openpyxl.styles import Alignment
import pandas as pd
from .login import admin_required

report_bp = Blueprint("report_bp",__name__,url_prefix="/report")



@report_bp.route('/export_report')
def export_report():
    items = Item.query.all()

    data = [{
        "project_code": i.project_code,
        "warehouse_location": i.warehouse_location,
        "row": i.row,
        "user": i.user,
        "company": i.company,
        "unit": i.unit,
        "personnel_code": i.personnel_code,
        "current_location": i.current_location,
        "system_identification_code": i.system_identification_code,
        "category": i.category,
        "model": i.model,
        "serial_number": i.serial_number,
        "property_code": i.property_code,
        "recipient_delivery": i.recipient_delivery,
        "description": i.description,
        "closed": i.closed,
        "closed_time": i.closed_time,
    } for i in items]

    df = pd.DataFrame(data)

    file_path = "export.xlsx"
    df.to_excel(file_path, index=False, engine="openpyxl")

    wb = load_workbook(file_path)
    ws = wb.active
    
    # 1) صفحه راست به چپ
    ws.sheet_view.rightToLeft = True

    # 2) وسط‌چین بودن تمام سلول‌ها
    center_alignment = Alignment(horizontal="center", vertical="center")
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = center_alignment

    # 3) تنظیم خودکار عرض ستون‌ها
    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter

        for cell in col:
            try:
                value_length = len(str(cell.value))
                if value_length > max_length:
                    max_length = value_length
            except:
                pass

        # کمی فاصله اضافه می‌کنیم که خفه نشود
        ws.column_dimensions[col_letter].width = max_length + 3

    wb.save(file_path)

    return send_file(file_path, as_attachment=True)





@report_bp.route("/report")
def report():
    args = request.args

    field_mapping = {
        "property_code": Item.property_code,
        "project_code": Item.project_code,
        "warehouse_location": Item.warehouse_location,
        "row": Item.row,
        "user": Item.user,
        "company": Item.company,
        "category": Item.category,
        "personnel_code": Item.personnel_code,
        "current_location": Item.current_location,
        "system_identification_code": Item.system_identification_code,
        "model": Item.model,
        "serial_number": Item.serial_number,
        "recipient_delivery": Item.recipient_delivery,
        "closed": Item.closed
    }

    query = Item.query
    has_filter = False

    # ---- اعمال فیلترهای فرم ----
    for arg_key, model_field in field_mapping.items():
        value = args.get(arg_key)
        if value:
            has_filter = True
            query = query.filter(model_field.ilike(f"%{value}%"))

    if not has_filter:
        return render_template("report_panel/report.html", 
                               items=[],
                               group_data=None,
                               group_field=None)

    # ---- گروه‌بندی ----
    group_field = args.get("group_field")
    group_data = None

    if group_field in field_mapping:
        column = field_mapping[group_field]
        group_data = (
            query.with_entities(column.label("field"), db.func.count().label("cnt"))
                 .group_by(column)
                 .order_by(db.func.count().desc())
                 .all()
        )

    # ---- نتایج لیستی ----
    items = query.order_by(Item.property_code.desc()).all()

    return render_template("report_panel/report.html",
                           items=items,
                           group_data=group_data,
                           group_field=group_field)




@report_bp.route("/suggest", methods=["GET"])
def suggest():
    args = request.args

    field = args.get("field")
    value = args.get("value", "")

    field_mapping = {
       "property_code": Item.property_code,
        "project_code": Item.project_code,
        "warehouse_location":Item.warehouse_location,
        "row":Item.row,
        "user": Item.user,
        "company": Item.company,
        "category": Item.category,
        "personnel_code":Item.personnel_code,
        "current_location":Item.current_location,
        "system_identification_code":Item.system_identification_code,
        "model":Item.model,
        "serial_number":Item.serial_number,
        "recipient_delivery":Item.recipient_delivery,
        "closed":Item.closed
    }

    if field not in field_mapping:
        return {"error": "invalid field"}, 400

    query = Item.query

    # اعمال فیلتر برای فیلدهای دیگر
    for key, column in field_mapping.items():
        if key != field:
            v = args.get(key)
            if v:
                query = query.filter(column.ilike(f"%{v}%"))

    # دریافت همه مقادیر
    suggestions = (
        query.with_entities(field_mapping[field])
        .distinct()
        .filter(field_mapping[field].ilike(f"%{value}%"))
        .order_by(field_mapping[field])
        
        .all()
    )

    return {"suggestions": [s[0] for s in suggestions if s[0]]}