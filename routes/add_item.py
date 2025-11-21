from flask import Flask, render_template,render_template_string, request, redirect, url_for,Blueprint,flash,session
from models import Item
import pandas as pd
from extensions import db
from .login import admin_required
from flask_login import login_required
from werkzeug.utils import secure_filename
import os


add_item_bp = Blueprint("add_item_bp", __name__,url_prefix="/add_item")


@add_item_bp.route("/add_item",methods=['GET', 'POST'])
@login_required
@admin_required
def add_item():
    if request.method == 'POST':
        record = Item(

                project_code = request.form.get('project_code'),
                warehouse_location = request.form.get('warehouse_location'),
                row = request.form.get('row'),
                user = request.form.get('user'),
                company = request.form.get('company'),
                unit = request.form.get('unit'),
                personnel_code = request.form.get('personnel_code'),
                current_location = request.form.get('current_location'),
                system_identification_code = request.form.get('system_identification_code'),
                category = request.form.get('category'),
                model = request.form.get('model'),
                serial_number = request.form.get('serial_number'),
                property_code = request.form.get('property_code'),
                recipient_delivery = request.form.get('recipient_delivery'),
                description =  request.form.get('description'), 
                closed = request.form.get('closed'),
                closed_time = request.form.get('closed_time'),

        )
        db.session.add(record)
        db.session.commit()
        flash("آیتم با موفقیت اضافه شد!", "success")
        return redirect(url_for("add_item_bp.add_item"))

    return render_template("add_item_panel/add_item.html")



@add_item_bp.route("/excel_import/show_records", methods=["POST"])
@login_required
@admin_required
def show_records():
    file = request.files.get("excel_file")

    if not file or file.filename == "":
        flash("لطفاً یک فایل اکسل انتخاب کنید!", "danger")
        return redirect(url_for("add_item_bp.excel_import"))

    # ذخیره موقت
    filename = secure_filename(file.filename)
    temp_path = os.path.join("uploads", filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(temp_path)

    # خواندن فایل
    df = pd.read_excel(temp_path).astype(str)

    # ذخیره نام فایل برای مرحله بعد (import)
    session["uploaded_excel"] = filename

    # ارسال DataFrame به صفحه HTML
    records = df.to_dict(orient="records")

    return render_template("add_item_panel/show_records.html", records=records)

@add_item_bp.route('/excel_import')
@login_required
@admin_required
def excel_import():
    return render_template('add_item_panel/excel_import.html')



@add_item_bp.route("/excel_import/import_to_database", methods=["POST"])
@login_required
@admin_required
def import_to_database():

    filename = session.get("uploaded_excel")

    if not filename:
        flash("هیچ فایلی برای وارد کردن یافت نشد!", "danger")
        return redirect(url_for("add_item_bp.excel_import"))

    file_path = os.path.join("uploads", filename)

    # خواندن اکسل و تبدیل نال‌ها به خط تیره
    excelFile = pd.read_excel(file_path)
    excelFile = excelFile.fillna("-").astype(str)

    db_fields = [
        "project_code", "warehouse_location", "row", "user", "company", "unit",
        "personnel_code", "current_location", "system_identification_code",
        "category", "model", "serial_number", "property_code",
        "recipient_delivery", "description", "closed", "closed_time"
    ]

    for _, excelRow in excelFile.iterrows():

        # ساخت دیکشنری امن: اگر ستون نبود → '-'
        data = {field: excelRow.get(field, "-") for field in db_fields}

        record = Item(**data)
        db.session.add(record)

    db.session.commit()

    flash("داده‌ها با موفقیت وارد پایگاه داده شدند!", "success")
    return redirect(url_for("add_item_bp.excel_import"))




@add_item_bp.route("/suggest", methods=["GET"])
@login_required
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