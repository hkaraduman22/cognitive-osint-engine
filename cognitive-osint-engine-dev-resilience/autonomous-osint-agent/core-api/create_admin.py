from app.database import SessionLocal
from app.repositories.user_repository import UserRepository
from app.utils.security import hash_password


def create_admin_once() -> None:
    db = SessionLocal()
    try:
        user_repository = UserRepository(db)
        existing_user = user_repository.get_by_username("admin")
        if existing_user is not None:
            print("Admin user already exists. No changes made.")
            return

        user_repository.create(
            username="admin",
            hashed_password=hash_password("admin"),
            is_admin=True,
        )
        print("Admin user created successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_once()
