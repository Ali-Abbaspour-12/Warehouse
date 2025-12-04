from flask import Blueprint, render_template,request,redirect,url_for,flash,session
from models import Item,ItemHistory,Repair,ItemLog
from extensions import db
from .login import admin_required
from flask_login import login_required
from werkzeug.utils import secure_filename
import os
import pandas as pd
from sqlalchemy import event
import json,os


item_bp = Blueprint("item_bp", __name__,url_prefix="/item")


def log_item_change(item_data):
    # حذف کلیدهایی که در ItemLog وجود ندارند
    allowed_fields = {c.name for c in ItemLog.__table__.columns}
    filtered_data = {k: v for k, v in item_data.items() if k in allowed_fields}

    # ایجاد لاگ جدید
    new_log = ItemLog(**filtered_data)
    db.session.add(new_log)
    db.session.commit()

    # محدود کردن تعداد لاگ‌ها به 50
    total_logs = ItemLog.query.count()
    if total_logs > 50:
        logs_to_delete = ItemLog.query.order_by(ItemLog.id).limit(total_logs - 50).all()
        for log in logs_to_delete:
            db.session.delete(log)
        db.session.commit()



@item_bp.route("/show_latest_changes")
def show_latest_changes():
    logs = ItemLog.query.order_by(ItemLog.id.desc()).limit(50).all()
    return render_template("item_panel/show_latest_changes.html", logs=logs)





@item_bp.route("/item")
@login_required
def item():
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
        "closed": Item.closed,
        "description":Item.description,
        "unit":Item.unit,
        "closed_time":Item.closed_time

    }

    query = Item.query
    has_filter = False

    for arg_key, model_field in field_mapping.items():
        value = args.get(arg_key)
        if value:
            has_filter = True
            query = query.filter(model_field.ilike(f"%{value}%"))

    if not has_filter:
        return render_template("item_panel/item.html", items=[])

    # مرتب‌سازی نزولی بر اساس property_code
    items = query.order_by(Item.property_code.desc()).all()

    return render_template("item_panel/item.html", items=items)


   

@item_bp.route("/show_all_records")
@login_required
def show_all_records():
    items = Item.query.all()
    return render_template("item_panel/show_all_records.html",items=items)


@item_bp.route('/item_detail_<int:item_id>')
@login_required
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)

    return render_template('item_panel/item_detail.html',item=item)



@item_bp.route('/history_detail_<int:item_id>_<int:history_id>')
@admin_required
@login_required
def history_detail(item_id,history_id):
    history = ItemHistory.query.get_or_404(history_id)
    return render_template('item_panel/history_detail.html',history=history,item_id=item_id)

@item_bp.route('/delete_history_<int:item_id>_<int:history_id>')
@login_required
@admin_required
def delete_history(item_id, history_id):

    history = ItemHistory.query.get_or_404(history_id)

    db.session.delete(history)
    db.session.commit()

    flash("رکورد تاریخچه با موفقیت حذف شد!", "success")

    return redirect(url_for("item_bp.item_detail", item_id=item_id))




