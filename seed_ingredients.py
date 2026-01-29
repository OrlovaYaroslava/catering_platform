from app import create_app, db
from app.models import Ingredient, Dish, DishIngredient

app = create_app()

with app.app_context():
    chicken = Ingredient(name="Chicken", unit="kg", stock_quantity=50, min_quantity=10)
    lettuce = Ingredient(name="Lettuce", unit="kg", stock_quantity=20, min_quantity=5)
    sauce = Ingredient(name="Caesar sauce", unit="l", stock_quantity=15, min_quantity=3)

    db.session.add_all([chicken, lettuce, sauce])
    db.session.commit()

    caesar = Dish.query.filter_by(name="Chicken Caesar").first()

    links = [
        DishIngredient(dish=caesar, ingredient=chicken, amount_per_unit=0.15),
        DishIngredient(dish=caesar, ingredient=lettuce, amount_per_unit=0.05),
        DishIngredient(dish=caesar, ingredient=sauce, amount_per_unit=0.03),
    ]

    db.session.add_all(links)
    db.session.commit()

    print("Ingredients and norms added")
