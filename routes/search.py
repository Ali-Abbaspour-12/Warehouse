from flask import Blueprint, render_template,request,redirect,url_for
from models import Item,db


search_bp = Blueprint("search_bp", __name__)

@search_bp.route("/search")
def search():

    q = request.args.get("q")
    if not q:
        return render_template("search.html",items=[])
    
    

    items = Item.query.filter(Item.property_code.contains(q)).all()
    return render_template("search.html",items=items)




    

    


@search_bp.route("/show_all_records")
def show_all_records():
    items = Item.query.all()
    return render_template("show_all_records.html",items=items)


@search_bp.route('/item_detail_<int:item_id>')
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)

    return render_template('item_detail.html',item=item)

@search_bp.route('/item_detail_<int:item_id>/edit',methods=['GET','POST'])
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)

    if request.method == "POST":
        
        item.project_code = request.form.get("project_code")
        item.warehouse_location = request.form.get("warehouse_location")
        item.row = request.form.get("row")
        item.first_recipient_delivery = request.form.get("first_recipient_delivery")
        item.company = request.form.get("company")
        item.unit = request.form.get("unit")
        item.personnel_code = request.form.get("personnel_code")
        item.current_location = request.form.get("current_location")
        item.system_identification_code = request.form.get("system_identification_code")
        item.category = request.form.get("category")
        item.model = request.form.get("model")
        item.serial_number = request.form.get("serial_number")
        item.property_code = request.form.get("property_code")
        item.second_recipient_delivery = request.form.get("second_recipient_delivery")
        item.third_recipient_delivery = request.form.get("third_recipient_delivery")
        item.forth_recipient_delivery = request.form.get("forth_recipient_delivery")
        item.description = request.form.get("description")
        item.closed = request.form.get("closed")
        item.closed_time = request.form.get("closed_time")

        db.session.commit()

        return redirect(url_for("search_bp.item_detail", item_id=item.id))

    return render_template("edit_item.html", item=item)
    