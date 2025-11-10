from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import pandas as pd
import os
from werkzeug.utils import secure_filename
from models.models import Product, ExcelImport, CustomField
from models.database import get_db_connection
import json

excel_import_bp = Blueprint('excel_import', __name__)

ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@excel_import_bp.route('/import/excel', methods=['GET', 'POST'])
def import_excel():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('لطفا فایل را انتخاب کنید', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('لطفا فایل را انتخاب کنید', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                upload_folder = 'uploads'
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                
                # خواندن فایل اکسل
                if filename.endswith('.csv'):
                    df = pd.read_csv(filepath)
                else:
                    df = pd.read_excel(filepath)
                
                # دریافت mapping از فرم
                mapping = {}
                for col in df.columns:
                    mapped_field = request.form.get(f'map_{col}')
                    if mapped_field:
                        mapping[col] = mapped_field
                
                # ایجاد رکورد ایمپورت
                import_id = ExcelImport.create_import(filename, mapping, len(df))
                
                # پردازش داده‌ها
                successful = 0
                failed = 0
                
                for index, row in df.iterrows():
                    try:
                        data = {}
                        for excel_col, db_field in mapping.items():
                            data[db_field] = row[excel_col]
                        
                        # بررسی فیلدهای اجباری
                        if 'name' in data and data['name']:
                            Product.create(data)
                            successful += 1
                        else:
                            failed += 1
                            
                    except Exception as e:
                        failed += 1
                        print(f"Error in row {index}: {str(e)}")
                
                # بروزرسانی نتیجه ایمپورت
                ExcelImport.update_import(import_id, successful, failed)
                
                flash(f'ایمپورت با موفقیت انجام شد. موفق: {successful}, ناموفق: {failed}', 'success')
                return redirect(url_for('excel_import.import_history'))
                
            except Exception as e:
                flash(f'خطا در پردازش فایل: {str(e)}', 'error')
        
        else:
            flash('فرمت فایل مجاز نیست. فقط فایل‌های Excel و CSV مجاز هستند.', 'error')
    
    custom_fields = CustomField.get_by_table('products')
    base_fields = ['name', 'category', 'quantity', 'price', 'description']
    all_fields = base_fields + [field['field_name'] for field in custom_fields]
    
    return render_template('import_excel.html', fields=all_fields)

@excel_import_bp.route('/import/history')
def import_history():
    imports = ExcelImport.get_all()
    return render_template('import_history.html', imports=imports)

@excel_import_bp.route('/api/import/preview', methods=['POST'])
def preview_excel():
    if 'file' not in request.files:
        return jsonify({'error': 'فایل یافت نشد'})
    
    file = request.files['file']
    if file and allowed_file(file.filename):
        try:
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            preview = df.head(10).fillna('').to_dict('records')
            columns = list(df.columns)
            
            return jsonify({
                'preview': preview,
                'columns': columns,
                'total_rows': len(df)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)})
    
    return jsonify({'error': 'فرمت فایل نامعتبر است'})