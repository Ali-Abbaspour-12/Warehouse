import os
from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory, flash
from flask_login import login_required
from .login import admin_required  # اگر میخوای فقط ادمین اجازه حذف/آپلود داشته باشه

document_bp = Blueprint("document_bp", __name__,url_prefix="/document")

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@document_bp.route("/document", methods=["GET", "POST"])
@login_required
def document():
    if request.method == "POST":
        # آپلود فایل
        if "file" not in request.files:
            flash("هیچ فایلی انتخاب نشده است.")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("هیچ فایلی انتخاب نشده است.")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = file.filename
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            flash("فایل با موفقیت آپلود شد.")
            return redirect(url_for("document_bp.document"))

    # نمایش لیست فایل‌ها
    files = os.listdir(UPLOAD_FOLDER)
    return render_template("document_panel/document.html", files=files)

@document_bp.route("/document/uploads/<filename>")
@admin_required 
@login_required
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@document_bp.route("/document/delete/<filename>", methods=["POST"])
@admin_required 
@login_required
def delete_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash("فایل با موفقیت حذف شد.")
    else:
        flash("فایل پیدا نشد.")
    return redirect(url_for("document_bp.document"))
