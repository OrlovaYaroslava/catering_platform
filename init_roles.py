from app import create_app, db
from app.models import Role

app = create_app()

with app.app_context():
    roles = ["admin", "client", "kitchen"]
    for role_name in roles:
        if not Role.query.filter_by(name=role_name).first():
            db.session.add(Role(name=role_name))
    db.session.commit()
    print("Roles added")
