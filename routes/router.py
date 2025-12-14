from flask import Blueprint, render_template, request, Response
import threading

router_bp = Blueprint("router_bp", __name__, url_prefix="/router")



@router_bp.route("/router", methods=["GET", "POST"])
def router():
    return render_template("router_panel/router.html")
                          

