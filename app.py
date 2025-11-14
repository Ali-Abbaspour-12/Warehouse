from flask import Flask
from models import db
from routes import dashboard_bp,add_item_bp,search_bp,settings_bp,report_bp

app = Flask(__name__)

app.secret_key = "your_secret_key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Aass13579@localhost:5432/warehouse_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.register_blueprint(dashboard_bp)
app.register_blueprint(add_item_bp)
app.register_blueprint(search_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(report_bp)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0",debug=True)
