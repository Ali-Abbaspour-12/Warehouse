from flask import Flask, redirect, url_for, request
from flask_login import LoginManager, current_user
from config import Config
from extensions import db
from models import User
from waitress import serve




from routes import (
    login_bp,
    dashboard_bp,
    settings_bp,
    report_bp,
    document_bp,
    personnel_bp,
    item_bp,
    camera_bp,
    phone_bp
)

login_manager = LoginManager()
login_manager.login_view = 'login_bp.login'  


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    
    db.init_app(app)
    login_manager.init_app(app)

    # -------- user_loader --------
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # -------- محدود کردن همه routeها به جز login_bp و static --------
    @app.before_request
    def require_login():
        if request.blueprint == 'login_bp' or request.endpoint == 'static':
            return
        if not current_user.is_authenticated:
            return redirect(url_for('login_bp.login'))

    # register blueprints
    app.register_blueprint(login_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(document_bp)
    app.register_blueprint(personnel_bp)
    app.register_blueprint(item_bp)
    app.register_blueprint(camera_bp)
    app.register_blueprint(phone_bp)

    return app


app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5001,debug=True)
    #serve(app, host="0.0.0.0", port=5001)
