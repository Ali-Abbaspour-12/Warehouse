# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer,primary_key=True)
    project_code = db.Column(db.String(120))
    warehouse_location = db.Column(db.String(80))
    row = db.Column(db.String(80))
    first_recipient_delivery = db.Column(db.String(80))
    company = db.Column(db.String(80))
    unit = db.Column(db.String(80))
    personnel_code = db.Column(db.String(80))
    current_location = db.Column(db.String(80))
    system_identification_code = db.Column(db.String(80))
    category = db.Column(db.String(80))
    model = db.Column(db.String(80))
    serial_number = db.Column(db.String(80))
    property_code = db.Column(db.String(80))
    second_recipient_delivery = db.Column(db.String(80))
    third_recipient_delivery = db.Column(db.String(80))
    description = db.Column(db.String(255))   
    closed = db.Column(db.String(80))
    closed_time = db.Column(db.String(80))

