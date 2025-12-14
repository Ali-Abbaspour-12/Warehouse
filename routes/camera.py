from flask import Blueprint, render_template, request, Response
import threading

camera_bp = Blueprint("camera_bp", __name__, url_prefix="/camera")



@camera_bp.route("/", methods=["GET", "POST"])
def camera():
    return render_template("camera_panel/camera.html")
                          

