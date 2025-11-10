from flask import Blueprint, render_template, request
from models.models import Product

search_bp = Blueprint('search', __name__)

@search_bp.route('/search')
def search():
    query = request.args.get('q', '')
    products = Product.search(query)
    return render_template('search.html', products=products, query=query)