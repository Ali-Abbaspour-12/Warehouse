from flask import Blueprint, render_template, request, Response
import threading

radio_bp = Blueprint("radio_bp", __name__, url_prefix="/radio")



@radio_bp.route("/radio", methods=["GET", "POST"])
def radio():
    return render_template("radio_panel/radio.html")
                          

