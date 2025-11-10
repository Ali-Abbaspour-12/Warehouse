from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# داده‌های نمونه برای نمایش
sample_products = [
    {"id": 1, "name": "لپ‌تاپ ایسوس", "category": "الکترونیکی", "quantity": 15, "price": 12000000},
    {"id": 2, "name": "ماوس بی‌سیم", "category": "الکترونیکی", "quantity": 42, "price": 350000},
    {"id": 3, "name": "صندلی اداری", "category": "اداری", "quantity": 8, "price": 2500000},
    {"id": 4, "name": "کاغذ A4", "category": "اداری", "quantity": 120, "price": 80000},
    {"id": 5, "name": "پرینتر HP", "category": "الکترونیکی", "quantity": 5, "price": 8500000},
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', products=sample_products)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        results = [p for p in sample_products if query.lower() in p['name'].lower()]
    else:
        results = sample_products
    return render_template('search.html', products=results, query=query)

if __name__ == '__main__':
    app.run(debug=True)