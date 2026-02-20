from app import create_app, db
from app.models import Dish, Ingredient, DishIngredient, Tag, Role, User
from werkzeug.security import generate_password_hash
import random  # 👈 импортируем в начале

app = create_app()

def get_image_url(category, dish_name=None):
    """Возвращает URL реального фото для блюда"""
    
    # Словарь с фото для КАЖДОГО блюда
    dish_images = {
        # САЛАТЫ
        "Цезарь с курицей": "https://images.unsplash.com/photo-1546793665-c74683f339c1?w=400&h=300&fit=crop",
        "Цезарь с креветками": "https://images.unsplash.com/photo-1550304943-4f24f54ddde9?w=400&h=300&fit=crop",
        "Греческий салат": "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=400&h=300&fit=crop",
        "Капрезе": "https://images.unsplash.com/photo-1529312266912-b33cf6227e24?w=400&h=300&fit=crop",
        "Оливье": "https://images.unsplash.com/photo-1603073477944-39d4b1c2d866?w=400&h=300&fit=crop",
        
        # ГОРЯЧИЕ БЛЮДА
        "Бефстроганов": "https://images.unsplash.com/photo-1432139509613-5c4255815697?w=400&h=300&fit=crop",
        "Лосось на гриле": "https://images.unsplash.com/photo-1467003909585-2f8a7270028d?w=400&h=300&fit=crop",
        "Куриная грудка с овощами": "https://images.unsplash.com/photo-1604908176997-125f27cc2d4d?w=400&h=300&fit=crop",
        "Паста Карбонара": "https://images.unsplash.com/photo-1473093295043-cdd812d0e601?w=400&h=300&fit=crop",
        "Ризотто с грибами": "https://images.unsplash.com/photo-1476124369491-e7addf5db371?w=400&h=300&fit=crop",
        "Стейк Рибай": "https://images.unsplash.com/photo-1600891964092-4316c288032e?w=400&h=300&fit=crop",
        "Плов с курицей": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=400&h=300&fit=crop",
        
        # ЗАКУСКИ
        "Брускетта с томатами": "https://images.unsplash.com/photo-1572656631137-7935b80a2f52?w=400&h=300&fit=crop",
        "Тарталетки с икрой": "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=400&h=300&fit=crop",
        "Куриные крылышки BBQ": "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=400&h=300&fit=crop",
        "Канапе ассорти": "https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=400&h=300&fit=crop",
        
        # СУПЫ
        "Грибной суп-пюре": "https://images.unsplash.com/photo-1547592166-23ac45744acd?w=400&h=300&fit=crop",
        "Куриный бульон": "https://images.unsplash.com/photo-1547592166-23ac45744acd?w=400&h=300&fit=crop",
        "Солянка сборная": "https://images.unsplash.com/photo-1547592166-23ac45744acd?w=400&h=300&fit=crop",
        
        # ДЕСЕРТЫ
        "Тирамису": "https://images.unsplash.com/photo-1571875257727-256c39da42af?w=400&h=300&fit=crop",
        "Шоколадный торт": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400&h=300&fit=crop",
        "Чизкейк Нью-Йорк": "https://images.unsplash.com/photo-1533134242443-d4fd2160c5c9?w=400&h=300&fit=crop",
        "Фруктовая тарелка": "https://images.unsplash.com/photo-1519996529931-28324d5a630e?w=400&h=300&fit=crop",
        "Панна-котта": "https://images.unsplash.com/photo-1488477181946-6428a0b7147b?w=400&h=300&fit=crop",
        
        # НАПИТКИ
        "Лимонад домашний": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=400&h=300&fit=crop",
        "Морс клюквенный": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400&h=300&fit=crop",
    }
    
    # Если есть точное совпадение по названию блюда
    if dish_name and dish_name in dish_images:
        return dish_images[dish_name]
    
    # Иначе возвращаем фото по категории
    category_images = {
        "Салаты": "https://images.unsplash.com/photo-1546793665-c74683f339c1?w=400&h=300&fit=crop",
        "Горячее": "https://images.unsplash.com/photo-1432139509613-5c4255815697?w=400&h=300&fit=crop",
        "Закуски": "https://images.unsplash.com/photo-1572656631137-7935b80a2f52?w=400&h=300&fit=crop",
        "Супы": "https://images.unsplash.com/photo-1547592166-23ac45744acd?w=400&h=300&fit=crop",
        "Десерты": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400&h=300&fit=crop",
        "Напитки": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=400&h=300&fit=crop",
        "Паста": "https://images.unsplash.com/photo-1473093295043-cdd812d0e601?w=400&h=300&fit=crop",
    }
    
    return category_images.get(category, "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400&h=300&fit=crop")
