from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.repositories.search_repository import SearchRepository
from app.services.company_service import get_companies


class AdminService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.search_repository = SearchRepository(db)

    def list_users(self):
        return self.user_repository.list_all()

    def list_bot_logs(self):
        return self.search_repository.list_bot_logs()

    def list_user_search_history(self, user_id: int):
        return self.search_repository.list_user_search_history_for_admin(user_id=user_id)

    def get_search_history_detail(self, search_history_id: int):
        detail = self.search_repository.get_search_history_detail_for_admin(search_history_id=search_history_id)
        if detail is None:
            return None

        companies = get_companies(
            self.db,
            min_confidence=0,
            limit=10000,
            skip=0,
            search_history_id=search_history_id,
            current_user={"id": 0, "is_admin": True},
        )

        detail["companies"] = [
            {
                "id": company.id,
                "name": company.name,
                "industry": company.industry,
                "city": company.city,
                "confidence_score": company.confidence_score,
                "address": company.address,
                "website": company.website,
                "phone": company.phone,
                "email": company.email,
                "source_url": company.source_url,
            }
            for company in companies
        ]
        return detail
