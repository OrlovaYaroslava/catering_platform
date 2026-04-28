import json
from app import create_app, db
from app.models import User, Dish, Ingredient, DishIngredient, Order, OrderItem

app = create_app()

with app.app_context():
    db.create_all()
    
    with open("backup_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Пользователи
    for u in data["users"]:
        if not User.query.get(u["id"]):
            user = User(id=u["id"], email=u["email"], role=u["role"])
            user.password_hash = u["password_hash"]
            db.session.add(user)
    db.session.commit()
    print(f"✅ Пользователи: {len(data['users'])}")

    # Ингредиенты
    for i in data["ingredients"]:
        if not Ingredient.query.get(i["id"]):
            ing = Ingredient(id=i["id"], name=i["name"], unit=i["unit"],
                             stock_quantity=i["stock_quantity"],
                             min_quantity=i["min_quantity"])
            db.session.add(ing)
    db.session.commit()
    print(f"✅ Ингредиенты: {len(data['ingredients'])}")

    # Блюда
    for d in data["dishes"]:
        if not Dish.query.get(d["id"]):
            dish = Dish(id=d["id"], name=d["name"], price_per_unit=d["price_per_unit"],
                        is_active=d["is_active"], description=d["description"],
                        category=d["category"], is_vegan=d["is_vegan"],
                        is_gluten_free=d["is_gluten_free"],
                        contains_allergens=d["contains_allergens"],
                        image_url=d["image_url"])
            db.session.add(dish)
    db.session.commit()
    print(f"✅ Блюда: {len(data['dishes'])}")

    # Технологические карты
    for di in data["dish_ingredients"]:
        exists = DishIngredient.query.filter_by(
            dish_id=di["dish_id"], ingredient_id=di["ingredient_id"]).first()
        if not exists:
            card = DishIngredient(dish_id=di["dish_id"],
                                  ingredient_id=di["ingredient_id"],
                                  amount_per_unit=di["amount_per_unit"])
            db.session.add(card)
    db.session.commit()
    print(f"✅ Технологические карты: {len(data['dish_ingredients'])}")

    # Заказы
    for o in data["orders"]:
        if not Order.query.get(o["id"]):
            order = Order(id=o["id"], user_id=o["user_id"], status=o["status"],
                          total_price=o["total_price"], address=o["address"],
                          guests_count=o["guests_count"], is_urgent=o["is_urgent"],
                          kitchen_comment=o["kitchen_comment"] or None,
                          event_date=o["event_date"], event_time=o["event_time"])
            db.session.add(order)
    db.session.commit()
    print(f"✅ Заказы: {len(data['orders'])}")

    # Позиции заказов
    for oi in data["order_items"]:
        if not OrderItem.query.get(oi["id"]):
            item = OrderItem(id=oi["id"], order_id=oi["order_id"],
                             dish_id=oi["dish_id"], quantity=oi["quantity"],
                             price=oi["price"])
            db.session.add(item)
    db.session.commit()
    print(f"✅ Позиции заказов: {len(data['order_items'])}")

    print("\n🎉 Все данные импортированы успешно!")