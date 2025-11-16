from flask import Blueprint, render_template,request,redirect,url_for
from models import Item,ItemHistory
from extensions import db
from .login import admin_required


search_bp = Blueprint("search_bp", __name__,url_prefix="/search")


@search_bp.route("/search")
def search():
    args = request.args

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

    query = Item.query
    has_filter = False

    for arg_key, model_field in field_mapping.items():
        value = args.get(arg_key)
        if value:
            has_filter = True
            query = query.filter(model_field.ilike(f"%{value}%"))

    if not has_filter:
        return render_template("search_panel/search.html", items=[])

    items = query.all()
    return render_template("search_panel/search.html", items=items)

   

@search_bp.route("search_panel/show_all_records")
def show_all_records():
    items = Item.query.all()
    return render_template("search_panel/show_all_records.html",items=items)


@search_bp.route('/item_detail_<int:item_id>')
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)

    return render_template('search_panel/item_detail.html',item=item)



@search_bp.route('/history_detail_<int:item_id>_<int:history_id>')
def history_detail(item_id,history_id):
    history = ItemHistory.query.get_or_404(history_id)
    return render_template('search_panel/history_detail.html',history=history,item_id=item_id)



@search_bp.route('/item_detail_<int:item_id>/edit_item',methods=['GET','POST'])
@admin_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)

    if request.method == "POST":
        
        
        record = ItemHistory(

            project_code = item.project_code,
            warehouse_location = item.warehouse_location,
            row = item.row,
            user = item.user,
            company = item.company,
            unit = item.unit,
            personnel_code = item.personnel_code,
            current_location = item.current_location,
            system_identification_code = item.system_identification_code,
            category = item.category,
            model = item.model,
            serial_number = item.serial_number,
            property_code = item.property_code,
            recipient_delivery = item.recipient_delivery,
            description =  item.description, 
            closed = item.closed,
            closed_time = item.closed_time,
            item_id = item.id
        )

        db.session.add(record)


        item.project_code = request.form.get("project_code")
        item.warehouse_location = request.form.get("warehouse_location")
        item.row = request.form.get("row")
        item.user = request.form.get("user")
        item.company = request.form.get("company")
        item.unit = request.form.get("unit")
        item.personnel_code = request.form.get("personnel_code")
        item.current_location = request.form.get("current_location")
        item.system_identification_code = request.form.get("system_identification_code")
        item.category = request.form.get("category")
        item.model = request.form.get("model")
        item.serial_number = request.form.get("serial_number")
        item.property_code = request.form.get("property_code")
        item.recipient_delivery = request.form.get("recipient_delivery")
        item.description = request.form.get("description")
        item.closed = request.form.get("closed")
        item.closed_time = request.form.get("closed_time")

        db.session.commit()

        return redirect(url_for("search_bp.item_detail", item_id=item.id))

    return render_template("search_panel/edit_item.html", item=item)


@search_bp.route("/suggest", methods=["GET"])
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
