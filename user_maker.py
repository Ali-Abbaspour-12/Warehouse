from app import create_app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash



new_users = [
    {"username": "admin", "password": "1234", "is_admin": True},
    {"username": "user1", "password": "1111", "is_admin": False}
    
]



app = create_app()

with app.app_context():


    User.query.delete()
    db.session.commit()



    for u in new_users:
        user = User(
            username=u["username"],
            password=generate_password_hash(u["password"]),
            is_admin=u["is_admin"]
        )
        db.session.add(user)

    db.session.commit()



    for u in new_users:
        role = "ادمین" if u["is_admin"] else "کاربر معمولی"
        print(f"   → {u['username']}  /  {u['password']}  ({role})")
