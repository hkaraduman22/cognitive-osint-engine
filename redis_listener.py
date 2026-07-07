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

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("Worker")


async def worker_loop():
    if aioredis is None:
        print("Hata: redis paketi yüklü değil (pip install redis)")
        return

    r = await aioredis.from_url("redis://localhost:6379/0", decode_responses=True)
    ai_engine = AnalizMotoru()

    print("Worker başlatıldı. Redis kuyruğu dinleniyor...")

    counter = 1
    while True:
        data_json = await r.lpop("osint_raw_queue")

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
                ai_sonuc = await ai_engine.analiz_et(ham_metin)
            except Exception as e:
                ai_sonuc = [{"hata": "WORKER_ANALIZ_HATASI", "detay": str(e)}]

            print(f"\n{counter}. [{kaynak.upper()}] -> {hedef_url}")
            print(f"   Yyapay Zeka Analizi: {len(ai_sonuc)} şirket bulundu.")
            print(f"   Metin (Karakter Sayısı): {len(ham_metin)}")
            print("-" * 50)

            counter += 1
            await asyncio.sleep(5)
        else:
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(worker_loop())