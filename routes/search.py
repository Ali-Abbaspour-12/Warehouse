from flask import Blueprint, render_template,request
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