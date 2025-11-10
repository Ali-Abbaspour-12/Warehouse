import os

class Config:
    SECRET_KEY = 'your_secret_key_here'
    DATABASE = 'warehouse.db'
    
    # داده‌های نمونه برای نمایش
    SAMPLE_PRODUCTS = [
        {"id": 1, "name": "لپ‌تاپ ایسوس", "category": "الکترونیکی", "quantity": 15, "price": 12000000},
        {"id": 2, "name": "ماوس بی‌سیم", "category": "الکترونیکی", "quantity": 42, "price": 350000},
        {"id": 3, "name": "صندلی اداری", "category": "اداری", "quantity": 8, "price": 2500000},
        {"id": 4, "name": "کاغذ A4", "category": "اداری", "quantity": 120, "price": 80000},
        {"id": 5, "name": "پرینتر HP", "category": "الکترونیکی", "quantity": 5, "price": 8500000},
    ]