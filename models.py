# models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from zoneinfo import ZoneInfo   # پایتون 3.9+
import jdatetime

db = SQLAlchemy()

def tehran_now():
    """برگشت زمان timezone-aware تهران + رشته تاریخ/ساعت جلالی."""
    dt = datetime.now(ZoneInfo("Asia/Tehran"))
    jdt = jdatetime.datetime.fromgregorian(datetime=dt)
    return dt, jdt.strftime("%Y/%m/%d %H:%M:%S")

class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    project_code = db.Column(db.String(120), nullable=False)
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
    description = db.Column(db.String(255))   # اصلاح املای descripiton
    closed = db.Column(db.String(80))
    closed_time = db.Column(db.String(80))

    histories = relationship("ItemHistory", back_populates="item", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Item {self.project_code}>"

class ItemHistory(db.Model):
    __tablename__ = 'item_histories'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, ForeignKey('items.id'), index=True, nullable=False)

    # زمان اسنپ‌شات
    snapshot_at = db.Column(db.DateTime(timezone=True), nullable=False)
    snapshot_at_jalali = db.Column(db.String(19), nullable=False)  # مثال: 1404/08/19 12:34:56

    # نوع تغییر: update/delete
    change_type = db.Column(db.String(16), nullable=False, default='update')

    # کپی فیلدهای آیتم (اسنپ‌شات):
    project_code = db.Column(db.String(120), nullable=False)
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

    item = relationship("Item", back_populates="histories")

    def __repr__(self):
        return f"<ItemHistory item_id={self.item_id} type={self.change_type} at={self.snapshot_at_jalali}>"

def _make_history_from_item(item, change_type='update', use_previous_values=False):
    """یک رکورد تاریخچه از آیتم می‌سازد."""
    dt, jdt = tehran_now()

    # اگر بخوایم دقیقا مقادیر قبلی رو بگیریم، از history هر اتریبیوت استفاده می‌کنیم:
    def prev_or_curr(attr_name):
        if not use_previous_values:
            return getattr(item, attr_name)
        attr_state = db.inspect(item).attrs[attr_name].history
        if attr_state.deleted and len(attr_state.deleted) > 0:
            return attr_state.deleted[0]
        return getattr(item, attr_name)

    return ItemHistory(
        item_id=item.id,
        snapshot_at=dt,
        snapshot_at_jalali=jdt,
        change_type=change_type,
        project_code=prev_or_curr('project_code'),
        warehouse_location=prev_or_curr('warehouse_location'),
        row=prev_or_curr('row'),
        first_recipient_delivery=prev_or_curr('first_recipient_delivery'),
        company=prev_or_curr('company'),
        unit=prev_or_curr('unit'),
        personnel_code=prev_or_curr('personnel_code'),
        current_location=prev_or_curr('current_location'),
        system_identification_code=prev_or_curr('system_identification_code'),
        category=prev_or_curr('category'),
        model=prev_or_curr('model'),
        serial_number=prev_or_curr('serial_number'),
        property_code=prev_or_curr('property_code'),
        second_recipient_delivery=prev_or_curr('second_recipient_delivery'),
        third_recipient_delivery=prev_or_curr('third_recipient_delivery'),
        description=prev_or_curr('description'),
        closed=prev_or_curr('closed'),
        closed_time=prev_or_curr('closed_time'),
    )


