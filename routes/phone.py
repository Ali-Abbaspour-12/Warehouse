from flask import Flask, render_template,render_template_string, request, redirect, url_for,Blueprint,flash,session,jsonify
from models import Phone
import pandas as pd
from extensions import db
from flask_login import login_required
from .login import admin_required 
from werkzeug.utils import secure_filename
import os


phone_bp = Blueprint("phone_bp", __name__,url_prefix="/phone")



@phone_bp.route("/phone")
@login_required
def phone():
    args = request.args

    field_mapping = {
        "username": Phone.username,
        "place":Phone.place,
        "phone_number":Phone.phone_number,
        "pre_phone_number":Phone.pre_phone_number

    }

    query = Phone.query
    has_filter = False

    for arg_key, model_field in field_mapping.items():
        value = args.get(arg_key)
        if value:
            has_filter = True
            query = query.filter(model_field.ilike(f"%{value}%"))

    if not has_filter:
        return render_template("phone_panel/phone.html", phones=[])

    # مرتب‌سازی نزولی بر اساس property_code
    phones = query.order_by(Phone.phone_number.desc()).all()

    return render_template("phone_panel/phone.html", phones=phones)
    
    

@phone_bp.route("/add_phone", methods=["GET", "POST"])
@login_required
def add_phone():
    if request.method == 'POST':
        new_phone_number = Phone(
            username=request.form['username'],
            place=request.form['place'],
            phone_number=request.form['phone_number'],
            pre_phone_number=request.form['pre_phone_number']
        )
        db.session.add(new_phone_number)
        db.session.commit()
        flash('شماره تلفن جدید با موفقیت اضافه شد.', 'success')
        return redirect(url_for('phone_bp.phone'))

    return render_template('phone_panel/add_phone.html')


@phone_bp.route("/edit_phone_<int:id>", methods=["GET", "POST"])
@login_required
def edit_phone(id):
    phone = Phone.query.get_or_404(id)
    if request.method == 'POST':
        Phone.username = request.form['username']
        Phone.place = request.form['place']
        Phone.phone_number = request.form['phone_number']
        Phone.pre_phone_number = request.form['pre_phone_number']

        db.session.commit()
        flash('شماره تلفن با موفقیت ویرایش شد.', 'success')
        return redirect(url_for('phone_bp.phone'))

    return render_template('phone_panel/edit_phone.html', phone=phone)


@phone_bp.route("/delete_phone_<int:id>", methods=["GET", "POST"])
@login_required
def delete_phone(id):
    phone = Phone.query.get_or_404(id)
    db.session.delete(phone)
    db.session.commit()
    flash('شماره تلفن با موفقیت حذف شد.', 'success')
    return redirect(url_for('phone_bp.phone'))



@phone_bp.route("/suggest", methods=["GET"])
@login_required
def suggest():
    args = request.args

    field = args.get("field")
    value = args.get("value", "")

    # مپ فیلدها
    field_mapping = {
        "username": Phone.username,
        "place": Phone.place,
        "phone_number": Phone.phone_number,
        "pre_phone_number": Phone.pre_phone_number,
    }

    if field not in field_mapping:
        return {"error": "invalid field"}, 400

    query = Phone.query

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


@phone_bp.route("/suggest_all", methods=["GET"])
@login_required
def suggest_all():
    args = request.args

    field = args.get("field")
    value = args.get("value", "")

    field_mapping = {
        "username": Phone.username,
        "place": Phone.place,
        "phone_number": Phone.phone_number,
        "pre_phone_number": Phone.pre_phone_number,
    }

    if field not in field_mapping:
        return {"error": "invalid field"}, 400

    column = field_mapping[field]

    suggestions = (
        Phone.query.with_entities(column)
        .filter(column.isnot(None))
        .filter(column.ilike(f"%{value}%"))
        .distinct()
        .order_by(column)
        .all()
    )

    return {"suggestions": [s[0] for s in suggestions if s[0]]}


@phone_bp.route('/show_exel_records', methods=['GET', 'POST'])
@login_required
def show_exel_records():
    filepath = session.get('uploaded_file')
    if not filepath or not os.path.exists(filepath):
        flash('فایل اکسل پیدا نشد. لطفا دوباره آپلود کنید.', 'danger')
        return redirect(url_for('phone_bp.add_multy_phone'))

    df = pd.read_excel(filepath,dtype=str)
    df.fillna('', inplace=True)
    columns = df.columns.tolist()
    data_preview = df.head(50).to_dict(orient='records')  # پیش نمایش 50 ردیف

    return render_template('phone_panel/show_exel_records.html', columns=columns, data=data_preview)



UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@phone_bp.route('/add_multy_phone', methods=['GET', 'POST'])
@login_required
def add_multy_phone():
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

        return redirect(url_for('phone_bp.show_exel_records'))

    return render_template('phone_panel/add_multy_phone.html')


@phone_bp.route('/add_multy_phone_to_database', methods=['POST'])
@login_required
def add_multy_phone_to_database():
    filepath = session.get('uploaded_file')
    if not filepath or not os.path.exists(filepath):
        flash('فایل اکسل پیدا نشد. لطفا دوباره آپلود کنید.', 'danger')
        return redirect(url_for('phone_bp.add_multy_phone'))

    df = pd.read_excel(filepath , dtype=str)

    # پر کردن تمام سلول‌های خالی با خط تیره
    df = df.fillna('-')

    db_fields = ['username', 'place', 'phone_number', 'pre_phone_number']

    # ساخت و ذخیره ردیف‌ها
    for _, row in df.iterrows():
        data = {field: row.get(field, '-') for field in db_fields}

        if data.get('username') != '-':  # حداقل شرط معتبر بودن رکورد
            phone = Phone(**data)
            db.session.add(phone)

    db.session.commit()

    flash('چند شماره تلفن با موفقیت وارد دیتابیس شدند.', 'success')
    session.pop('uploaded_file', None)

    return redirect(url_for('phone_bp.phone'))



