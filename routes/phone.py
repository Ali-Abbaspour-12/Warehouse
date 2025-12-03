from flask import Flask, render_template,render_template_string, request, redirect, url_for,Blueprint,flash,session,jsonify
from models import Phone
import pandas as pd
from extensions import db
from flask_login import login_required
from .login import admin_required 
from werkzeug.utils import secure_filename
import os


phone_bp = Blueprint("phone_bp", __name__,url_prefix="/phone")



@phone_bp.route("/phone", methods=["GET", "POST"])
@login_required
def phone():
    query = request.args.get("q", "").strip()

    results = []
    if query:
        results = Phone.query.filter(
            (Phone.username.ilike(f"%{query}%")) |
            (Phone.project.ilike(f"%{query}%")) |
            (Phone.phone_number.ilike(f"%{query}%")) |
            (Phone.pre_phone_number.ilike(f"%{query}%"))
        ).all()

    return render_template("phone_panel/phone.html", results=results, query=query)
    
    

@phone_bp.route("/add_phone", methods=["GET", "POST"])
@admin_required
@login_required
def add_phone():
    if request.method == 'POST':
        new_phone_number = Phone(
            username=request.form['username'],
            project=request.form['project'],
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
@admin_required
def edit_phone(id):
    phone = Phone.query.get_or_404(id)
    if request.method == 'POST':
        Phone.username = request.form['username']
        Phone.project = request.form['project']
        Phone.phone_number = request.form['phone_number']
        Phone.pre_phone_number = request.form['pre_phone_number']

        db.session.commit()
        flash('شماره تلفن با موفقیت ویرایش شد.', 'success')
        return redirect(url_for('phone_bp.phone'))

    return render_template('phone_panel/edit_phone.html', phone=phone)


@phone_bp.route("/delete_phone_<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def delete_phone(id):
    phone = Phone.query.get_or_404(id)
    db.session.delete(phone)
    db.session.commit()
    flash('شماره تلفن با موفقیت حذف شد.', 'success')
    return redirect(url_for('phone_bp.phone'))



@phone_bp.route('/suggestions')
@login_required
def phone_suggestions():
    term = request.args.get('term', '').strip()
    query = Phone.query
    if term:
        query = query.filter(Phone.username.ilike(f'%{term}%'))
    users = query.order_by(Phone.username).limit(50).all()  # حداکثر 50 مورد
    suggestions = [user.username for user in users]
    return jsonify(suggestions)



@phone_bp.route('/field_suggestions')
@login_required
@admin_required
def field_suggestions():
    field = request.args.get('field')
    term = request.args.get('term', '').strip()
    if not field or not hasattr(Phone, field):
        return jsonify([])

    query = Phone.query
    if term:
        query = query.filter(getattr(Phone, field).ilike(f'%{term}%'))

    results = query.with_entities(getattr(Phone, field)).distinct().limit(20).all()
    suggestions = [r[0] for r in results if r[0]]  # حذف None
    return jsonify(suggestions)


@phone_bp.route('/show_exel_records', methods=['GET', 'POST'])
@login_required
@admin_required
def show_exel_records():
    filepath = session.get('uploaded_file')
    if not filepath or not os.path.exists(filepath):
        flash('فایل اکسل پیدا نشد. لطفا دوباره آپلود کنید.', 'danger')
        return redirect(url_for('phone_bp.add_multy_phone'))

    df = pd.read_excel(filepath)
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
@admin_required
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
@admin_required
def add_multy_phone_to_database():
    filepath = session.get('uploaded_file')
    if not filepath or not os.path.exists(filepath):
        flash('فایل اکسل پیدا نشد. لطفا دوباره آپلود کنید.', 'danger')
        return redirect(url_for('phone_bp.add_multy_phone'))

    df = pd.read_excel(filepath)

    # پر کردن تمام سلول‌های خالی با خط تیره
    df = df.fillna('-')

    db_fields = ['username', 'project', 'phone_number', 'pre_phone_number']

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



