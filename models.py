
from flask_sqlalchemy import SQLAlchemy
import jdatetime

db = SQLAlchemy()

def get_now_jalali():
    return jdatetime.datetime.now().strftime('%Y/%m/%d - %H:%M:%S')

class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer,primary_key=True)
    project_code = db.Column(db.String(80))
    warehouse_location = db.Column(db.String(80))
    row = db.Column(db.String(80))
    user = db.Column(db.String(80))
    company = db.Column(db.String(80))
    unit = db.Column(db.String(80))
    personnel_code = db.Column(db.String(80))
    current_location = db.Column(db.String(80))
    system_identification_code = db.Column(db.String(80))
    category = db.Column(db.String(80))
    model = db.Column(db.String(80))
    serial_number = db.Column(db.String(80))
    property_code = db.Column(db.String(80))
    recipient_delivery = db.Column(db.String(80))
    description = db.Column(db.String(512))   
    closed = db.Column(db.String(80))
    closed_time = db.Column(db.String(80))

    item_history = db.relationship('ItemHistory',backref='Item',lazy=True)

class ItemHistory(db.Model):
    __tablename__ = 'items_history'

    id = db.Column(db.Integer,primary_key=True)
    project_code = db.Column(db.String(80))
    warehouse_location = db.Column(db.String(80))
    row = db.Column(db.String(80))
    user = db.Column(db.String(80))
    company = db.Column(db.String(80))
    unit = db.Column(db.String(80))
    personnel_code = db.Column(db.String(80))
    current_location = db.Column(db.String(80))
    system_identification_code = db.Column(db.String(80))
    category = db.Column(db.String(80))
    model = db.Column(db.String(80))
    serial_number = db.Column(db.String(80))
    property_code = db.Column(db.String(80))
    recipient_delivery = db.Column(db.String(80))
    description = db.Column(db.String(512))   
    closed = db.Column(db.String(80))
    closed_time = db.Column(db.String(80))
    changed_at = db.Column(db.String(80),default = get_now_jalali())
    item_id = db.Column(db.Integer,db.ForeignKey('items.id'),nullable=False)


