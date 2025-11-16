from flask import render_template,redirect,request,url_for,Blueprint,send_file
from models import Item
from extensions import db
from openpyxl import load_workbook
from openpyxl.styles import Alignment
import pandas as pd
from .login import admin_required

report_bp = Blueprint("report_bp",__name__)



@report_bp.route('/export_report')
def export_report():
    items = Item.query.all()

    data = [{
        "project_code": i.project_code,
        #"warehouse_location": i.warehouse_location,
        #"row": i.row,
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
        "company": Item.company,
        "category": Item.category,
        "user": Item.user,
        "serial_number":Item.serial_number
    }

    query = Item.query
    has_filter = False

    for arg_key, model_field in field_mapping.items():
        value = args.get(arg_key)
        if value:
            has_filter = True
            query = query.filter(model_field.ilike(f"%{value}%"))

    if not has_filter:
        return render_template("report_panel/report.html", items=[])

    items = query.all()
    return render_template("report_panel/report.html", items=items)
