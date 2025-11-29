from flask import Blueprint, render_template

main_router = Blueprint("main_router", __name__)
@main_router.route("/")
def index():
    return render_template("main/main.html")
