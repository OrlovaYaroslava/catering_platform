from flask import Blueprint, abort,render_template, request,session, redirect, url_for
from app.models import Dish,Order, OrderItem,DishIngredient, Ingredient, Role, User, Payment
from flask_login import login_required
from flask_login import login_required,current_user
from app.decorators import role_required
from app.forms import OrderForm
from app import db
from collections import defaultdict
from sqlalchemy import func,extract
from datetime import date
from random import choice

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")

@main.route("/client")
@login_required
@role_required("client")
def client_dashboard():
    return render_template("client_dashboard.html")

@main.route("/kitchen")
@login_required
@role_required("kitchen")
def kitchen_dashboard():
    return render_template("kitchen_dashboard.html")

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
        # 1. Создаём заказ со статусом "ожидает оплаты"
        order = Order(
            user=current_user,
            event_date=form.event_date.data,
            event_time=form.event_time.data,
            address=form.address.data,
            guests_count=form.guests_count.data,
            total_price=0,
            status="awaiting_payment"
        )

        db.session.add(order)
        db.session.flush()  # получаем order.id без коммита

        dishes = Dish.query.filter(Dish.id.in_(cart.keys())).all()
        total = 0

        # 2. Создаём позиции заказа
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

        # 3. Фиксируем итоговую сумму заказа
        order.total_price = total

        # 4. Создаём платёж (ещё НЕ оплачен)
        payment = Payment(
            order_id=order.id,
            amount=order.total_price,
            status="pending"
        )
        db.session.add(payment)

        # 5. Сохраняем всё разом
        db.session.commit()

        # 6. Очищаем корзину
        session.pop("cart", None)

        # 7. Переход к странице заказа (а не просто в кабинет)
        return redirect(
            url_for("main.client_order_detail", order_id=order.id)
        )

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

@main.route("/admin/dashboard")
@login_required
@role_required("admin")
def admin_dashboard():
    # Общее количество заказов
    total_orders = Order.query.count()

    # Общая выручка
    total_revenue = db.session.query(
        func.coalesce(func.sum(Order.total_price), 0)
    ).scalar()

    # Количество клиентов
    total_clients = User.query.join(Role).filter(Role.name == "client").count()

    # Топ-5 блюд по количеству заказов
    top_dishes = (
        db.session.query(
            Dish.name,
            func.sum(OrderItem.quantity).label("total_quantity")
        )
        .join(OrderItem, Dish.id == OrderItem.dish_id)
        .group_by(Dish.name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(5)
        .all()
    )

    return render_template(
        "admin_dashboard.html",
        total_orders=total_orders,
        total_revenue=round(float(total_revenue), 2),
        total_clients=total_clients,
        top_dishes=top_dishes
    )

@main.route("/admin/analytics/period")
@login_required
@role_required("admin")
def analytics_period():
    # Период по умолчанию — текущий месяц
    today = date.today()
    start_date = date(today.year, today.month, 1)

    orders = Order.query.filter(Order.created_at >= start_date).all()

    total_orders = len(orders)
    total_revenue = sum(float(order.total_price) for order in orders)

    return render_template(
        "analytics_period.html",
        start_date=start_date,
        total_orders=total_orders,
        total_revenue=round(total_revenue, 2)
    )

@main.route("/admin/analytics/monthly")
@login_required
@role_required("admin")
def analytics_monthly():
    monthly_stats = (
        db.session.query(
            extract("year", Order.created_at).label("year"),
            extract("month", Order.created_at).label("month"),
            func.count(Order.id).label("orders_count"),
            func.sum(Order.total_price).label("revenue")
        )
        .group_by("year", "month")
        .order_by("year", "month")
        .all()
    )

    return render_template(
        "analytics_monthly.html",
        stats=monthly_stats
    )

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

@main.route("/kitchen/order/<int:order_id>/ingredients")
@login_required
@role_required("kitchen")
def kitchen_order_ingredients(order_id):
    order = Order.query.get_or_404(order_id)
    items = OrderItem.query.filter_by(order_id=order.id).all()

    ingredient_data = {}

    
    for item in items:
        links = DishIngredient.query.filter_by(dish_id=item.dish_id).all()
        for link in links:
            required = round(float(link.amount_per_unit) * item.quantity, 2)

            if link.ingredient.id not in ingredient_data:
                ingredient_data[link.ingredient.id] = {
                    "ingredient": link.ingredient,
                    "required": 0
                }

            ingredient_data[link.ingredient.id]["required"] += required

   
    for data in ingredient_data.values():
        ingredient = data["ingredient"]
        required = data["required"]

        data["in_stock"] = float(ingredient.stock_quantity)
        data["deficit"] = max(0, round(required - data["in_stock"], 2))

    
    return render_template(
        "kitchen_order_ingredients.html",
        order=order,
        ingredients=ingredient_data.values()
    )

@main.route("/client/orders/<int:order_id>")
@login_required
@role_required("client")
def client_order_detail(order_id):
    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()

    items = OrderItem.query.filter_by(order_id=order.id).all()

    payment = order.payment  # связь uselist=False

    return render_template(
        "client_order_detail.html",
        order=order,
        items=items,
        payment=payment
    )

from random import choice
from flask import request, redirect, url_for, render_template
from flask_login import login_required, current_user

@main.route("/payment/<int:order_id>", methods=["GET", "POST"])
@login_required
@role_required("client")
def payment_page(order_id):
    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()

    payment = order.payment

    # Если заказ уже оплачен — повторно платить нельзя
    if payment.status == "success":
        return redirect(
            url_for("main.client_order_detail", order_id=order.id)
        )

    if request.method == "POST":
        method = request.form.get("method")
        payment.method = method

        # 💳 Оплата картой (имитация)
        if method == "card":
            result = choice(["success", "success", "failed"])
            payment.status = result

            if result == "success":
                order.status = "paid"
            else:
                order.status = "awaiting_payment"

            db.session.commit()

            return redirect(
                url_for("main.client_order_detail", order_id=order.id)
            )

        # 💵 Наличные курьеру (считаем подтверждёнными)
        if method == "cash":
            payment.status = "success"
            order.status = "paid"

            db.session.commit()

            return redirect(
                url_for("main.client_order_detail", order_id=order.id)
            )

        # 🧾 Безналичный расчёт по счёту (юрлица)
        if method == "invoice":
            payment.status = "pending"
            order.status = "awaiting_payment"

            payment.comment = f"""
            Организация: {request.form.get('company_name')}
            ИНН: {request.form.get('inn')}
            КПП: {request.form.get('kpp')}
            Юридический адрес: {request.form.get('legal_address')}
            Email бухгалтера: {request.form.get('accountant_email')}
            """

            db.session.commit()

            # 👉 Переход на страницу счёта
            return redirect(
                url_for("main.invoice_page", order_id=order.id)
            )

    return render_template(
        "payment_page.html",
        order=order,
        payment=payment
    )

@main.route("/payment/invoice/<int:order_id>")
@login_required
@role_required("client")
def invoice_page(order_id):
    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()

    payment = order.payment

    if payment.method != "invoice":
        return redirect(
            url_for("main.client_order_detail", order_id=order.id)
        )

    return render_template(
        "invoice.html",
        order=order,
        payment=payment
    )
