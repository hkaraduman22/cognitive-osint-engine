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
        try:
            self.search_repository.save_search_history(user_id=user_id, query=query)
            return {"status": "success", "message": "Arama talebi sisteme kaydedildi."}
        except Exception as exc:
            logger.error(f"Arama gecmisi kaydedilirken hata olustu: {exc}")
            return {"status": "error", "message": "Gecmis kaydi basarisiz oldu."}

    def list_records(self) -> List[Record]:
        return self.search_repository.list_records()

    def list_history(self, user_id: int) -> List[SearchHistory]:
        return self.search_repository.get_last_searches(user_id=user_id)

# EKSİK OLAN VE HATAYA SEBEP OLAN FONKSİYON:
def run_scraper_background(target_domain: str, db: Session):
    """
    Arayüzden gelen istekle otonom botu arka planda tetikler.
    """
    logger.info(f"Bot arka planda {target_domain} için tetiklendi.")
    
    # Gelen arama talebini veritabanına kaydet
    service = SearchService(db)
    service.enqueue_search(user_id=1, query=target_domain)
    
    # Not: Redis kuyruğuna veri gönderme işlemin varsa 
    # (redis_client.publish vb.) buraya eklenebilir.