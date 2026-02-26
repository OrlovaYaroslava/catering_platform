from flask import Blueprint, abort, flash,render_template, request,session, redirect, url_for
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
    popular_dishes = Dish.query.filter_by(is_active=True).limit(6).all()
    return render_template("index.html", popular_dishes=popular_dishes)

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
def menu():
    dishes = Dish.query.filter_by(is_active=True).all()
    return render_template("menu.html", dishes=dishes)

@main.route("/add_to_cart/<int:dish_id>", methods=["POST"])
@login_required
@role_required("client")
def add_to_cart(dish_id):
    quantity = int(request.form.get("quantity", 1))

    cart = session.get("cart", {})

    dish_id_str = str(dish_id)

    if dish_id_str in cart:
        cart[dish_id_str] += quantity
    else:
        cart[dish_id_str] = quantity

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
        Order.status.in_(["paid", "cooking", "ready"])
    ).order_by(
        Order.event_date,
        Order.event_time
    ).all()

    return render_template(
        "kitchen_orders.html",
        orders=orders
    )


@main.route("/order/<int:order_id>/status/<status>")
@login_required
@role_required("kitchen")
def update_order_status(order_id, status):
    allowed_statuses = ["cooking", "ready", "completed"]

    if status not in allowed_statuses:
        abort(400)

    order = Order.query.get_or_404(order_id)
    old_status = order.status
    order.status = status

    # 🔥 Списываем ингредиенты, если заказ стал готовым/выполненным 🔥
    if status in ["ready", "completed"] and old_status not in ["ready", "completed"]:
        deduct_ingredients_for_order(order)
        flash("✅ Ингредиенты списаны со склада", "success")

    db.session.commit()
    return redirect(url_for("main.kitchen_orders"))

@main.route("/kitchen/orders/<int:order_id>")
@login_required
@role_required("kitchen")
def kitchen_order_detail(order_id):
    order = Order.query.get_or_404(order_id)

    if order.status not in ["paid", "cooking", "ready"]:
        abort(403)

    items = OrderItem.query.filter_by(order_id=order.id).all()

    return render_template(
        "kitchen_order_detail.html",
        order=order,
        items=items
    )

@main.route("/kitchen/orders/<int:order_id>/start", methods=["POST"])
@login_required
@role_required("kitchen")
def kitchen_start_order(order_id):
    order = Order.query.get_or_404(order_id)

    if order.status == "paid":
        order.status = "cooking"
        db.session.commit()

    return redirect(
        url_for("main.kitchen_order_detail", order_id=order.id)
    )

@main.route("/kitchen/board")
@login_required
@role_required("kitchen")
def kitchen_board():

    orders_paid = Order.query.filter_by(status="paid").order_by(
        Order.is_urgent.desc(),
        Order.event_date,
        Order.event_time
    ).all()

    orders_cooking = Order.query.filter_by(status="cooking").order_by(
        Order.is_urgent.desc(),
        Order.event_date,
        Order.event_time
    ).all()

    orders_ready = Order.query.filter_by(status="ready").order_by(
        Order.is_urgent.desc(),
        Order.event_date,
        Order.event_time
    ).all()

    # 👇 ВОТ ЭТО НОВОЕ (KPI)
    today = date.today()

    orders_today = Order.query.filter(
        Order.event_date == today,
        Order.status.in_(["paid", "cooking", "ready"])
    ).count()

    return render_template(
        "kitchen_board.html",
        orders_paid=orders_paid,
        orders_cooking=orders_cooking,
        orders_ready=orders_ready,
        orders_today=orders_today  # 👈 передаём в шаблон
    )

