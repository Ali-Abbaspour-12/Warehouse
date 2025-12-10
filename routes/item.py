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

        # --- 1) ذخیره داده‌های قدیمی ---
        old_data = {field: getattr(item, field) for field in [
            "project_code","warehouse_location","row","user","company","unit",
            "personnel_code","current_location","system_identification_code",
            "category","model","serial_number","property_code",
            "recipient_delivery","closed","description","closed_time"
        ]}

        # --- 2) ذخیره نسخه قدیمی در ItemHistory ---
        history = ItemHistory(
            item_id=item.id,
            **old_data
        )
        db.session.add(history)

        # --- 3) اعمال تغییرات جدید روی آیتم ---
        for field in old_data.keys():
            setattr(item, field, request.form.get(field))

        # --- 4) ذخیره در دیتابیس ---
        db.session.commit()

        # --- 5) لاگ‌گذاری نسخه جدید مثل add_item ---
        new_data = {field: getattr(item, field) for field in old_data.keys()}
        log_item_change(new_data)  # <-- این اضافه شده

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
        new_data = {field: getattr(record, field) for field in [
            "project_code","warehouse_location","row","user","company","unit",
            "personnel_code","current_location","system_identification_code",
            "category","model","serial_number","property_code",
            "recipient_delivery","closed","description","closed_time"
        ]}
        log_item_change(new_data)

        flash("آیتم با موفقیت اضافه شد!", "success")
        return redirect(url_for("item_bp.item"))

    return render_template("item_panel/add_item.html")




@item_bp.route('/show_exel_records', methods=['GET', 'POST'])
@login_required
@admin_required
def show_exel_records():
    filepath = session.get('uploaded_file')
    if not filepath or not os.path.exists(filepath):
        flash('فایل اکسل پیدا نشد. لطفا دوباره آپلود کنید.', 'danger')
        return redirect(url_for('item_bp.add_multy_item'))

    df = pd.read_excel(filepath,dtype=str)
    df.fillna('', inplace=True)
    columns = df.columns.tolist()
    data_preview = df.to_dict(orient='records')  # پیش نمایش 50 ردیف

    return render_template('item_panel/show_exel_records.html', columns=columns, data=data_preview)



UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@item_bp.route('/add_multy_item', methods=['GET', 'POST'])
@login_required
def add_multy_item():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            flash('لطفا یک فایل اکسل انتخاب کنید.', 'danger')
            return redirect(request.url)
        if not allowed_file(file.filename):
            flash('فرمت فایل باید اکسل باشد.', 'danger')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # ذخیره مسیر فایل در session برای استفاده در مراحل بعد
        session['uploaded_file'] = filepath

        return redirect(url_for('item_bp.show_exel_records'))

    return render_template('item_panel/add_multy_item.html')


@item_bp.route('/add_multy_item_to_database', methods=['POST'])
@login_required
def add_multy_item_to_database():
    filepath = session.get('uploaded_file')
    if not filepath or not os.path.exists(filepath):
        flash('فایل اکسل پیدا نشد. لطفا دوباره آپلود کنید.', 'danger')
        return redirect(url_for('item_bp.add_multy_item'))

    df = pd.read_excel(filepath , dtype=str)

    # پر کردن تمام سلول‌های خالی با خط تیره
    df = df.fillna('-')

    db_fields = ['project_code','warehouse_location','row','user','company','unit','personnel_code',
                 'current_location','system_identification_code','category','model','serial_number','property_code',
                 'recipient_delivery','description','closed','closed_time']

    # ساخت و ذخیره ردیف‌ها
    for _, row in df.iterrows():
        data = {field: row.get(field, '-') for field in db_fields}

        if data.get('username') != '-':  # حداقل شرط معتبر بودن رکورد
            item = Item(**data)
            db.session.add(item)

    db.session.commit()

    flash('چند شماره تلفن با موفقیت وارد دیتابیس شدند.', 'success')
    session.pop('uploaded_file', None)

    return redirect(url_for('item_bp.item'))





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




@item_bp.route('/show_exel_records_repair', methods=['GET', 'POST'])
@login_required
@admin_required
def show_exel_records_repair():
    filepath = session.get('uploaded_file')
    if not filepath or not os.path.exists(filepath):
        flash('فایل اکسل پیدا نشد. لطفا دوباره آپلود کنید.', 'danger')
        return redirect(url_for('item_bp.add_multy_repair_item'))

    df = pd.read_excel(filepath,dtype=str)
    df.fillna('', inplace=True)
    columns = df.columns.tolist()
    data_preview = df.to_dict(orient='records')  # پیش نمایش 50 ردیف

    return render_template('item_panel/repair/show_exel_records_repair.html', columns=columns, data=data_preview)



UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@item_bp.route('/add_multy_repair_item', methods=['GET', 'POST'])
@login_required
def add_multy_repair_item():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            flash('لطفا یک فایل اکسل انتخاب کنید.', 'danger')
            return redirect(request.url)
        if not allowed_file(file.filename):
            flash('فرمت فایل باید اکسل باشد.', 'danger')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # ذخیره مسیر فایل در session برای استفاده در مراحل بعد
        session['uploaded_file'] = filepath

        return redirect(url_for('item_bp.show_exel_records_repair'))

    return render_template('item_panel/repair/add_multy_repair_item.html')


@item_bp.route('/add_multy_repair_item_to_database', methods=['POST'])
@login_required
def add_multy_repair_item_to_database():
    filepath = session.get('uploaded_file')
    if not filepath or not os.path.exists(filepath):
        flash('فایل اکسل پیدا نشد. لطفا دوباره آپلود کنید.', 'danger')
        return redirect(url_for('item_bp.add_multy_repair_item'))

    df = pd.read_excel(filepath , dtype=str)

    # پر کردن تمام سلول‌های خالی با خط تیره
    df = df.fillna('-')

    db_fields = ['device_type','model','serial_number','property_code','description','status','current_location']

    # ساخت و ذخیره ردیف‌ها
    for _, row in df.iterrows():
        data = {field: row.get(field, '-') for field in db_fields}

        if data.get('username') != '-':  # حداقل شرط معتبر بودن رکورد
            repair_item = Repair(**data)
            db.session.add(repair_item)

    db.session.commit()

    flash('چند شماره تلفن با موفقیت وارد دیتابیس شدند.', 'success')
    session.pop('uploaded_file', None)

    return redirect(url_for('item_bp.repair_item'))






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