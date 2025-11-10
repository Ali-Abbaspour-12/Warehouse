from flask import Blueprint, render_template
from models.models import Product

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
def dashboard():
    products = Product.get_all()
    return render_template('dashboard.html', products=products)