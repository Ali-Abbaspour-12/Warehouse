from flask import Blueprint, render_template
from flask_login import login_required
from .login import admin_required


document_bp = Blueprint("document_bp", __name__)

@document_bp.route("/")
@login_required
def document():
    return render_template("document_panel/document.html")
