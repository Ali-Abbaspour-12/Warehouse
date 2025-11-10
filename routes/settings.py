from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.models import CustomField, SearchSetting
from models.database import get_db_connection

settings_bp = Blueprint('settings', __name__)

# صفحه اصلی تنظیمات
@settings_bp.route('/settings')
def settings():
    return render_template('settings.html')

# مدیریت فیلدها
@settings_bp.route('/settings/fields')
def manage_fields():
    fields = CustomField.get_all()
    return render_template('manage_fields.html', fields=fields)

@settings_bp.route('/settings/fields/add', methods=['GET', 'POST'])
def add_field():
    if request.method == 'POST':
        # فقط یک جدول داریم: products
        table_name = 'products'
        field_name = request.form['field_name']
        field_type = request.form['field_type']
        display_name = request.form['display_name']
        is_required = 1 if request.form.get('is_required') else 0
        is_searchable = 1 if request.form.get('is_searchable') else 0
        is_filterable = 1 if request.form.get('is_filterable') else 0
        
        try:
            CustomField.create(table_name, field_name, field_type, display_name, is_required, is_searchable, is_filterable)
            flash('فیلد با موفقیت اضافه شد', 'success')
            return redirect(url_for('settings.manage_fields'))
        except Exception as e:
            flash(f'خطا در ایجاد فیلد: {str(e)}', 'error')
    
    return render_template('add_field.html')

@settings_bp.route('/settings/fields/edit/<int:field_id>', methods=['GET', 'POST'])
def edit_field(field_id):
    if request.method == 'POST':
        # فقط یک جدول داریم: products
        table_name = 'products'
        field_name = request.form['field_name']
        field_type = request.form['field_type']
        display_name = request.form['display_name']
        is_required = 1 if request.form.get('is_required') else 0
        is_searchable = 1 if request.form.get('is_searchable') else 0
        is_filterable = 1 if request.form.get('is_filterable') else 0
        
        try:
            CustomField.update(field_id, table_name, field_type, display_name, is_required, is_searchable, is_filterable)
            flash('فیلد با موفقیت بروزرسانی شد', 'success')
            return redirect(url_for('settings.manage_fields'))
        except Exception as e:
            flash(f'خطا در بروزرسانی فیلد: {str(e)}', 'error')
    
    conn = get_db_connection()
    field = conn.execute('SELECT * FROM custom_fields WHERE id = ?', (field_id,)).fetchone()
    conn.close()
    
    if field is None:
        flash('فیلد مورد نظر یافت نشد', 'error')
        return redirect(url_for('settings.manage_fields'))
    
    return render_template('edit_field.html', field=field)

@settings_bp.route('/settings/fields/delete/<int:field_id>')
def delete_field(field_id):
    try:
        CustomField.delete(field_id)
        flash('فیلد با موفقیت حذف شد', 'success')
    except Exception as e:
        flash(f'خطا در حذف فیلد: {str(e)}', 'error')
    
    return redirect(url_for('settings.manage_fields'))

# مدیریت جستجو
@settings_bp.route('/settings/search')
def manage_search():
    settings = SearchSetting.get_all()
    return render_template('manage_search.html', search_settings=settings)

@settings_bp.route('/settings/search/add', methods=['GET', 'POST'])
def add_search_setting():
    if request.method == 'POST':
        name = request.form['name']
        table_name = request.form['table_name']
        search_fields = request.form['search_fields']
        filter_fields = request.form.get('filter_fields', '')
        sort_field = request.form.get('sort_field', '')
        sort_order = request.form.get('sort_order', 'DESC')
        is_active = 1 if request.form.get('is_active') else 0
        
        try:
            SearchSetting.create(name, table_name, search_fields, filter_fields, sort_field, sort_order, is_active)
            flash('تنظیمات جستجو با موفقیت اضافه شد', 'success')
            return redirect(url_for('settings.manage_search'))
        except Exception as e:
            flash(f'خطا در ایجاد تنظیمات جستجو: {str(e)}', 'error')
    
    return render_template('add_search_setting.html')

@settings_bp.route('/settings/search/edit/<int:setting_id>', methods=['GET', 'POST'])
def edit_search_setting(setting_id):
    if request.method == 'POST':
        name = request.form['name']
        table_name = request.form['table_name']
        search_fields = request.form['search_fields']
        filter_fields = request.form.get('filter_fields', '')
        sort_field = request.form.get('sort_field', '')
        sort_order = request.form.get('sort_order', 'DESC')
        is_active = 1 if request.form.get('is_active') else 0
        
        try:
            SearchSetting.update(setting_id, name, table_name, search_fields, filter_fields, sort_field, sort_order, is_active)
            flash('تنظیمات جستجو با موفقیت بروزرسانی شد', 'success')
            return redirect(url_for('settings.manage_search'))
        except Exception as e:
            flash(f'خطا در بروزرسانی تنظیمات جستجو: {str(e)}', 'error')
    
    conn = get_db_connection()
    setting = conn.execute('SELECT * FROM search_settings WHERE id = ?', (setting_id,)).fetchone()
    conn.close()
    
    if setting is None:
        flash('تنظیمات جستجوی مورد نظر یافت نشد', 'error')
        return redirect(url_for('settings.manage_search'))
    
    return render_template('edit_search_setting.html', setting=setting)

@settings_bp.route('/settings/search/delete/<int:setting_id>')
def delete_search_setting(setting_id):
    try:
        SearchSetting.delete(setting_id)
        flash('تنظیمات جستجو با موفقیت حذف شد', 'success')
    except Exception as e:
        flash(f'خطا در حذف تنظیمات جستجو: {str(e)}', 'error')
    
    return redirect(url_for('settings.manage_search'))

@settings_bp.route('/settings/search/toggle/<int:setting_id>')
def toggle_search_setting(setting_id):
    try:
        SearchSetting.toggle(setting_id)
        flash('وضعیت تنظیمات جستجو تغییر کرد', 'success')
    except Exception as e:
        flash(f'خطا در تغییر وضعیت تنظیمات جستجو: {str(e)}', 'error')
    
    return redirect(url_for('settings.manage_search'))