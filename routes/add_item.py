from flask import Flask, render_template,render_template_string, request, redirect, url_for,Blueprint,flash
from models import db, Item
import pandas as pd

add_item_bp = Blueprint("add_item_bp", __name__,url_prefix="/add_item")


@add_item_bp.route("/add_item",methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        record = Item(

                project_code = request.form.get('project_code'),
                #warehouse_location = request.form.get('warehouse_location'),
                #row = request.form.get('row'),
                user = request.form.get('user'),
                company = request.form.get('company'),
                unit = request.form.get('unit'),
                personnel_code = request.form.get('personnel_code'),
                current_location = request.form.get('current_location'),
                system_identification_code = request.form.get('system_identification_code'),
                category = request.form.get('category'),
                model = request.form.get('model'),
                serial_number = request.form.get('serial_number'),
                property_code = request.form.get('property_code'),
                recipient_delivery = request.form.get('recipient_delivery'),
                description =  request.form.get('description'), 
                closed = request.form.get('closed'),
                closed_time = request.form.get('closed_time'),

        )
        db.session.add(record)
        db.session.commit()
        flash("آیتم با موفقیت اضافه شد!", "success")
        return redirect(url_for("add_item_bp.add_item"))

    return render_template("add_item_panel/add_item.html")



@add_item_bp.route('/show_all_items_wants_import_from_excel')
def show_all_items_wants_import_from_excel():

    excelFile = pd.read_excel("./excel/data.xlsx")

    records = []
    for _,excelRow in excelFile.iterrows():
        record = (

                excelRow["project_code"],
                #excelRow["warehouse_location"],
                #excelRow["row"],
                excelRow["user"],
                excelRow["company"],
                excelRow["unit"],
                excelRow["personnel_code"],
                excelRow["current_location"],
                excelRow["system_identification_code"],
                excelRow["category"],
                excelRow["model"],
                excelRow["serial_number"],
                excelRow["property_code"],
                excelRow["recipient_delivery"],
                excelRow["description"], 
                excelRow["closed"],
                excelRow["closed_time"],

        )
        records.append(record)
    return render_template("add_item_panel/show_all_items_wants_import_from_excel.html",records=records)


@add_item_bp.route('/excel_import')
def excel_import():
    return render_template('add_item_panel/excel_import.html')



@add_item_bp.route("/excel_import/import_to_database")
def import_to_database():

    excelFile = pd.read_excel("./excel/data.xlsx").astype(str)

    for _,excelRow in excelFile.iterrows():
        record = Item(

                project_code = excelRow["project_code"],
                #warehouse_location = excelRow["warehouse_location"],
                #row = excelRow["row"],
                user = excelRow["user"],
                company = excelRow["company"],
                unit = excelRow["unit"],
                personnel_code = excelRow["personnel_code"],
                current_location = excelRow["current_location"],
                system_identification_code = excelRow["system_identification_code"],
                category = excelRow["category"],
                model = excelRow["model"],
                serial_number = excelRow["serial_number"],
                property_code = excelRow["property_code"],
                recipient_delivery = excelRow["recipient_delivery"],
                description =  excelRow["description"], 
                closed = excelRow["closed"],
                closed_time = excelRow["closed_time"],

        )
        db.session.add(record)

    
    db.session.commit()

    flash("آیتم با موفقیت اضافه شد!", "success")
    return redirect(url_for("add_item_bp.excel_import"))


@add_item_bp.route("/suggest", methods=["GET"])
def suggest():
    args = request.args

    field = args.get("field")
    value = args.get("value", "")

    field_mapping = {
       "property_code": Item.property_code,
        "project_code": Item.project_code,
        "user": Item.user,
        "company": Item.company,
        "category": Item.category,
        "personnel_code":Item.personnel_code,
        "current_location":Item.current_location,
        "system_identification_code":Item.system_identification_code,
        "model":Item.model,
        "serial_number":Item.serial_number,
        "recipient_delivery":Item.recipient_delivery,
        "closed":Item.closed
    }

    if field not in field_mapping:
        return {"error": "invalid field"}, 400

    query = Item.query

    # اعمال فیلتر برای فیلدهای دیگر
    for key, column in field_mapping.items():
        if key != field:
            v = args.get(key)
            if v:
                query = query.filter(column.ilike(f"%{v}%"))

    # دریافت همه مقادیر
    suggestions = (
        query.with_entities(field_mapping[field])
        .distinct()
        .filter(field_mapping[field].ilike(f"%{value}%"))
        .order_by(field_mapping[field])
        
        .all()
    )

    return {"suggestions": [s[0] for s in suggestions if s[0]]}