@item_bp.route('/edit_item_<int:item_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)

    if request.method == "POST":
        # --- آپدیت فیلدها ---
        for field in [
            "project_code","warehouse_location","row","user","company","unit",
            "personnel_code","current_location","system_identification_code",
            "category","model","serial_number","property_code",
            "recipient_delivery","closed","description","closed_time"
        ]:
            setattr(item, field, request.form.get(field))

        db.session.commit()  # commit بعد از اعمال تغییرات

        # --- لاگ نسخه جدید آیتم ---
        # بعد از commit کردن تغییرات
        new_data = {field: getattr(item, field) for field in [
            "project_code","warehouse_location","row","user","company","unit",
            "personnel_code","current_location","system_identification_code",
            "category","model","serial_number","property_code",
            "recipient_delivery","closed","description","closed_time"
        ]}
        log_item_change(new_data)


        flash("آیتم با موفقیت ویرایش شد!", "success")
        return redirect(url_for("item_bp.item_detail", item_id=item.id))

    return render_template("item_panel/edit_item.html", item=item)








@item_bp.route("/add_item", methods=['GET', 'POST'])
@login_required
@admin_required
def add_item():
    if request.method == 'POST':
        record = Item(
            project_code=request.form.get('project_code'),
            warehouse_location=request.form.get('warehouse_location'),
            row=request.form.get('row'),
            user=request.form.get('user'),
            company=request.form.get('company'),
            unit=request.form.get('unit'),
            personnel_code=request.form.get('personnel_code'),
            current_location=request.form.get('current_location'),
            system_identification_code=request.form.get('system_identification_code'),
            category=request.form.get('category'),
            model=request.form.get('model'),
            serial_number=request.form.get('serial_number'),
            property_code=request.form.get('property_code'),
            recipient_delivery=request.form.get('recipient_delivery'),
            description=request.form.get('description'),
            closed=request.form.get('closed'),
            closed_time=request.form.get('closed_time'),
        )
        db.session.add(record)
        db.session.commit()  # commit برای داشتن id

        # --- لاگ نسخه جدید ---
        new_data = {field: getattr(item, field) for field in [
            "project_code","warehouse_location","row","user","company","unit",
            "personnel_code","current_location","system_identification_code",
            "category","model","serial_number","property_code",
            "recipient_delivery","closed","description","closed_time"
        ]}
        log_item_change(new_data)

        flash("آیتم با موفقیت اضافه شد!", "success")
        return redirect(url_for("item_bp.item"))

    return render_template("item_panel/add_item.html")




@item_bp.route("/excel_import/show_records", methods=["POST"])
@login_required
@admin_required
def show_records():
    file = request.files.get("excel_file")

    if not file or file.filename == "":
        flash("لطفاً یک فایل اکسل انتخاب کنید!", "danger")
        return redirect(url_for("item_bp.excel_import"))

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

    return render_template("item_panel/show_records.html", records=records)

@item_bp.route('/excel_import')
@login_required
@admin_required
def excel_import():
    return render_template('item_panel/excel_import.html')



@item_bp.route("/excel_import/import_to_database", methods=["POST"])
@login_required
@admin_required
def import_to_database():

    filename = session.get("uploaded_excel")

    if not filename:
        flash("هیچ فایلی برای وارد کردن یافت نشد!", "danger")
        return redirect(url_for("item_bp.excel_import"))

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
    return redirect(url_for("item_bp.excel_import"))



@item_bp.route("/repair_item", methods=["GET"])
@login_required
def repair_item():
    repairs = Repair.query.all()
    return render_template("item_panel/repair/repair_item.html", repairs=repairs)


@item_bp.route("/add_repair_item", methods=["GET", "POST"])
@login_required
@admin_required
def add_repair_item():
    if request.method == "POST":
        new_repair = Repair(
            device_type=request.form['device_type'],
            model=request.form['model'],
            serial_number=request.form['serial_number'],
            property_code=request.form['property_code'],
            description=request.form['description'],
            status=request.form['status'],
            current_location=request.form['current_location']
        )

        db.session.add(new_repair)
        db.session.commit()
        return redirect(url_for("item_bp.repair_item"))

    return render_template("item_panel/repair/add_repair_item.html")


@item_bp.route("/edit_repair_item_<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_repair_item(id):
    repair = Repair.query.get_or_404(id)

    if request.method == "POST":
        repair.device_type = request.form['device_type']
        repair.model = request.form['model']
        repair.serial_number = request.form['serial_number']
        repair.property_code = request.form['property_code']
        repair.description = request.form['description']
        repair.status = request.form['status']
        repair.current_location = request.form['current_location']

        db.session.commit()
        return redirect(url_for("item_bp.repair_item"))

    return render_template("item_panel/repair/edit_repair_item.html", repair=repair)


@item_bp.route("/delete_repair_item_<int:id>", methods=["POST"])
@login_required
@admin_required
def delete_repair_item(id):
    repair = Repair.query.get_or_404(id)
    db.session.delete(repair)
    db.session.commit()
    return redirect(url_for("item_bp.repair_item"))





@item_bp.route("/suggest", methods=["GET"])
@login_required
def suggest():
    args = request.args

    field = args.get("field")
    value = args.get("value", "")

    # مپ فیلدها
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
        "closed": Item.closed,
        "description":Item.description,
        "unit":Item.unit,
        "closed_time":Item.closed_time
    }

    if field not in field_mapping:
        return {"error": "invalid field"}, 400

    query = Item.query

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


@item_bp.route("/suggest_all", methods=["GET"])
@login_required
def suggest_all():
    args = request.args

    field = args.get("field")
    value = args.get("value", "")

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
        "closed": Item.closed,
        "description":Item.description,
        "unit":Item.unit,
        "closed_time":Item.closed_time
    }

    if field not in field_mapping:
        return {"error": "invalid field"}, 400

    column = field_mapping[field]

    suggestions = (
        Item.query.with_entities(column)
        .filter(column.isnot(None))
        .filter(column.ilike(f"%{value}%"))
        .distinct()
        .order_by(column)
        .all()
    )

    return {"suggestions": [s[0] for s in suggestions if s[0]]}