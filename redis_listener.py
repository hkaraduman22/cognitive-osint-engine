import sys
import os
import json
import asyncio
import logging

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None

from analiz import AnalizMotoru

_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
_SCRAPER_PATH = os.path.join(_PROJECT_ROOT, "scraper-bot")
if _SCRAPER_PATH not in sys.path:
    sys.path.insert(0, _SCRAPER_PATH)

from core.sqlite_queue import SQLiteMessageQueue

# Günlükleme (Logging) sisteminin canlı ortam standartlarına uygun formatta yapılandırılması
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("OSINT_Listener")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
QUEUE_NAME = os.getenv("OSINT_REDIS_QUEUE", "osint_raw_queue")
QUEUE_BACKEND = os.getenv("QUEUE_BACKEND", "sqlite").lower()


async def process_queue_message(data_json: str, ai_engine: AnalizMotoru) -> dict:
    """Kuyruktan gelen tek mesajı doğrular ve analiz motoruna iletir."""
    try:
        data = json.loads(data_json)
    except json.JSONDecodeError:
        data = {"ham_metin": data_json}

    if not isinstance(data, dict):
        raise ValueError("Redis mesajı JSON nesnesi veya düz metin olmalıdır.")

    ham_metin = str(data.get("ham_metin", "")).strip()
    if not ham_metin:
        raise ValueError("Redis mesajında ham_metin alanı boş olamaz.")

    return {
        "kaynak": data.get("kaynak", "Bilinmeyen"),
        "hedef_url": data.get("hedef_url", "Bilinmeyen"),
        "search_history_id": data.get("search_history_id"),
        "ham_metin_uzunlugu": len(ham_metin),
        "analiz_sonuclari": await ai_engine.analiz_et(
            ham_metin,
            search_history_id=data.get("search_history_id"),
            source_url=data.get("hedef_url"),
        ),
    }


async def worker_loop() -> None:
    """
    Üretim ortamında Redis kuyruğunu (osint_raw_queue) asenkron olarak dinleyen
    ve gelen verileri tekil AnalizMotoru üzerinden işleyen ana döngü.
    """
    if QUEUE_BACKEND == "redis" and aioredis is None:
        logger.error("Kritik Hata: 'redis' asenkron paketi yüklü değil (pip install redis).")
        return

    if QUEUE_BACKEND == "sqlite":
        sqlite_queue = SQLiteMessageQueue()
        r = None
    elif QUEUE_BACKEND == "redis":
        sqlite_queue = None
        r = await aioredis.from_url(REDIS_URL, decode_responses=True)
    else:
        logger.error("QUEUE_BACKEND yalnızca 'sqlite' veya 'redis' olabilir.")
        return

    ai_engine = AnalizMotoru()

    logger.info("OSINT Listener başlatıldı. Backend=%s, kuyruk=%s", QUEUE_BACKEND, QUEUE_NAME)

    counter: int = 1
    while True:
        # Kuyruktan bloklamayan asenkron FIFO veri çekme işlemi
        if sqlite_queue is not None:
            data_json = await asyncio.to_thread(sqlite_queue.pop, QUEUE_NAME)
        else:
            data_json = await r.lpop(QUEUE_NAME)

        if data_json:
            try:
                processed = await process_queue_message(data_json, ai_engine)
                ham_metin_uzunlugu = processed["ham_metin_uzunlugu"]
                kaynak = processed["kaynak"]
                hedef_url = processed["hedef_url"]
                ai_sonuc = processed["analiz_sonuclari"]
            except (ValueError, TypeError) as exc:
                logger.warning("Geçersiz Redis mesajı atlandı: %s", exc)
                continue
            except Exception as exc:
                logger.exception("Redis mesajı analiz edilirken hata oluştu: %s", exc)
                continue

            # Üretim ortamı loglama standartları (print yerine logger kullanımı)
            logger.info(f"[{counter}] Kuyruktan Görev Alındı -> [{kaynak.upper()}] {hedef_url}")
            logger.info(f"   Yapay Zeka Analizi: {len(ai_sonuc)} şirket potansiyeli tespit edildi.")
            logger.info(f"   Metin Boyutu: {ham_metin_uzunlugu} karakter.")
            logger.info("-" * 60)

            counter += 1
            # Rate-limit sınırlarına takılmamak ve sunucuyu korumak için bekleme süresi
            await asyncio.sleep(5)
        else:
            # Kuyruk boşsa işlemciyi (CPU) dinlendirmek için uyku modu
            await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        asyncio.run(worker_loop())
    except KeyboardInterrupt:
        logger.info("OSINT Dinleyici servisi kullanıcı tarafından güvenli şekilde kapatıldı.")
