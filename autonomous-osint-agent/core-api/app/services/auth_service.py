from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.config import settings
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)


class AuthService:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)
        self.refresh_token_repository = RefreshTokenRepository(db)

    def register_user(self, username: str, password: str):
        existing = self.user_repository.get_by_username(username)
        if existing:
            raise ValueError("Kullanıcı adı zaten mevcut")
        hashed_password = hash_password(password)
        user = self.user_repository.create(username=username, hashed_password=hashed_password)
        access_token = create_access_token(subject=str(user.id))
        refresh_token = self._issue_refresh_token(user.id)
        return user, access_token, refresh_token

    def authenticate_user(self, username: str, password: str):
        user = self.user_repository.get_by_username(username)
        if user is None or not verify_password(password, user.hashed_password):
            raise ValueError("Geçersiz kullanıcı adı veya şifre")
        access_token = create_access_token(subject=str(user.id))
        refresh_token = self._issue_refresh_token(user.id)
        return user, access_token, refresh_token

    def refresh_access_token(self, refresh_token: str):
        token_hash = hash_refresh_token(refresh_token)
        record = self.refresh_token_repository.get_by_hash(token_hash)
        if record is None or record.revoked or self._is_expired(record.expires_at):
            raise ValueError("Geçersiz veya süresi dolmuş refresh token")

        self.refresh_token_repository.revoke(record)

        user = self.user_repository.get_by_id(record.user_id)
        access_token = create_access_token(subject=str(user.id))
        new_refresh_token = self._issue_refresh_token(user.id)
        return access_token, new_refresh_token

    def logout(self, refresh_token: str) -> None:
        record = self.refresh_token_repository.get_by_hash(hash_refresh_token(refresh_token))
        if record is not None:
            self.refresh_token_repository.revoke(record)

    def _issue_refresh_token(self, user_id: int) -> str:
        raw_token = create_refresh_token()
        expires_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
        self.refresh_token_repository.create(
            user_id=user_id, token_hash=hash_refresh_token(raw_token), expires_at=expires_at
        )
        return raw_token

    @staticmethod
    def _is_expired(expires_at: datetime) -> bool:
        # Postgres stores DateTime columns as naive TIMESTAMP; treat naive values as UTC.
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        return expires_at < datetime.now(UTC)
