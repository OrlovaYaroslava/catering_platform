from flask import Blueprint,render_template,session, redirect, url_for
from app.models import Dish
from flask_login import login_required
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

@main.route("/menu")
@login_required
def menu():
    dishes = Dish.query.filter_by(is_active=True).all()
    return render_template("menu.html", dishes=dishes)

@main.route("/add_to_cart/<int:dish_id>")
@login_required
def add_to_cart(dish_id):
    cart = session.get("cart", {})

    dish_id_str = str(dish_id)
    cart[dish_id_str] = cart.get(dish_id_str, 0) + 1

    session["cart"] = cart
    return redirect(url_for("main.menu"))

@main.route("/cart")
@login_required
def cart():
    cart = session.get("cart", {})
    dishes = Dish.query.filter(Dish.id.in_(cart.keys())).all()

    total = 0
    items = []

    for dish in dishes:
        quantity = cart[str(dish.id)]
        subtotal = dish.price_per_unit * quantity
        total += subtotal

        items.append({
            "dish": dish,
            "quantity": quantity,
            "subtotal": subtotal
        })

    return render_template("cart.html", items=items, total=total)
