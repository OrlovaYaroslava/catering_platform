from app import create_app, db
from app.models import Dish, DishIngredient, Ingredient

app = create_app()

def add_ingredient(dish, ingredient_name, amount, unit_name=None):
    """Добавляет ингредиент к блюду если ещё нет"""
    # Ищем ингредиент по названию (русское или английское)
    ingredient = Ingredient.query.filter(
        (Ingredient.name == ingredient_name) | 
        (Ingredient.name.like(f"%{ingredient_name}%"))
    ).first()
    
    if ingredient and dish:
        # Проверяем нет ли уже такой связи
        existing = DishIngredient.query.filter_by(
            dish_id=dish.id, 
            ingredient_id=ingredient.id
        ).first()
        
        if not existing:
            link = DishIngredient(
                dish_id=dish.id,
                ingredient_id=ingredient.id,
                amount_per_unit=amount
            )
            db.session.add(link)
            return True
    return False

with app.app_context():
    print("🔧 Добавляем технологические карты...\n")
    
    added_count = 0
    skipped_count = 0
    
    # === ЦЕЗАРЬ С КРЕВЕТКАМИ ===
    dish = Dish.query.filter_by(name="Цезарь с креветками").first()
    if dish:
        if add_ingredient(dish, "Креветки", 0.15): added_count += 1
        if add_ingredient(dish, "Салат Айсберг", 0.1): added_count += 1
        if add_ingredient(dish, "Сыр пармезан", 0.05): added_count += 1
        if add_ingredient(dish, "Caesar sauce", 0.03): added_count += 1
        print(f"✅ Цезарь с креветками")
    
    # === КАПРЕЗЕ ===
    dish = Dish.query.filter_by(name="Капрезе").first()
    if dish:
        if add_ingredient(dish, "Помидоры", 0.15): added_count += 1
        if add_ingredient(dish, "Сыр моцарелла", 0.1): added_count += 1
        if add_ingredient(dish, "Масло оливковое", 0.02): added_count += 1
        if add_ingredient(dish, "Базилик", 0.01): added_count += 1
        print(f"✅ Капрезе")
    
    # === ОЛИВЬЕ ===
    dish = Dish.query.filter_by(name="Оливье").first()
    if dish:
        if add_ingredient(dish, "Картофель", 0.1): added_count += 1
        if add_ingredient(dish, "Морковь", 0.05): added_count += 1
        if add_ingredient(dish, "Яйца", 2): added_count += 1
        if add_ingredient(dish, "Колбаса", 0.1): added_count += 1
        if add_ingredient(dish, "Огурцы", 0.05): added_count += 1
        if add_ingredient(dish, "Майонез", 0.03): added_count += 1
        print(f"✅ Оливье")
    
    # === BEEF STROGANOFF ===
    dish = Dish.query.filter_by(name="Beef Stroganoff").first()
    if dish:
        if add_ingredient(dish, "Говядина", 0.2): added_count += 1
        if add_ingredient(dish, "Грибы шампиньоны", 0.1): added_count += 1
        if add_ingredient(dish, "Лук репчатый", 0.05): added_count += 1
        if add_ingredient(dish, "Сливки 20%", 0.1): added_count += 1
        print(f"✅ Beef Stroganoff")
    
    # === CHOCOLATE CAKE ===
    dish = Dish.query.filter_by(name="Chocolate Cake").first()
    if dish:
        if add_ingredient(dish, "Шоколад тёмный", 0.1): added_count += 1
        if add_ingredient(dish, "Мука", 0.15): added_count += 1
        if add_ingredient(dish, "Яйца", 2): added_count += 1
        if add_ingredient(dish, "Сахар", 0.08): added_count += 1
        print(f"✅ Chocolate Cake")
    
    # === РИЗОТТО С ГРИБАМИ ===
    dish = Dish.query.filter_by(name="Ризотто с грибами").first()
    if dish:
        if add_ingredient(dish, "Рис", 0.15): added_count += 1
        if add_ingredient(dish, "Грибы шампиньоны", 0.15): added_count += 1
        if add_ingredient(dish, "Лук репчатый", 0.05): added_count += 1
        if add_ingredient(dish, "Сыр пармезан", 0.05): added_count += 1
        if add_ingredient(dish, "Масло сливочное", 0.03): added_count += 1
        print(f"✅ Ризотто с грибами")
    
    # === СТЕЙК РИБАЙ ===
    dish = Dish.query.filter_by(name="Стейк Рибай").first()
    if dish:
        if add_ingredient(dish, "Говядина", 0.25): added_count += 1
        if add_ingredient(dish, "Соль", 0.005): added_count += 1
        if add_ingredient(dish, "Перец", 0.002): added_count += 1
        if add_ingredient(dish, "Масло оливковое", 0.02): added_count += 1
        print(f"✅ Стейк Рибай")
    
    # === ПЛОВ С КУРИЦЕЙ ===
    dish = Dish.query.filter_by(name="Плов с курицей").first()
    if dish:
        if add_ingredient(dish, "Куриное филе", 0.15): added_count += 1
        if add_ingredient(dish, "Рис", 0.1): added_count += 1
        if add_ingredient(dish, "Морковь", 0.05): added_count += 1
        if add_ingredient(dish, "Лук репчатый", 0.03): added_count += 1
        if add_ingredient(dish, "Масло растительное", 0.03): added_count += 1
        print(f"✅ Плов с курицей")
    
    # === БРУСКЕТТА С ТОМАТАМИ ===
    dish = Dish.query.filter_by(name="Брускетта с томатами").first()
    if dish:
        if add_ingredient(dish, "Хлеб", 0.1): added_count += 1
        if add_ingredient(dish, "Помидоры", 0.1): added_count += 1
        if add_ingredient(dish, "Чеснок", 0.005): added_count += 1
        if add_ingredient(dish, "Масло оливковое", 0.02): added_count += 1
        print(f"✅ Брускетта с томатами")
    
    # === ТАРТАЛЕТКИ С ИКРОЙ ===
    dish = Dish.query.filter_by(name="Тарталетки с икрой").first()
    if dish:
        if add_ingredient(dish, "Тарталетки", 5): added_count += 1
        if add_ingredient(dish, "Икра красная", 0.03): added_count += 1
        if add_ingredient(dish, "Сливочное масло", 0.01): added_count += 1
        print(f"✅ Тарталетки с икрой")
    
    # === КУРИНЫЕ КРЫЛЫШКИ BBQ ===
    dish = Dish.query.filter_by(name="Куриные крылышки BBQ").first()
    if dish:
        if add_ingredient(dish, "Куриное филе", 0.2): added_count += 1
        if add_ingredient(dish, "Соус BBQ", 0.05): added_count += 1
        if add_ingredient(dish, "Мёд", 0.02): added_count += 1
        print(f"✅ Куриные крылышки BBQ")
    
    # === КАНАПЕ АССОРТИ ===
    dish = Dish.query.filter_by(name="Канапе ассорти").first()
    if dish:
        if add_ingredient(dish, "Хлеб", 0.05): added_count += 1
        if add_ingredient(dish, "Сыр", 0.05): added_count += 1
        if add_ingredient(dish, "Ветчина", 0.05): added_count += 1
        if add_ingredient(dish, "Огурцы", 0.03): added_count += 1
        print(f"✅ Канапе ассорти")
    
    # === КУРИНЫЙ БУЛЬОН ===
    dish = Dish.query.filter_by(name="Куриный бульон").first()
    if dish:
        if add_ingredient(dish, "Куриное филе", 0.2): added_count += 1
        if add_ingredient(dish, "Морковь", 0.05): added_count += 1
        if add_ingredient(dish, "Лук репчатый", 0.03): added_count += 1
        if add_ingredient(dish, "Соль", 0.005): added_count += 1
        print(f"✅ Куриный бульон")
    
    # === СОЛЯНКА СБОРНАЯ ===
    dish = Dish.query.filter_by(name="Солянка сборная").first()
    if dish:
        if add_ingredient(dish, "Говядина", 0.1): added_count += 1
        if add_ingredient(dish, "Колбаса", 0.05): added_count += 1
        if add_ingredient(dish, "Огурцы", 0.05): added_count += 1
        if add_ingredient(dish, "Лук репчатый", 0.03): added_count += 1
        if add_ingredient(dish, "Томатная паста", 0.02): added_count += 1
        print(f"✅ Солянка сборная")
    
    # === ЧИЗКЕЙК НЬЮ-ЙОРК ===
    dish = Dish.query.filter_by(name="Чизкейк Нью-Йорк").first()
    if dish:
        if add_ingredient(dish, "Сыр моцарелла", 0.2): added_count += 1
        if add_ingredient(dish, "Печенье", 0.1): added_count += 1
        if add_ingredient(dish, "Масло сливочное", 0.05): added_count += 1
        if add_ingredient(dish, "Сахар", 0.05): added_count += 1
        if add_ingredient(dish, "Яйца", 2): added_count += 1
        print(f"✅ Чизкейк Нью-Йорк")
    
    # === ФРУКТОВАЯ ТАРЕЛКА ===
    dish = Dish.query.filter_by(name="Фруктовая тарелка").first()
    if dish:
        if add_ingredient(dish, "Яблоки", 0.1): added_count += 1
        if add_ingredient(dish, "Апельсины", 0.1): added_count += 1
        if add_ingredient(dish, "Виноград", 0.1): added_count += 1
        if add_ingredient(dish, "Киви", 0.05): added_count += 1
        print(f"✅ Фруктовая тарелка")
    
    # === ПАННА-КОТТА ===
    dish = Dish.query.filter_by(name="Панна-котта").first()
    if dish:
        if add_ingredient(dish, "Сливки 20%", 0.15): added_count += 1
        if add_ingredient(dish, "Сахар", 0.03): added_count += 1
        if add_ingredient(dish, "Желатин", 0.01): added_count += 1
        if add_ingredient(dish, "Ваниль", 0.002): added_count += 1
        print(f"✅ Панна-котта")
    
    # === ЛИМОНАД ДОМАШНИЙ ===
    dish = Dish.query.filter_by(name="Лимонад домашний").first()
    if dish:
        if add_ingredient(dish, "Лимон", 0.05): added_count += 1
        if add_ingredient(dish, "Сахар", 0.03): added_count += 1
        if add_ingredient(dish, "Вода", 0.3): added_count += 1
        if add_ingredient(dish, "Мята", 0.005): added_count += 1
        print(f"✅ Лимонад домашний")
    
    # === МОРС КЛЮКВЕННЫЙ ===
    dish = Dish.query.filter_by(name="Морс клюквенный").first()
    if dish:
        if add_ingredient(dish, "Клюква", 0.1): added_count += 1
        if add_ingredient(dish, "Сахар", 0.03): added_count += 1
        if add_ingredient(dish, "Вода", 0.3): added_count += 1
        print(f"✅ Морс клюквенный")
    
    # === СОХРАНЯЕМ ===
    db.session.commit()
    
    print("\n" + "="*60)
    print(f"🎉 ГОТОВО! Добавлено {added_count} связей ингредиентов")
    print("="*60)