from app import create_app, db
from app.models import Dish

app = create_app()

with app.app_context():
    dishes = [
        Dish(
            name="Chicken Caesar",
            description="Classic Caesar salad with chicken",
            price_per_unit=350,
            category="Salads"
        ),
        Dish(
            name="Beef Stroganoff",
            description="Beef with creamy sauce",
            price_per_unit=550,
            category="Hot dishes"
        ),
        Dish(
            name="Chocolate Cake",
            description="Dessert with dark chocolate",
            price_per_unit=250,
            category="Desserts"
        )
    ]

    db.session.add_all(dishes)
    db.session.commit()
    print("Dishes added")
