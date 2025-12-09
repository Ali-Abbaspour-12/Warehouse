from flask import Flask, render_template,render_template_string, request, redirect, url_for,Blueprint,flash,session,jsonify
from models import Personnel
import pandas as pd
from extensions import db
from flask_login import login_required
from .login import admin_required 
from werkzeug.utils import secure_filename
import os


personnel_bp = Blueprint("personnel_bp", __name__,url_prefix="/personnel")



@personnel_bp.route("/personnel")
@login_required
def personnel():
    args = request.args

    field_mapping = {
        "username": Personnel.username,
        "personnel_code": Personnel.personnel_code,
        "company": Personnel.company,
        "unit": Personnel.unit,
        "national_code": Personnel.national_code,
        "current_location": Personnel.current_location,
    }

    query = Personnel.query
    has_filter = False

    for arg_key, model_field in field_mapping.items():
        value = args.get(arg_key)
        if value:
            has_filter = True
            query = query.filter(model_field.ilike(f"%{value}%"))

    if not has_filter:
        return render_template("personnel_panel/personnel.html", personnels=[])

    # مرتب‌سازی نزولی بر اساس property_code
    personnels = query.all()

    return render_template("personnel_panel/personnel.html", personnels=personnels)
    
    

@personnel_bp.route("/add_personnel", methods=["GET", "POST"])
@admin_required
@login_required
def add_personnel():
    if request.method == 'POST':
        new_person = Personnel(
            username=request.form['username'],
            personnel_code=request.form['personnel_code'],
            company=request.form['company'],
            unit=request.form['unit'],
            national_code=request.form['national_code'],
            current_location=request.form['current_location']
        )
        db.session.add(new_person)
        db.session.commit()
        flash('پرسنل جدید با موفقیت اضافه شد.', 'success')
        return redirect(url_for('personnel_bp.personnel'))

    return render_template('personnel_panel/add_personnel.html')


@personnel_bp.route("/edit_personnel_<int:personnel_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_personnel(personnel_id):
    person = Personnel.query.get_or_404(personnel_id)
    if request.method == 'POST':
        person.username = request.form['username']
        person.personnel_code = request.form['personnel_code']
        person.company = request.form['company']
        person.unit = request.form['unit']
        person.national_code = request.form['national_code']
        person.current_location = request.form['current_location']

        db.session.commit()
        flash('پرسنل با موفقیت ویرایش شد.', 'success')
        return redirect(url_for('personnel_bp.personnel'))

    return render_template('personnel_panel/edit_personnel.html', person=person)


@personnel_bp.route("/delete_personnel_<int:personnel_id>", methods=["GET", "POST"])
@login_required
@admin_required
def delete_personnel(personnel_id):
    personnel = Personnel.query.get_or_404(personnel_id)
    db.session.delete(personnel)
    db.session.commit()
    flash('پرسنل با موفقیت حذف شد.', 'success')
    return redirect(url_for('personnel_bp.personnel'))



@personnel_bp.route("/suggest", methods=["GET"])
@login_required
def suggest():
    args = request.args

    field = args.get("field")
    value = args.get("value", "")

    # مپ فیلدها
    field_mapping = {
        "username": Personnel.username,
        "personnel_code": Personnel.personnel_code,
        "company": Personnel.company,
        "unit": Personnel.unit,
        "national_code": Personnel.national_code,
        "current_location": Personnel.current_location,
    }

    if field not in field_mapping:
        return {"error": "invalid field"}, 400

    query = Personnel.query

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


@personnel_bp.route("/suggest_all", methods=["GET"])
@login_required
def suggest_all():
    args = request.args

    field = args.get("field")
    value = args.get("value", "")

    field_mapping = {
        "username": Personnel.username,
        "personnel_code": Personnel.personnel_code,
        "company": Personnel.company,
        "unit": Personnel.unit,
        "national_code": Personnel.national_code,
        "current_location": Personnel.current_location,
    }

    if field not in field_mapping:
        return {"error": "invalid field"}, 400

    column = field_mapping[field]

    suggestions = (
        Personnel.query.with_entities(column)
        .filter(column.isnot(None))
        .filter(column.ilike(f"%{value}%"))
        .distinct()
        .order_by(column)
        .all()
    )

    return {"suggestions": [s[0] for s in suggestions if s[0]]}


@personnel_bp.route('/show_exel_records', methods=['GET', 'POST'])
@login_required
@admin_required
def show_exel_records():
    filepath = session.get('uploaded_file')
    if not filepath or not os.path.exists(filepath):
        flash('فایل اکسل پیدا نشد. لطفا دوباره آپلود کنید.', 'danger')
        return redirect(url_for('personnel_bp.add_multy_personnel'))

    df = pd.read_excel(filepath,dtype=str)
    df.fillna('', inplace=True)
    columns = df.columns.tolist()
    data_preview = df.head(50).to_dict(orient='records')  # پیش نمایش 50 ردیف

    return render_template('personnel_panel/show_exel_records.html', columns=columns, data=data_preview)



UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@personnel_bp.route('/add_multy_personnel', methods=['GET', 'POST'])
@login_required
@admin_required
def add_multy_personnel():
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

        return redirect(url_for('personnel_bp.show_exel_records'))

    return render_template('personnel_panel/add_multy_personnel.html')


@personnel_bp.route('/add_multy_personnel_to_database', methods=['POST'])
@login_required
@admin_required
def add_multy_personnel_to_database():
    filepath = session.get('uploaded_file')
    if not filepath or not os.path.exists(filepath):
        flash('فایل اکسل پیدا نشد. لطفا دوباره آپلود کنید.', 'danger')
        return redirect(url_for('personnel_bp.add_multy_personnel'))

    df = pd.read_excel(filepath,dtype=str)

    # پر کردن تمام سلول‌های خالی با خط تیره
    df = df.fillna('-')

    db_fields = ['username', 'personnel_code', 'company', 'unit', 'national_code', 'current_location']

    # ساخت و ذخیره ردیف‌ها
    for _, row in df.iterrows():
        data = {field: row.get(field, '-') for field in db_fields}

        if data.get('username') != '-':  # حداقل شرط معتبر بودن رکورد
            person = Personnel(**data)
            db.session.add(person)

    db.session.commit()

    flash('چند پرسنل با موفقیت وارد دیتابیس شدند.', 'success')
    session.pop('uploaded_file', None)

    return redirect(url_for('personnel_bp.personnel'))



