from flask import Blueprint, render_template, request, Response
import cv2
import threading

switch_bp = Blueprint("switch_bp", __name__, url_prefix="/switch")



@switch_bp.route("/switch", methods=["GET", "POST"])
def switch():
    return render_template("switch_panel/switch.html")
                          

