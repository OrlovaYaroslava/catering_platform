from flask import Blueprint
from flask_login import login_required

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return "Public page"

@main.route("/protected")
@login_required
def protected():
    return "You are logged in"
