from app import create_app, db
from app.models import Dish, User, Ingredient, Order, Role, Tag

app = create_app()

with app.app_context():
    print("=" * 40)
    print("ПОЛЬЗОВАТЕЛИ:")
    for u in User.query.all():
        role_name = u.role.name if u.role else "нет роли"
        print(f"  id={u.id} | {u.email} | роль: {role_name}")

    print("=" * 40)
    print("БЛЮДА:")
    for d in Dish.query.all():
        print(f"  id={d.id} | {d.name} | {d.price_per_unit} руб. | активно: {d.is_active}")

    print("=" * 40)
    print("ИНГРЕДИЕНТЫ:")
    for i in Ingredient.query.all():
        print(f"  id={i.id} | {i.name} | {i.stock_quantity} {i.unit}")

    print("=" * 40)
    print("ЗАКАЗЫ:")
    for o in Order.query.all():
        print(f"  id={o.id} | статус: {o.status} | сумма: {o.total_price}")

    print("=" * 40)
    print(f"ИТОГО: {User.query.count()} польз. | {Dish.query.count()} блюд | {Ingredient.query.count()} ингред. | {Order.query.count()} заказов")
    print("=" * 40)
    print("ТЕХНОЛОГИЧЕСКИЕ КАРТЫ (блюдо → ингредиент):")
    from app.models import DishIngredient
    cards = DishIngredient.query.all()
    if not cards:
        print("  ❌ ПУСТО — технологических карт нет!")
    else:
        for c in cards:
            print(f"  {c.dish.name} → {c.ingredient.name}: {c.amount_per_unit} {c.ingredient.unit}")
    print(f"  ИТОГО записей: {DishIngredient.query.count()}")