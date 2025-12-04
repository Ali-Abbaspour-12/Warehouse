
from flask_sqlalchemy import SQLAlchemy
import jdatetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db,login_manager


def get_now_jalali():
    return jdatetime.datetime.now().strftime('%Y/%m/%d')

def get_now_jalali_with_time():
    return jdatetime.datetime.now().strftime("%Y/%m/%d-%H:%M:%S")

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



class ItemLog(db.Model):
    __tablename__ = 'items_log'

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
    changed_at = db.Column(db.String(80),default = get_now_jalali_with_time())



class User(UserMixin, db.Model):
    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)



class Personnel(db.Model):
    __tablename__ = 'personnels'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    personnel_code = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(100), nullable=False)
    national_code = db.Column(db.String(100), nullable=False)
    current_location = db.Column(db.String(100), nullable=False)


class Repair(db.Model):
    __tablename__ = 'repairs'

    id = db.Column(db.Integer, primary_key=True)
    device_type = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100), nullable=False)
    property_code = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(512), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    current_location = db.Column(db.String(100), nullable=False)


class Phone(db.Model):
    __tablename__ = 'phones'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    place = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(100), nullable=False)
    pre_phone_number = db.Column(db.String(100), nullable=False)

