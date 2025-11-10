from .database import get_db_connection
import json
from datetime import datetime

class Product:
    @staticmethod
    def get_all():
        conn = get_db_connection()
        try:
            products = conn.execute('SELECT * FROM products ORDER BY created_at DESC').fetchall()
            return products
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(product_id):
        conn = get_db_connection()
        try:
            product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
            return product
        finally:
            conn.close()
    
    @staticmethod
    def search(query, filters=None):
        conn = get_db_connection()
        try:
            where_conditions = []
            params = []
            
            if query:
                where_conditions.append('(name LIKE ? OR category LIKE ? OR description LIKE ?)')
                params.extend([f'%{query}%', f'%{query}%', f'%{query}%'])
            
            if filters:
                for field, value in filters.items():
                    if value:
                        where_conditions.append(f'{field} = ?')
                        params.append(value)
            
            where_clause = ' AND '.join(where_conditions) if where_conditions else '1=1'
            
            sql = f'SELECT * FROM products WHERE {where_clause} ORDER BY created_at DESC'
            products = conn.execute(sql, params).fetchall()
            return products
        finally:
            conn.close()
    
    @staticmethod
    def create(data):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO products (name, category, quantity, price, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (data['name'], data.get('category'), data.get('quantity', 0), 
                  data.get('price', 0), data.get('description', '')))
            
            product_id = cursor.lastrowid
            conn.commit()
            
            # ثبت در تاریخچه تغییرات
            for field, value in data.items():
                ChangeHistory.record_change('products', product_id, field, None, value, 'system')
            
            return product_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def update(product_id, data):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # دریافت مقادیر قدیمی
            old_product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
            old_values = dict(old_product) if old_product else {}
            
            # بروزرسانی محصول
            cursor.execute('''
                UPDATE products 
                SET name = ?, category = ?, quantity = ?, price = ?, description = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (data['name'], data.get('category'), data.get('quantity', 0), 
                  data.get('price', 0), data.get('description', ''), product_id))
            
            # ثبت در تاریخچه تغییرات
            for field, new_value in data.items():
                old_value = old_values.get(field)
                if str(old_value) != str(new_value):
                    ChangeHistory.record_change('products', product_id, field, old_value, new_value, 'system')
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def delete(product_id):
        conn = get_db_connection()
        try:
            # دریافت مقادیر قدیمی برای تاریخچه
            product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
            if product:
                for field in product.keys():
                    if field not in ['id', 'created_at', 'updated_at']:
                        ChangeHistory.record_change('products', product_id, field, product[field], None, 'system')
            
            conn.execute('DELETE FROM products WHERE id = ?', (product_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

class CustomField:
    @staticmethod
    def get_all():
        conn = get_db_connection()
        try:
            fields = conn.execute('SELECT * FROM custom_fields ORDER BY table_name, sort_order').fetchall()
            return fields
        finally:
            conn.close()
    
    @staticmethod
    def get_by_table(table_name):
        conn = get_db_connection()
        try:
            fields = conn.execute('SELECT * FROM custom_fields WHERE table_name = ? ORDER BY sort_order', (table_name,)).fetchall()
            return fields
        finally:
            conn.close()
    
    @staticmethod
    def create(table_name, field_name, field_type, display_name, is_required, is_searchable, is_filterable):
        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO custom_fields (table_name, field_name, field_type, display_name, is_required, is_searchable, is_filterable)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (table_name, field_name, field_type, display_name, is_required, is_searchable, is_filterable))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def update(field_id, table_name, field_type, display_name, is_required, is_searchable, is_filterable):
        conn = get_db_connection()
        try:
            conn.execute('''
                UPDATE custom_fields 
                SET table_name = ?, field_type = ?, display_name = ?, is_required = ?, is_searchable = ?, is_filterable = ?
                WHERE id = ?
            ''', (table_name, field_type, display_name, is_required, is_searchable, is_filterable, field_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def delete(field_id):
        conn = get_db_connection()
        try:
            conn.execute('DELETE FROM custom_fields WHERE id = ?', (field_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

class SearchSetting:
    @staticmethod
    def get_all():
        conn = get_db_connection()
        try:
            settings = conn.execute('SELECT * FROM search_settings ORDER BY is_active DESC, name').fetchall()
            return settings
        finally:
            conn.close()
    
    @staticmethod
    def get_active():
        conn = get_db_connection()
        try:
            setting = conn.execute('SELECT * FROM search_settings WHERE is_active = 1').fetchone()
            return setting
        finally:
            conn.close()
    
    @staticmethod
    def create(name, table_name, search_fields, filter_fields, sort_field, sort_order, is_active):
        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO search_settings (name, table_name, search_fields, filter_fields, sort_field, sort_order, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, table_name, search_fields, filter_fields, sort_field, sort_order, is_active))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def update(setting_id, name, table_name, search_fields, filter_fields, sort_field, sort_order, is_active):
        conn = get_db_connection()
        try:
            conn.execute('''
                UPDATE search_settings 
                SET name = ?, table_name = ?, search_fields = ?, filter_fields = ?, 
                    sort_field = ?, sort_order = ?, is_active = ?
                WHERE id = ?
            ''', (name, table_name, search_fields, filter_fields, sort_field, sort_order, is_active, setting_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def delete(setting_id):
        conn = get_db_connection()
        try:
            conn.execute('DELETE FROM search_settings WHERE id = ?', (setting_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def toggle(setting_id):
        conn = get_db_connection()
        try:
            setting = conn.execute('SELECT * FROM search_settings WHERE id = ?', (setting_id,)).fetchone()
            if setting:
                new_status = 0 if setting['is_active'] else 1
                conn.execute('UPDATE search_settings SET is_active = ? WHERE id = ?', (new_status, setting_id))
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

class ChangeHistory:
    @staticmethod
    def record_change(table_name, record_id, field_name, old_value, new_value, changed_by='system'):
        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO change_history (table_name, record_id, field_name, old_value, new_value, changed_by)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (table_name, record_id, field_name, old_value, new_value, changed_by))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def get_history(table_name, record_id):
        conn = get_db_connection()
        try:
            history = conn.execute('''
                SELECT * FROM change_history 
                WHERE table_name = ? AND record_id = ? 
                ORDER BY changed_at DESC
            ''', (table_name, record_id)).fetchall()
            return history
        finally:
            conn.close()

class ExcelImport:
    @staticmethod
    def create_import(filename, mapping_config, total_records):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO excel_imports (filename, mapping_config, total_records)
                VALUES (?, ?, ?)
            ''', (filename, json.dumps(mapping_config), total_records))
            import_id = cursor.lastrowid
            conn.commit()
            return import_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def update_import(import_id, successful_records, failed_records):
        conn = get_db_connection()
        try:
            conn.execute('''
                UPDATE excel_imports 
                SET successful_records = ?, failed_records = ?
                WHERE id = ?
            ''', (successful_records, failed_records, import_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def get_all():
        conn = get_db_connection()
        try:
            imports = conn.execute('SELECT * FROM excel_imports ORDER BY imported_at DESC').fetchall()
            return imports
        finally:
            conn.close()