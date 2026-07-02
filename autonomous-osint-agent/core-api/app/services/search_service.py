from sqlalchemy.orm import Session

from app.repositories.search_repository import SearchRepository
from app.utils.osint_bot import run_osint_pipeline


class SearchService:
    def __init__(self, db: Session):
        self.search_repository = SearchRepository(db)

    def enqueue_search(self, user_id: int, query: str):
        self.search_repository.save_search_history(user_id=user_id, query=query)
        run_osint_pipeline(user_id=user_id, query=query, repository=self.search_repository)
        return {"message": "Arama alındı, işlem başlatıldı"}

    def list_records(self):
        return self.search_repository.list_records()

    def list_history(self, user_id: int):
        return self.search_repository.get_last_searches(user_id=user_id)
