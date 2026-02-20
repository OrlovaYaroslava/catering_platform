# migrate_add_tags_and_images.py
from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("🔧 Начинаем миграцию базы данных...")
    
    # 1. Добавляем поле image_url в таблицу dishes
    print("📸 Добавляем поле image_url в таблицу dishes...")
    try:
        db.session.execute(text("""
            ALTER TABLE dishes 
            ADD COLUMN IF NOT EXISTS image_url VARCHAR(255) DEFAULT NULL
        """))
        db.session.commit()
        print("✅ Поле image_url добавлено")
    except Exception as e:
        print(f"⚠️  Поле image_url уже существует или ошибка: {e}")
        db.session.rollback()
    
    # 2. Создаём таблицу tags
    print("🏷  Создаём таблицу tags...")
    try:
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS tags (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                description VARCHAR(255)
            )
        """))
        db.session.commit()
        print("✅ Таблица tags создана")
    except Exception as e:
        print(f"⚠️  Ошибка создания tags: {e}")
        db.session.rollback()
    
    # 3. Создаём таблицу dish_tags (связь many-to-many)
    print("🔗 Создаём таблицу dish_tags...")
    try:
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS dish_tags (
                dish_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (dish_id, tag_id),
                FOREIGN KEY (dish_id) REFERENCES dishes(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        """))
        db.session.commit()
        print("✅ Таблица dish_tags создана")
    except Exception as e:
        print(f"⚠️  Ошибка создания dish_tags: {e}")
        db.session.rollback()
    
    print("\n🎉 Миграция завершена!")
    print("Теперь запусти seed_full.py для наполнения данными")