def deduct_ingredients_for_order(order):
    order_items = OrderItem.query.filter_by(order_id=order.id).all()
    deficit_warnings = []
    
    for item in order_items:
        dish_ingredients = DishIngredient.query.filter_by(dish_id=item.dish_id).all()
        
        for di in dish_ingredients:
            ingredient = Ingredient.query.get(di.ingredient_id)
            if ingredient:
                amount_needed = float(di.amount_per_unit) * item.quantity
                
                # Проверяем, хватит ли
                if ingredient.stock_quantity < amount_needed:
                    deficit_warnings.append(
                        f"{ingredient.name}: нужно {amount_needed}, есть {ingredient.stock_quantity}"
                    )
                
                # Списываем (не уходит в минус)
                ingredient.stock_quantity = max(0, ingredient.stock_quantity - amount_needed)
    
    db.session.commit()
    
    # Показываем предупреждения, если был дефицит
    if deficit_warnings:
        flash("⚠️ Дефицит ингредиентов: " + "; ".join(deficit_warnings), "warning")

def deduct_ingredients_for_order(order):
    """
    Автоматически списывает ингредиенты для заказа.
    Вызывается когда заказ переходит в статус "ready" или "completed".
    """
    from decimal import Decimal  # 👈 Импортируем Decimal
    
    # Получаем все позиции заказа
    order_items = OrderItem.query.filter_by(order_id=order.id).all()
    
    for item in order_items:
        # Получаем технологическую карту блюда
        dish_ingredients = DishIngredient.query.filter_by(dish_id=item.dish_id).all()
        
        for di in dish_ingredients:
            ingredient = Ingredient.query.get(di.ingredient_id)
            if ingredient:
                # 👇 ВАЖНО: Преобразуем всё к Decimal
                amount_needed = Decimal(str(float(di.amount_per_unit) * item.quantity))
                current_stock = Decimal(str(ingredient.stock_quantity or 0))
                
                # Списываем со склада (не уходит в минус)
                new_stock = max(Decimal('0'), current_stock - amount_needed)
                ingredient.stock_quantity = new_stock
    
    # Сохраняем изменения в БД
    db.session.commit()

@main.route("/kitchen/orders/<int:order_id>/finish", methods=["POST"])
@login_required
@role_required("kitchen")
def kitchen_finish_order(order_id):
    order = Order.query.get_or_404(order_id)

    if order.status == "cooking":
        order.status = "ready"
        
        # 🔥 АВТОМАТИЧЕСКОЕ СПИСАНИЕ ИНГРЕДИЕНТОВ 🔥
        deduct_ingredients_for_order(order)
        
        db.session.commit()
        
        flash("✅ Заказ готов! Ингредиенты списаны со склада", "success")

    return redirect(
        url_for("main.kitchen_order_detail", order_id=order.id)
    )

@main.route("/kitchen/report")
@login_required
@role_required("kitchen")
def kitchen_report():
    selected_date = request.args.get("date")

    if selected_date:
        report_date = selected_date
    else:
        report_date = date.today().isoformat()

    orders = Order.query.filter(
        Order.event_date == report_date,
        Order.status.in_(["paid", "cooking"])
    ).all()

    # 🔹 АГРЕГАЦИЯ БЛЮД
    dishes_summary = defaultdict(int)

    # 🔹 АГРЕГАЦИЯ ИНГРЕДИЕНТОВ
    ingredients_summary = defaultdict(float)

    for order in orders:
        order_items = OrderItem.query.filter_by(order_id=order.id).all()

        for item in order_items:
            # Считаем блюда
            dishes_summary[item.dish.name] += item.quantity

            # Получаем технологическую карту блюда
            dish_links = DishIngredient.query.filter_by(
                dish_id=item.dish_id
            ).all()

            for link in dish_links:
                total_amount = float(link.amount_per_unit) * item.quantity
                ingredients_summary[link.ingredient.name] += round(total_amount, 2)

    return render_template(
        "kitchen_report.html",
        orders=orders,
        report_date=report_date,
        dishes_summary=dishes_summary,
        ingredients_summary=ingredients_summary
    )


