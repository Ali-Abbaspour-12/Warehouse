from flask import render_template,redirect,request,url_for,Blueprint,send_file
from models import Item,db
from openpyxl import load_workbook
from openpyxl.styles import Alignment
import pandas as pd

report_bp = Blueprint("report_bp",__name__)



@report_bp.route('/export_report')
def export_report():
    items = Item.query.all()

    data = [{
        "project_code": i.project_code,
        "warehouse_location": i.warehouse_location,
        "row": i.row,
        "first_recipient_delivery": i.first_recipient_delivery,
        "company": i.company,
        "unit": i.unit,
        "personnel_code": i.personnel_code,
        "current_location": i.current_location,
        "system_identification_code": i.system_identification_code,
        "category": i.category,
        "model": i.model,
        "serial_number": i.serial_number,
        "property_code": i.property_code,
        "second_recipient_delivery": i.second_recipient_delivery,
        "third_recipient_delivery": i.third_recipient_delivery,
        "forth_recipient_delivery": i.forth_recipient_delivery,
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
    query_params_exist = any([
        request.args.get('q'),
        request.args.get('project_code'),
        request.args.get('company'),
        request.args.get('warehouse_locaiton'),
        request.args.get('category'),
    ])


    if not query_params_exist:
        return render_template('report.html',items=[])

    query = Item.query

    search = request.args.get("q")
    if search:
        query = query.filter(Item.property_code.ilike(f"%{search}%"))


    project_code = request.args.get("project_code")
    if project_code:
        query = query.filter(Item.project_code.ilike(f'%{project_code}%'))

    persian_equal = {}
    company = request.args.get("company") 
    if company:
        query = query.filter(Item.company.ilike(f'%{company}%'))


    category = request.args.get("category") 
    if category:
        query = query.filter(Item.category.ilike(f'%{category}%'))  



    warehouse_location = request.args.get("warehouse_location") 
    if warehouse_location:
        query = query.filter(Item.warehouse_location.ilike(f'%{warehouse_location}%')) 


        

    items = query.all()

    return render_template("report.html",items=items)
    