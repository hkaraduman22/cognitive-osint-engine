from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.repositories.search_repository import SearchRepository


class AdminService:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)
        self.search_repository = SearchRepository(db)

    def list_users(self):
        return self.user_repository.list_all()

    def list_bot_logs(self):
        return self.search_repository.list_bot_logs()
