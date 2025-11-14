from flask import Blueprint, render_template,request,redirect,url_for
from models import Item,db,ItemHistory


search_bp = Blueprint("search_bp", __name__)

@search_bp.route("/search")
def search():
    query_params_exist = any([
        request.args.get('q'),
        request.args.get('project_code'),
        request.args.get('company'),
        request.args.get('warehouse_locaiton'),
        request.args.get('category'),
    ])


    if not query_params_exist:
        return render_template('search.html',items=[])

    query = Item.query

    search = request.args.get("q")
    if search:
        query = query.filter(Item.property_code.ilike(f"%{search}%"))


    project_code = request.args.get("project_code")
    if project_code:
        query = query.filter(Item.project_code.ilike(f'%{project_code}%'))

    persian_equal = {}
    company = request.args.get("company") 
    if company:
        query = query.filter(Item.company.ilike(f'%{company}%'))


    category = request.args.get("category") 
    if category:
        query = query.filter(Item.category.ilike(f'%{category}%'))  



    warehouse_location = request.args.get("warehouse_location") 
    if warehouse_location:
        query = query.filter(Item.warehouse_location.ilike(f'%{warehouse_location}%')) 
 

    items = query.all()

    return render_template("search.html",items=items)        

   


@search_bp.route("/show_all_records")
def show_all_records():
    items = Item.query.all()
    return render_template("show_all_records.html",items=items)


@search_bp.route('/item_detail_<int:item_id>')
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)

    return render_template('item_detail.html',item=item)


@search_bp.route('/history_detail_<int:item_id>_<int:history_id>')
def history_detail(item_id,history_id):
    history = ItemHistory.query.filter_by(id=history_id)
    return render_template('history_detail.html',history=history,item_id=item_id)


@search_bp.route('/item_detail_<int:item_id>/edit_item',methods=['GET','POST'])
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

    return render_template("edit_item.html", item=item)
    