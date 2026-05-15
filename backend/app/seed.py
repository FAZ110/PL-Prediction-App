from .database import SessionLocal
from .auth_models import User
from .auth import hash_password

SEED_USERS = [
    {"email": "admin@football.local", "username": "admin",  "password": "Admin1234!"},
    {"email": "user1@football.local", "username": "user1",  "password": "User1234!"},
    {"email": "user2@football.local", "username": "user2",  "password": "User1234!"},
]


def seed_users() -> None:
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            return
        for u in SEED_USERS:
            db.add(User(
                email=u["email"],
                username=u["username"],
                hashed_password=hash_password(u["password"]),
            ))
        db.commit()
        print("✅ Seed: created default accounts")
        for u in SEED_USERS:
            print(f"   {u['email']}  /  {u['password']}  (username: {u['username']})")
    except Exception as e:
        db.rollback()
        print(f"⚠️ Seed failed: {e}")
    finally:
        db.close()