with app.app_context():
    print("🌱 Наполнение базы данных...")
    
    # 1. Теги
    tags_data = [
        ("Вегетарианское", ""), ("Веганское", ""), ("Без глютена", ""),
        ("Детское", ""), ("Без лактозы", ""), ("Содержит аллергены", ""),
        ("Острое", ""), ("Низкокалорийное", ""), ("Премиум", ""), ("Хит", ""),
    ]
    tags = {}
    for name, desc in tags_data:
        tag = Tag.query.filter_by(name=name).first()
        if not tag:
            tag = Tag(name=name, description=desc)
            db.session.add(tag)
        tags[name] = tag
    
    # 2. Ингредиенты
    ingredients_data = [
        ("Куриное филе", "кг", 50.0, 5.0), ("Говядина", "кг", 30.0, 5.0),
        ("Лосось", "кг", 20.0, 3.0), ("Салат Айсберг", "кг", 15.0, 2.0),
        ("Помидоры", "кг", 25.0, 3.0), ("Сыр пармезан", "кг", 8.0, 1.0),
        ("Сливки 20%", "л", 15.0, 2.0), ("Шоколад тёмный", "кг", 10.0, 2.0),
        ("Яйца", "шт", 200.0, 50.0), ("Грибы шампиньоны", "кг", 15.0, 3.0),
    ]
    ingredients = {}
    for name, unit, stock, min_qty in ingredients_data:
        ing = Ingredient.query.filter_by(name=name).first()
        if not ing:
            ing = Ingredient(name=name, unit=unit, stock_quantity=stock, min_quantity=min_qty)
            db.session.add(ing)
        ingredients[name] = ing
    
    # 3. Блюда с фото
    dishes_data = [
        ("Цезарь с курицей", "Классический салат", 350, "Салаты", ["Хит"]),
        ("Греческий салат", "Свежие овощи и фета", 320, "Салаты", ["Вегетарианское", "Без глютена"]),
        ("Бефстроганов", "Говядина в сливочном соусе", 550, "Горячее", ["Хит"]),
        ("Лосось на гриле", "Филе с овощами", 750, "Горячее", ["Без глютена", "Премиум"]),
        ("Грибной суп-пюре", "Крем-суп из шампиньонов", 280, "Супы", ["Вегетарианское"]),
        ("Тирамису", "Итальянский десерт", 300, "Десерты", ["Вегетарианское", "Хит"]),
        ("Шоколадный торт", "Торт из тёмного шоколада", 250, "Десерты", ["Вегетарианское"]),
    ]
    
    dishes = {}
    for name, desc, price, category, tag_names in dishes_data:
        dish = Dish.query.filter_by(name=name).first()
        if not dish:
            # 📸 Генерируем URL с исправленной функцией
            image_url = get_image_url(category)
            
            dish = Dish(
                name=name, description=desc, price_per_unit=price,
                category=category, is_active=True,
                image_url=image_url  # 👈 теперь поле существует в модели
            )
            for tag_name in tag_names:
                if tag_name in tags:
                    dish.tags.append(tags[tag_name])
            db.session.add(dish)
        dishes[name] = dish
    
    # 4. Технологические карты (без изменений)
    print("\n📋 Создаём технологические карты...")
    tech_cards = [
        ("Цезарь с курицей", "Куриное филе", 0.15),
        ("Цезарь с курицей", "Салат Айсберг", 0.1),
        ("Бефстроганов", "Говядина", 0.2),
        ("Грибной суп-пюре", "Грибы шампиньоны", 0.2),
    ]
    
    count = 0
    for dish_name, ing_name, amount in tech_cards:
        if dish_name in dishes and ing_name in ingredients:
            existing = DishIngredient.query.filter_by(
                dish_id=dishes[dish_name].id,
                ingredient_id=ingredients[ing_name].id
            ).first()
            if not existing:
                link = DishIngredient(
                    dish_id=dishes[dish_name].id,
                    ingredient_id=ingredients[ing_name].id,
                    amount_per_unit=amount
                )
                db.session.add(link)
                count += 1
    
    print(f"✅ Создано {count} новых технологических карт")
    
    # 5. Фиксация
    db.session.commit()
    print("\n🎉 Готово! Фото будут отображаться через picsum.photos")