from flask import Blueprint
from flask_login import login_required
from app.decorators import role_required

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return "Public page"

@main.route("/protected")
@login_required
def protected():
    return "You are logged in"

@main.route("/client")
@login_required
@role_required("client")
def client_dashboard():
    return "Client dashboard"

@main.route("/admin")
@login_required
@role_required("admin")
def admin_dashboard():
    return "Admin dashboard"

@main.route("/kitchen")
@login_required
@role_required("kitchen")
def kitchen_dashboard():
    return "Kitchen dashboard"