from flask import Flask, render_template, request, redirect, url_for

from models import db, Item

app = Flask(__name__)




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/excel_import')
def excel_import():
    return render_template('excel_import.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route("/search")
def search():
    return render_template("search.html")


if __name__ == '__main__':
    app.run(debug=True)
