import logging
import os
import sys
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.search_repository import SearchRepository
from app.models.models import Record, SearchHistory

# 'scraper-bot' klasörünün yukarı doğru taranarak dinamik ve güvenli şekilde bulunması
_current_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = None

while _current_dir and _current_dir != os.path.dirname(_current_dir):
    # Eğer mevcut dizinde 'scraper-bot' klasörü varsa, ana proje kök dizini bulunmuştur
    if os.path.exists(os.path.join(_current_dir, "scraper-bot")):
        _project_root = _current_dir
        break
    # Bir üst dizine geçiş yap
    _current_dir = os.path.dirname(_current_dir)

# 'core' ve 'spiders' paketlerini barındıran 'scraper-bot' yolunun sys.path'e eklenmesi
if _project_root:
    _scraper_bot_path = os.path.join(_project_root, "scraper-bot")
    if _scraper_bot_path not in sys.path:
        sys.path.insert(0, _scraper_bot_path)



logger = logging.getLogger(__name__)


class SearchService:
    """
    Arama geçmişi ve nitelikli kayıtların yönetiminden sorumlu servis sınıfı.
    """

    def __init__(self, db: Session) -> None:
        # Private isimlendirme kuralına uygun olarak repository nesnesi atanır
        self._search_repository = SearchRepository(db)

    def enqueue_search(self, user_id: int, query: str) -> Dict[str, Any]:
        """
        Kullanıcının yaptığı arama talebini sistem geçmişine kaydeder.
        """
        try:
            search = self._search_repository.save_search_history(user_id=user_id, query=query)
            return {"message": "Arama talebi sisteme başarıyla kaydedildi.", "search_history_id": search.id}
        except Exception as exc:
            logger.error(f"Arama geçmişi veritabanına kaydedilirken hata oluştu: {exc}")
            raise

    def list_records(self, user_id: int) -> List[Record]:
        """
        Sistemde kayıtlı olan tüm nitelikli OSINT verilerini listeler.
        """
        return self._search_repository.list_records(user_id=user_id, min_score=85)

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