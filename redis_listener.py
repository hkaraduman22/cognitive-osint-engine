import asyncio
import logging
import os
from typing import Any

from dotenv import load_dotenv

from analiz import AnalizMotoru

try:
    import redis.asyncio as aioredis
except ImportError:  # pragma: no cover
    aioredis = None

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DEFAULT_QUEUE_NAME = os.getenv("OSINT_REDIS_QUEUE", "osint:raw_text")
BRPOP_TIMEOUT = int(os.getenv("OSINT_REDIS_BRPOP_TIMEOUT", "5"))


class RedisSwarmListener:
    def __init__(self, queue_name: str = DEFAULT_QUEUE_NAME, redis_url: str = DEFAULT_REDIS_URL):
        if aioredis is None:
            raise RuntimeError(
                "redis paketini yüklemeden Redis dinleyicisi başlatılamaz. pip install redis"
            )

        self.queue_name = queue_name
        self.redis_url = redis_url
        self.motor = AnalizMotoru()
        self.redis: aioredis.Redis | None = None

    async def connect(self) -> None:
        self.redis = aioredis.from_url(self.redis_url, decode_responses=True)
        try:
            await self.redis.ping()
            logger.info("Redis'e bağlandı: %s", self.redis_url)
        except Exception as exc:
            raise RuntimeError(f"Redis bağlantısı kurulamadı: {exc}") from exc

    async def process_text(self, ham_metin: str) -> list[dict[str, Any]]:
        if not ham_metin or not ham_metin.strip():
            logger.warning("Boş metin alındı, işlem atlanıyor")
            return []

        logger.info("Metin işleniyor, LLM analizine gönderiliyor")
        result = await self.motor.analiz_et(ham_metin)
        logger.info(
            "Metin işlendi: %d sonuç, %d elit",
            len(result),
            sum(1 for item in result if item.get("confidence_score", 0) >= 85),
        )
        return result

    async def listen(self) -> None:
        if self.redis is None:
            await self.connect()

        logger.info("Redis kuyruğu dinleniyor: %s", self.queue_name)
        while True:
            try:
                message = await self.redis.brpop(self.queue_name, timeout=BRPOP_TIMEOUT)
                if message is None:
                    continue

                _, ham_metin = message
                if not ham_metin or not ham_metin.strip():
                    logger.warning("Kuyruktan boş mesaj alındı, atlanıyor")
                    continue

                await self.process_text(ham_metin)

            except asyncio.CancelledError:
                logger.info("Dinleyici iptal edildi")
                break
            except Exception as exc:
                logger.exception("Kuyruktan veri işlenirken hata oluştu: %s", exc)
                await asyncio.sleep(2)


async def main() -> None:
    listener = RedisSwarmListener()
    await listener.listen()


async def debug_test_kuyrugu():
    # Gerçek Redis'e ihtiyaç duymadan sistemi simüle et
    print("--- SÜRÜ (SWARM) SİMÜLASYONU BAŞLIYOR ---")
    listener = RedisSwarmListener()
    # AnalizMotoru zaten hazır, sadece bir test metni verelim
    test_metni = "ABC Teknoloji, Türkiye'nin önde gelen yapay zeka şirketidir."
    await listener.process_text(test_metni)
    print("--- SİMÜLASYON BAŞARILI ---")

if __name__ == "__main__":
    # Docker yerine bu simülasyonu çalıştır
    asyncio.run(debug_test_kuyrugu())


# redis_listener.py dosyanın en sonuna ekle:
async def swarm_debug():
    print("🚀 Sürü (Swarm) Motoru tetikleniyor...")
    listener = RedisSwarmListener()
    # Gerçek Redis'e gitmeden, analiz motorunu direkt test et
    sonuc = await listener.process_text("Denizli'de tekstil üreten, yapay zeka kullanan öncü bir şirketiz.")
    print(f"✅ Analiz tamamlandı. Elit şirket sayısı: {len([s for s in sonuc if s.get('confidence_score', 0) >= 85])}")

if __name__ == "__main__":
    asyncio.run(swarm_debug())
