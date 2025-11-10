from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models.models import Product, ChangeHistory, CustomField
from models.database import get_db_connection
import json

products_bp = Blueprint('products', __name__)

@products_bp.route('/products/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        try:
            data = {
                'name': request.form['name'],
                'category': request.form.get('category'),
                'quantity': int(request.form.get('quantity', 0)),
                'price': int(request.form.get('price', 0)),
                'description': request.form.get('description', '')
            }
            
            # اضافه کردن فیلدهای داینامیک
            custom_fields = CustomField.get_by_table('products')
            for field in custom_fields:
                field_value = request.form.get(field['field_name'])
                if field_value:
                    data[field['field_name']] = field_value
            
            product_id = Product.create(data)
            flash('محصول با موفقیت اضافه شد', 'success')
            return redirect(url_for('search.search'))
            
        except Exception as e:
            flash(f'خطا در افزودن محصول: {str(e)}', 'error')
    
    custom_fields = CustomField.get_by_table('products')
    return render_template('add_product.html', custom_fields=custom_fields)

@products_bp.route('/products/<int:product_id>')
def product_detail(product_id):
    product = Product.get_by_id(product_id)
    if not product:
        flash('محصول مورد نظر یافت نشد', 'error')
        return redirect(url_for('search.search'))
    
    history = ChangeHistory.get_history('products', product_id)
    return render_template('product_detail.html', product=product, history=history)

@products_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.get_by_id(product_id)
    if not product:
        flash('محصول مورد نظر یافت نشد', 'error')
        return redirect(url_for('search.search'))
    
    if request.method == 'POST':
        try:
            data = {
                'name': request.form['name'],
                'category': request.form.get('category'),
                'quantity': int(request.form.get('quantity', 0)),
                'price': int(request.form.get('price', 0)),
                'description': request.form.get('description', '')
            }
            
            # اضافه کردن فیلدهای داینامیک
            custom_fields = CustomField.get_by_table('products')
            for field in custom_fields:
                field_value = request.form.get(field['field_name'])
                if field_value is not None:
                    data[field['field_name']] = field_value
            
            Product.update(product_id, data)
            flash('محصول با موفقیت ویرایش شد', 'success')
            return redirect(url_for('products.product_detail', product_id=product_id))
            
        except Exception as e:
            flash(f'خطا در ویرایش محصول: {str(e)}', 'error')
    
    custom_fields = CustomField.get_by_table('products')
    return render_template('edit_product.html', product=product, custom_fields=custom_fields)

@products_bp.route('/products/delete/<int:product_id>')
def delete_product(product_id):
    try:
        Product.delete(product_id)
        flash('محصول با موفقیت حذف شد', 'success')
    except Exception as e:
        flash(f'خطا در حذف محصول: {str(e)}', 'error')
    
    return redirect(url_for('search.search'))

@products_bp.route('/api/products/categories')
def get_categories():
    conn = get_db_connection()
    categories = conn.execute('SELECT DISTINCT category FROM products WHERE category IS NOT NULL').fetchall()
    conn.close()
    return jsonify([cat['category'] for cat in categories])