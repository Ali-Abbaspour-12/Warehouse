import os
from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory, flash
from flask_login import login_required
from .login import admin_required

document_bp = Blueprint("document_bp", __name__, url_prefix="/document")

UPLOAD_FOLDER = "./uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# صفحه اصلی: نمایش تمام فایل‌ها
@document_bp.route("/document", methods=["GET", "POST"])
@login_required
def document():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template("document_panel/document.html", files=files)


# دانلود هر نوع فایل
@document_bp.route("/download/<filename>")
@login_required
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
