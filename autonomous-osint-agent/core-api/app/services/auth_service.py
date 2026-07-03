from datetime import timedelta

from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.utils.security import create_access_token, hash_password, verify_password


class AuthService:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)

    def register_user(self, username: str, password: str):
        existing = self.user_repository.get_by_username(username)
        if existing:
            raise ValueError("Kullanıcı adı zaten mevcut")

        hashed_password = hash_password(password)
        user = self.user_repository.create(username=username, hashed_password=hashed_password)
        access_token = create_access_token(subject=str(user.id), expires_delta=timedelta(minutes=60))
        return user, access_token

    def authenticate_user(self, username: str, password: str):
        user = self.user_repository.get_by_username(username)
        if user is None or not verify_password(password, user.hashed_password):
            raise ValueError("Geçersiz kullanıcı adı veya şifre")
        access_token = create_access_token(subject=str(user.id))
        return user, access_token
