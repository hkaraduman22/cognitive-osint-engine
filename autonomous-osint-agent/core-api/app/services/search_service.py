import logging
import os
import sys
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.search_repository import SearchRepository
from app.models.models import Record, SearchHistory

# OSINT motoru bileşenlerinin (core ve spiders) sorunsuz şekilde dahil edilmesi
from app.scraper.core.storage import RedisDataStorage
from app.scraper.core.coordinator import DataDrivenCoordinator
from app.scraper.spiders.html_parser import GeneralHtmlParser

logger = logging.getLogger(__name__)


class SearchService:
    """
    Arama geçmişi ve nitelikli kayıtların yönetiminden sorumlu servis sınıfı.
    """

    def __init__(self, db: Session) -> None:
        # Private isimlendirme kuralına uygun olarak repository nesnesi atanır
        self._search_repository = SearchRepository(db)

    def enqueue_search(self, user_id: int, query: str) -> Dict[str, str]:
        """
        Kullanıcının yaptığı arama talebini sistem geçmişine kaydeder.
        """
        try:
            self._search_repository.save_search_history(user_id=user_id, query=query)
            return {"status": "success", "message": "Arama talebi sisteme başarıyla kaydedildi."}
        except Exception as exc:
            logger.error(f"Arama geçmişi veritabanına kaydedilirken hata oluştu: {exc}")
            return {"status": "error", "message": "Geçmiş kaydı başarısız oldu."}

    def list_records(self) -> List[Record]:
        """
        Sistemde kayıtlı olan tüm nitelikli OSINT verilerini listeler.
        """
        return self._search_repository.list_records()

    def list_history(self, user_id: int) -> List[SearchHistory]:
        """
        Belirli bir kullanıcıya ait son arama geçmişi kayıtlarını getirir.
        """
        return self._search_repository.get_last_searches(user_id=user_id)


def run_scraper_background(target_domain: str, keyword: str) -> None:
    """
    FastAPI BackgroundTasks tarafından çağrılan ve kazıma mimarisini tetikleyen ana fonksiyon.
    """
    # Arama sorgusunun temizlenmesi ve birleştirilmesi (Örn: "Denizli Tekstil")
    complete_query: str = f"{keyword} {target_domain}".strip()
    logger.info(f"[OSINT_MOTORU] '{complete_query}' sorgusu için koordinatör uyandırılıyor.")

    try:
        # Bağımlılıkların temiz bir şekilde başlatılması (Clean Architecture)
        storage = RedisDataStorage()
        parser = GeneralHtmlParser()
        coordinator = DataDrivenCoordinator(parser=parser, storage=storage)

        # Çoklu bot tarama sürecinin eşzamanlı olarak başlatılması
        coordinator.execute(complete_query)

        logger.info("[OSINT_MOTORU] Çok kaynaklı tarama tamamlandı. Veriler Redis kuyruğuna gönderildi.")
    except Exception as exc:
        logger.error(f"[OSINT_MOTORU] Tarama sürecinde kritik hata oluştu: {exc}")