@main.route("/admin/orders")
@login_required
@role_required("admin")
def admin_orders():
    # Получаем параметры фильтрации
    status_filter = request.args.get("status", "all")  # all, new, paid, cooking, ready, completed
    search_query = request.args.get("search", "")  # Поиск по номеру или email
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")
    sort_by = request.args.get("sort", "created_at_desc")  # created_at_desc, created_at_asc, amount_desc, amount_asc
    
    # Базовый запрос
    query = Order.query
    
    # Фильтр по статусу
    if status_filter != "all":
        query = query.filter(Order.status == status_filter)
    
    # Поиск
    if search_query:
        # Ищем по ID заказа или email клиента
        if search_query.isdigit():
            query = query.filter(Order.id == int(search_query))
        else:
            query = query.join(User).filter(User.email.ilike(f"%{search_query}%"))
    
    # Фильтр по дате
    if date_from:
        query = query.filter(Order.event_date >= datetime.strptime(date_from, "%Y-%m-%d").date())
    if date_to:
        query = query.filter(Order.event_date <= datetime.strptime(date_to, "%Y-%m-%d").date())
    
    # Сортировка
    if sort_by == "created_at_asc":
        query = query.order_by(Order.created_at.asc())
    elif sort_by == "amount_desc":
        query = query.order_by(Order.total_price.desc())
    elif sort_by == "amount_asc":
        query = query.order_by(Order.total_price.asc())
    else:  # created_at_desc (по умолчанию)
        query = query.order_by(Order.created_at.desc())
    
    orders = query.all()
    
    # Статистика по статусам (для бейджей)
    status_counts = {
        "all": Order.query.count(),
        "new": Order.query.filter(Order.status == "new").count(),
        "awaiting_payment": Order.query.filter(Order.status == "awaiting_payment").count(),
        "paid": Order.query.filter(Order.status == "paid").count(),
        "cooking": Order.query.filter(Order.status == "cooking").count(),
        "ready": Order.query.filter(Order.status == "ready").count(),
        "completed": Order.query.filter(Order.status == "completed").count(),
    }
    
    return render_template(
        "admin_orders.html",
        orders=orders,
        status_counts=status_counts,
        current_status=status_filter,
        search_query=search_query,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by
    )

