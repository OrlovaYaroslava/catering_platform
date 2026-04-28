import json
from app import create_app, db
from app.models import User, Dish, Ingredient, DishIngredient, Order, OrderItem

app = create_app()

with app.app_context():
    data = {
        "users": [{"id": u.id, "email": u.email, "password_hash": u.password_hash, 
           "role": u.role.value if hasattr(u.role, 'value') else str(u.role)}
          for u in User.query.all()],
        "ingredients": [{"id": i.id, "name": i.name, "unit": i.unit,
                         "stock_quantity": float(i.stock_quantity),
                         "min_quantity": float(i.min_quantity)}
                        for i in Ingredient.query.all()],
        "dishes": [{"id": d.id, "name": d.name, "price_per_unit": float(d.price_per_unit),
                    "is_active": d.is_active, "description": d.description or "",
                    "category": d.category or "", "is_vegan": d.is_vegan,
                    "is_gluten_free": d.is_gluten_free,
                    "contains_allergens": d.contains_allergens,
                    "image_url": d.image_url or ""}
                   for d in Dish.query.all()],
        "dish_ingredients": [{"dish_id": di.dish_id, "ingredient_id": di.ingredient_id,
                               "amount_per_unit": float(di.amount_per_unit)}
                              for di in DishIngredient.query.all()],
        "orders": [{"id": o.id, "user_id": o.user_id, "status": o.status,
                    "total_price": float(o.total_price),
                    "address": o.address or "",
                    "guests_count": o.guests_count,
                    "is_urgent": o.is_urgent,
                    "kitchen_comment": o.kitchen_comment or "",
                    "event_date": str(o.event_date),
                    "event_time": str(o.event_time),
                    "created_at": str(o.created_at)}
                   for o in Order.query.all()],
        "order_items": [{"id": oi.id, "order_id": oi.order_id, "dish_id": oi.dish_id,
                         "quantity": oi.quantity, "price": float(oi.price)}
                        for oi in OrderItem.query.all()],
    }
    with open("backup_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✅ Данные экспортированы в backup_data.json")
    for k, v in data.items():
        print(f"  {k}: {len(v)} записей")