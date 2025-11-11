from flask import request,flash,redirect

@app.route("/add_item", methods=["POST"])
def add_item():
    # عملیات اضافه کردن رکورد
    flash("آیتم با موفقیت اضافه شد!", "success")  # "success" کلاس پیام
    return redirect(url_for("show_items"))
