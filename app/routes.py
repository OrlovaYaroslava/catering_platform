from flask import Blueprint, abort,render_template,session, redirect, url_for
from app.models import Dish,Order, OrderItem
from flask_login import login_required
from flask_login import login_required,current_user
from app.decorators import role_required
from app.forms import OrderForm
from app import db

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

@main.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    cart = session.get("cart", {})

    if not cart:
        return redirect(url_for("main.menu"))

    form = OrderForm()

    if form.validate_on_submit():
        order = Order(
            user=current_user,
            event_date=form.event_date.data,
            event_time=form.event_time.data,
            address=form.address.data,
            guests_count=form.guests_count.data,
            total_price=0,
            status="confirmed"
        )

        db.session.add(order)
        db.session.flush()  # получаем order.id

        dishes = Dish.query.filter(Dish.id.in_(cart.keys())).all()
        total = 0

        for dish in dishes:
            quantity = cart[str(dish.id)]
            subtotal = dish.price_per_unit * quantity
            total += subtotal

            item = OrderItem(
                order_id=order.id,
                dish_id=dish.id,
                quantity=quantity,
                price=dish.price_per_unit
            )
            db.session.add(item)

        order.total_price = total
        db.session.commit()

        session.pop("cart", None)

        return redirect(url_for("main.client_dashboard"))

    return render_template("checkout.html", form=form)

@main.route("/my-orders")
@login_required
@role_required("client")
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template("my_orders.html", orders=orders)

@main.route("/kitchen/orders")
@login_required
@role_required("kitchen")
def kitchen_orders():
    orders = Order.query.filter(
        Order.status.in_(["confirmed", "cooking"])
    ).all()
    return render_template("kitchen_orders.html", orders=orders)

@main.route("/order/<int:order_id>/status/<status>")
@login_required
@role_required("kitchen")
def update_order_status(order_id, status):
    allowed_statuses = ["cooking", "ready"]

    if status not in allowed_statuses:
        abort(400)

    order = Order.query.get_or_404(order_id)
    order.status = status

    db.session.commit()
    return redirect(url_for("main.kitchen_orders"))

@main.route("/admin/orders")
@login_required
@role_required("admin")
def admin_orders():
    orders = Order.query.all()
    return render_template("admin_orders.html", orders=orders)

@main.route("/kitchen/order/<int:order_id>")
@login_required
@role_required("kitchen")
def kitchen_order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    items = OrderItem.query.filter_by(order_id=order.id).all()

    return render_template(
        "kitchen_order_detail.html",
        order=order,
        items=items
    )
