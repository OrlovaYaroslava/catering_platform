from app import db
from flask_login import UserMixin
from app import login_manager


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    role = db.relationship("Role")

    created_at = db.Column(db.DateTime, default=db.func.now())



class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = db.relationship("User")

    event_date = db.Column(db.Date)
    event_time = db.Column(db.Time)
    address = db.Column(db.String(255))
    guests_count = db.Column(db.Integer)

    total_price = db.Column(db.Numeric(10, 2))
    status = db.Column(db.String(50), default="awaiting_payment")

    created_at = db.Column(db.DateTime, default=db.func.now())
    kitchen_comment = db.Column(db.Text)
    is_urgent = db.Column(db.Boolean, default=False)

# Таблица связи many-to-many между блюдами и тегами
dish_tags = db.Table('dish_tags',
    db.Column('dish_id', db.Integer, db.ForeignKey('dishes.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)


class Dish(db.Model):
    __tablename__ = "dishes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    price_per_unit = db.Column(db.Numeric(10, 2))
    category = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    is_vegan = db.Column(db.Boolean, default=False)
    is_gluten_free = db.Column(db.Boolean, default=False)
    contains_allergens = db.Column(db.Boolean, default=False)
    image_url = db.Column(db.String(255))  
    tags = db.relationship('Tag', secondary=dish_tags, backref='dishes') 
    



class OrderItem(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))
    dish_id = db.Column(db.Integer, db.ForeignKey("dishes.id"))

    quantity = db.Column(db.Integer)
    price = db.Column(db.Numeric(10, 2))

    dish = db.relationship("Dish")


class Ingredient(db.Model):
    __tablename__ = "ingredients"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    unit = db.Column(db.String(50))
    stock_quantity = db.Column(db.Numeric(10, 2))
    min_quantity = db.Column(db.Numeric(10, 2))


class DishIngredient(db.Model):
    __tablename__ = "dish_ingredients"

    dish_id = db.Column(db.Integer, db.ForeignKey("dishes.id"), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredients.id"), primary_key=True)
    amount_per_unit = db.Column(db.Numeric(10, 2))

    dish = db.relationship("Dish")
    ingredient = db.relationship("Ingredient")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id"),
        nullable=False
    )

    method = db.Column(db.String(50))  
    # card / invoice / cash

    status = db.Column(
        db.String(50),
        default="pending"
    )
    # pending / success / failed

    amount = db.Column(db.Numeric(10, 2))

    created_at = db.Column(
        db.DateTime,
        default=db.func.now()
    )

    comment = db.Column(db.String(255))

    order = db.relationship(
        "Order",
        backref=db.backref("payment", uselist=False)
    )


class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<Tag {self.name}>'
    
class IngredientLog(db.Model):
    """Журнал изменений остатков ингредиентов"""
    __tablename__ = "ingredient_logs"
    
    id = db.Column(db.Integer, primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredients.id"), nullable=False)
    
    old_quantity = db.Column(db.Numeric(10, 2), nullable=False)
    new_quantity = db.Column(db.Numeric(10, 2), nullable=False)
    quantity_diff = db.Column(db.Numeric(10, 2))  # Разница (положительная или отрицательная)
    
    comment = db.Column(db.Text)  # Комментарий
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))  # Кто изменил
    
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    # Связи
    ingredient = db.relationship("Ingredient", backref="logs")
    user = db.relationship("User")
    
    def __repr__(self):
        return f'<IngredientLog {self.ingredient.name}: {self.old_quantity} → {self.new_quantity}>'