import logging
from typing import List, Dict
from sqlalchemy.orm import Session
from app.repositories.search_repository import SearchRepository
from app.models.models import Record, SearchHistory

logger = logging.getLogger(__name__)

class SearchService:
    """
    Arama gecmisi ve kayitlarin yonetiminden sorumlu sirket mantigi servisi.
    """
    def __init__(self, db: Session):
        self.search_repository = SearchRepository(db)

    def enqueue_search(self, user_id: int, query: str) -> Dict[str, str]:
        """
        Kullanicinin arama talebini sistem gecmisine kaydeder.
        """
        try:
            self.search_repository.save_search_history(user_id=user_id, query=query)
            return {"status": "success", "message": "Arama talebi sisteme kaydedildi."}
        except Exception as exc:
            logger.error(f"Arama gecmisi kaydedilirken hata olustu: {exc}")
            return {"status": "error", "message": "Gecmis kaydi basarisiz oldu."}

    def list_records(self) -> List[Record]:
        """
        Sistemdeki tum nitelikli kayitlari listeler.
        """
        return self.search_repository.list_records()

    def list_history(self, user_id: int) -> List[SearchHistory]:
        """
        Belirli bir kullaniciya ait son arama gecmisini getirir.
        """
        return self.search_repository.get_last_searches(user_id=user_id)