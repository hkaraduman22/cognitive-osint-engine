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

# Günlükleme (Logging) sisteminin canlı ortam standartlarına uygun formatta yapılandırılması
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("OSINT_Listener")


async def worker_loop() -> None:
    """
    Üretim ortamında Redis kuyruğunu (osint_raw_queue) asenkron olarak dinleyen
    ve gelen verileri tekil AnalizMotoru üzerinden işleyen ana döngü.
    """
    if aioredis is None:
        logger.error("Kritik Hata: 'redis' asenkron paketi yüklü değil (pip install redis).")
        return

    # Asenkron Redis bağlantısının güvenli şekilde başlatılması
    r = await aioredis.from_url("redis://localhost:6379/0", decode_responses=True)
    ai_engine = AnalizMotoru()

    logger.info("OSINT Üretim Dinleyicisi (Listener) başlatıldı. Redis kuyruğu dinleniyor...")

    counter: int = 1
    while True:
        # Kuyruktan bloklamayan asenkron FIFO veri çekme işlemi
        data_json: str | None = await r.lpop("osint_raw_queue")

        if data_json:
            try:
                data = json.loads(data_json)
                ham_metin = data.get("ham_metin", "")
                kaynak = data.get("kaynak", "Bilinmeyen")
                hedef_url = data.get("hedef_url", "Bilinmeyen")
            except json.JSONDecodeError:
                ham_metin = data_json
                data = {}
                kaynak = "Bilinmeyen"
                hedef_url = "Bilinmeyen"

            try:
                # Güvenli hale getirilmiş AI analiz sürecinin çağrılması
                ai_sonuc = await ai_engine.analiz_et(ham_metin)
            except Exception as e:
                ai_sonuc = [{"hata": "PRODUCTION_ANALIZ_HATASI", "detay": str(e)}]

            # Üretim ortamı loglama standartları (print yerine logger kullanımı)
            logger.info(f"[{counter}] Kuyruktan Görev Alındı -> [{kaynak.upper()}] {hedef_url}")
            logger.info(f"   Yapay Zeka Analizi: {len(ai_sonuc)} şirket potansiyeli tespit edildi.")
            logger.info(f"   Metin Boyutu: {len(ham_metin)} karakter.")
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