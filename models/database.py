import sqlite3
import os
import json
from datetime import datetime
from config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(Config.DATABASE):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # ایجاد جدول فیلدهای داینامیک
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_fields (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL,
                field_name TEXT NOT NULL,
                field_type TEXT NOT NULL,
                display_name TEXT NOT NULL,
                is_required INTEGER DEFAULT 0,
                is_searchable INTEGER DEFAULT 1,
                is_filterable INTEGER DEFAULT 1,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ایجاد جدول تنظیمات جستجو
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                table_name TEXT NOT NULL,
                search_fields TEXT NOT NULL,
                filter_fields TEXT,
                sort_field TEXT,
                sort_order TEXT DEFAULT 'DESC',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ایجاد جدول محصولات با فیلدهای پایه
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                quantity INTEGER DEFAULT 0,
                price INTEGER DEFAULT 0,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ایجاد جدول تاریخچه تغییرات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS change_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL,
                record_id INTEGER NOT NULL,
                field_name TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                changed_by TEXT DEFAULT 'system',
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ایجاد جدول ایمپورت از اکسل
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS excel_imports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                mapping_config TEXT,
                total_records INTEGER DEFAULT 0,
                successful_records INTEGER DEFAULT 0,
                failed_records INTEGER DEFAULT 0,
                imported_by TEXT DEFAULT 'system',
                imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # بررسی وجود داده‌های نمونه
        existing_products = cursor.execute('SELECT COUNT(*) FROM products').fetchone()[0]
        if existing_products == 0:
            # درج داده‌های نمونه
            for product in Config.SAMPLE_PRODUCTS:
                cursor.execute('''
                    INSERT INTO products (name, category, quantity, price, description)
                    VALUES (?, ?, ?, ?, ?)
                ''', (product['name'], product['category'], product['quantity'], product['price'], 'توضیحات نمونه'))
        
        # درج تنظیمات جستجوی پیش‌فرض
        existing_settings = cursor.execute('SELECT COUNT(*) FROM search_settings').fetchone()[0]
        if existing_settings == 0:
            cursor.execute('''
                INSERT INTO search_settings (name, table_name, search_fields, filter_fields, sort_field)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                'جستجوی پیشرفته محصولات',
                'products',
                'name,category,description',
                'category,quantity,price',
                'created_at'
            ))
        
        conn.commit()
        conn.close()
        print("Database initialized successfully!")