@main.route("/admin/dashboard")
@login_required
@role_required("admin")
def admin_dashboard():
    from datetime import datetime, timedelta
    
    # Получаем даты из query params
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")
    
    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    else:
        # По умолчанию — текущий месяц
        today = date.today()
        start_date = date(today.year, today.month, 1)
        end_date = today
    
    # Фильтр заказов по периоду
    orders = Order.query.filter(
        Order.created_at >= start_date,
        Order.created_at <= end_date
    ).all()
    
    # КЛЮЧЕВЫЕ ПОКАЗАТЕЛИ
    total_orders = len(orders)
    total_revenue = sum(float(order.total_price) for order in orders)
    avg_check = round(total_revenue / total_orders, 2) if total_orders > 0 else 0
    
    # Количество клиентов
    total_clients = User.query.join(Role).filter(Role.name == "client").count()
    
    # ТОП БЛЮД ПО ВЫРУЧКЕ
    top_dishes = (
        db.session.query(
            Dish.name,
            func.sum(OrderItem.quantity).label("quantity"),
            func.sum(OrderItem.quantity * OrderItem.price).label("revenue")
        )
        .join(OrderItem, Dish.id == OrderItem.dish_id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.created_at >= start_date, Order.created_at <= end_date)
        .group_by(Dish.name)
        .order_by(func.sum(OrderItem.quantity * OrderItem.price).desc())
        .limit(5)
        .all()
    )
    
    # ТОП КЛИЕНТОВ
    top_clients = (
        db.session.query(
            User.email,
            func.count(Order.id).label("orders_count"),
            func.sum(Order.total_price).label("total_spent")
        )
        .join(Order, User.id == Order.user_id)
        .filter(Order.created_at >= start_date, Order.created_at <= end_date)
        .group_by(User.email)
        .order_by(func.sum(Order.total_price).desc())
        .limit(5)
        .all()
    )
    
    # ВОРОНКА ПРОДАЖ
    # Считаем количество заказов на каждом этапе
    created_count = Order.query.filter(
        Order.created_at >= start_date,
        Order.created_at <= end_date
    ).count()
    
    paid_count = Order.query.filter(
        Order.status == "paid",
        Order.created_at >= start_date,
        Order.created_at <= end_date
    ).count()
    
    cooking_count = Order.query.filter(
        Order.status == "cooking",
        Order.created_at >= start_date,
        Order.created_at <= end_date
    ).count()
    
    ready_count = Order.query.filter(
        Order.status == "ready",
        Order.created_at >= start_date,
        Order.created_at <= end_date
    ).count()
    
    completed_count = Order.query.filter(
        Order.status.in_(["ready", "completed"]),
        Order.created_at >= start_date,
        Order.created_at <= end_date
    ).count()
    
    # Формируем словарь funnel
    funnel = {
        "created": created_count,
        "paid": paid_count,
        "cooking": cooking_count,
        "ready": ready_count,
        "completed": completed_count,
        
        # ✅ ВСЕ проценты считаются ОТ СОЗДАННЫХ (created_count)!
        "paid_percent": round(paid_count / created_count * 100, 1) if created_count > 0 else 0,
        "cooking_percent": round(cooking_count / created_count * 100, 1) if created_count > 0 else 0,
        "ready_percent": round(ready_count / created_count * 100, 1) if created_count > 0 else 0,
        "completed_percent": round(completed_count / created_count * 100, 1) if created_count > 0 else 0,
    }
    
    # ГРАФИК: Выручка по дням
    from collections import defaultdict
    revenue_by_day = defaultdict(float)
    for order in orders:
        day_key = order.created_at.strftime("%Y-%m-%d")
        revenue_by_day[day_key] += float(order.total_price)
    
    revenue_labels = list(revenue_by_day.keys())
    revenue_data = list(revenue_by_day.values())
    
    # ГРАФИК: Статусы заказов
    status_counts = defaultdict(int)
    for order in orders:
        status_counts[order.status] += 1
    
    status_data = [
        status_counts.get("awaiting_payment", 0),
        status_counts.get("paid", 0),
        status_counts.get("cooking", 0),
        status_counts.get("ready", 0),
        status_counts.get("completed", 0),
    ]
    
    return render_template(
        "admin_dashboard.html",
        total_orders=total_orders,
        total_revenue=round(total_revenue, 2),
        avg_check=avg_check,
        total_clients=total_clients,
        top_dishes=top_dishes,
        top_clients=top_clients,
        funnel=funnel,
        revenue_labels=revenue_labels,
        revenue_data=revenue_data,
        status_data=status_data,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat()
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


@main.route("/admin/order/<int:order_id>/confirm-payment", methods=["POST"])
@login_required
@role_required("admin")
def admin_confirm_payment(order_id):
    order = Order.query.get_or_404(order_id)
    payment = order.payment

    # защита: подтверждать можно только безнал
    if payment.method != "invoice" or payment.status != "pending":
        return redirect(
            url_for("main.admin_order_detail", order_id=order.id)
        )

    # подтверждаем оплату
    payment.status = "success"
    order.status = "paid"

    db.session.commit()

    return redirect(
        url_for("main.admin_order_detail", order_id=order.id)
    )

@main.route("/admin/order/<int:order_id>/comment", methods=["POST"])
@login_required
@role_required("admin")
def admin_update_kitchen_comment(order_id):
    order = Order.query.get_or_404(order_id)

    comment = request.form.get("kitchen_comment")
    urgent = request.form.get("is_urgent")

    order.kitchen_comment = comment if comment else None
    order.is_urgent = True if urgent == "on" else False

    db.session.commit()

    return redirect(url_for("main.admin_order_detail", order_id=order.id))


@main.route("/admin/orders/<int:order_id>")
@login_required
@role_required("admin")
def admin_order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    items = OrderItem.query.filter_by(order_id=order.id).all()
    payment = order.payment

    return render_template(
        "admin_order_detail.html",
        order=order,
        items=items,
        payment=payment
    )

@main.route("/kitchen/order/<int:order_id>/ingredients")
@login_required
@role_required("kitchen")
def kitchen_order_ingredients(order_id):
    order = Order.query.get_or_404(order_id)
    items = OrderItem.query.filter_by(order_id=order.id).all()

    ingredient_data = {}

    # Считаем требуемые ингредиенты
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

    # Добавляем данные о наличии и дефиците
    for data in ingredient_data.values():
        ingredient = data["ingredient"]
        required = data["required"]
        data["in_stock"] = float(ingredient.stock_quantity or 0)
        data["deficit"] = max(0, round(required - data["in_stock"], 2))

    # 🔧 ВАЖНО: Преобразуем dict_values в список!
    ingredients_list = list(ingredient_data.values())

    return render_template(
        "kitchen_order_ingredients.html",
        order=order,
        ingredients=ingredients_list  # ✅ Теперь это список
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

@main.route("/about")
def about():
    """Страница о компании"""
    return render_template("about.html")

@main.route("/contacts")
def contacts():
    """Страница контактов"""
    return render_template("contacts.html")

@main.route("/admin/ingredients")
@login_required
@role_required("admin")
def admin_ingredients():
    ingredients = Ingredient.query.all()
    
    # Статусы для каждого ингредиента
    ingredients_data = []
    total_fill = 0
    deficit_count = 0
    low_stock_count = 0
    
    for ing in ingredients:
        if ing.stock_quantity <= 0:
            status = "deficit"
            deficit_count += 1
        elif ing.stock_quantity < ing.min_quantity:
            status = "low"
            low_stock_count += 1
        else:
            status = "ok"
        
        # Расчёт заполненности
        if ing.min_quantity > 0:
            fill = min(100, round(ing.stock_quantity / ing.min_quantity * 100, 1))
            total_fill += fill
        
        ingredients_data.append({
            "id": ing.id,
            "name": ing.name,
            "stock_quantity": ing.stock_quantity,
            "unit": ing.unit,
            "min_quantity": ing.min_quantity,
            "status": status
        })
    
    avg_fill = round(total_fill / len(ingredients), 1) if ingredients else 0
    
    return render_template(
        "admin_ingredients.html",
        ingredients=ingredients_data,
        stock_fill=avg_fill,
        deficit_count=deficit_count,
        low_stock_count=low_stock_count
    )

@main.route("/admin/ingredient/update", methods=["POST"])
@login_required
@role_required("admin")
def admin_update_ingredient():
    from app.models import IngredientLog  # 👈 Импортируем лог
    
    ingredient_id = request.form.get("ingredient_id")
    new_stock = float(request.form.get("new_stock"))
    comment = request.form.get("comment", "").strip()
    
    ingredient = Ingredient.query.get_or_404(ingredient_id)
    old_stock = float(ingredient.stock_quantity or 0)
    
    # Обновляем остаток
    ingredient.stock_quantity = new_stock
    
    # 👇 Создаём запись в журнале
    log = IngredientLog(
        ingredient_id=ingredient.id,
        old_quantity=old_stock,
        new_quantity=new_stock,
        quantity_diff=new_stock - old_stock,
        comment=comment if comment else None,
        user_id=current_user.id
    )
    db.session.add(log)
    
    db.session.commit()
    
    flash(f"✅ Остаток обновлён: {old_stock} → {new_stock}" + 
          (f" ({comment})" if comment else ""), "success")
    
    return redirect(url_for("main.admin_ingredients"))

@main.route("/admin/ingredient/<int:ingredient_id>/history")
@login_required
@role_required("admin")
def ingredient_history(ingredient_id):
    """История изменений ингредиента"""
    from app.models import IngredientLog
    
    ingredient = Ingredient.query.get_or_404(ingredient_id)
    logs = (IngredientLog.query
            .filter_by(ingredient_id=ingredient_id)
            .order_by(IngredientLog.created_at.desc())
            .limit(50)
            .all())
    
    return render_template(
        "ingredient_history.html",
        ingredient=ingredient,
        logs=logs
    )