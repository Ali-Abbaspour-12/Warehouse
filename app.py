from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from models import db, Item

app = Flask(__name__)



app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

with app.app_context():
    db.create_all()

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route("/search")
def search():
    return render_template("search.html")

@app.route("/add_item")
def add_item():
    return render_template("add_item.html")


@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/excel_import')
def excel_import():
    return render_template('excel_import.html')


if __name__ == '__main__':
    app.run(debug=True)
