import sys
import os
import redis
import json
import time
import asyncio


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../"))  # On remonte d'un niveau
if project_root not in sys.path:
    sys.path.append(project_root)
# ------------------------------------------------

from analiz import AnalizMotoru  # noqa: E402


def worker():
    # Redis bağlantısı
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    ai_engine = AnalizMotoru()

    print("[!] Worker başlatıldı, Redis dinleniyor...")

    counter = 1
    while True:
        # Redis'ten 1 adet veri çek
        data_json = r.lpop("osint_raw_queue")

        if data_json:
            data = json.loads(data_json)

            # LLM Analizi
            try:
                ai_sonuc = asyncio.run(ai_engine.analiz_et(data.get("ham_metin", "")))
            except Exception as e:
                ai_sonuc = {"hata": "WORKER_ANALIZ_HATASI", "detay": str(e)}

            # ---LOG ---
            print(f"\n{counter}. [{data['kaynak'].upper()}] -> {data['hedef_url']}")
            print(f"   E-postalar : {data['iletisim_bilgileri']['e_postalar']}")
            print(f"   Telefonlar : {data['iletisim_bilgileri']['telefonlar']}")
            print(f"   AI Analizi : {ai_sonuc}")
            print(f"   Metin (Karakter): {len(data['ham_metin'])}")
            print("-" * 50)

            counter += 1
            # Rate limit için 5 saniye bekle
            time.sleep(5)
        else:
            # Kuyruk boşsa bekle
            time.sleep(1)


if __name__ == "__main__":
    worker()
