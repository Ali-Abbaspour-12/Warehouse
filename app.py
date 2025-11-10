from flask import Flask
from config import Config
from models.database import init_db
from routes.main import main_bp
from routes.search import search_bp
from routes.settings import settings_bp
from routes.products import products_bp
from routes.excel_import import excel_import_bp

app = Flask(__name__)
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# ثبت blueprint ها
app.register_blueprint(main_bp)
app.register_blueprint(search_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(products_bp)
app.register_blueprint(excel_import_bp)

# راه‌اندازی دیتابیس
init_db()

if __name__ == '__main__':
    app.run(debug=True)