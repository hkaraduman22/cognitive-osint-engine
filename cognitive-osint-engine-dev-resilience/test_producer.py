import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SCRAPER_PATH = os.path.join(PROJECT_ROOT, "scraper-bot")
if SCRAPER_PATH not in sys.path:
    sys.path.insert(0, SCRAPER_PATH)

from core.storage import QueueDataStorage


DIRTY_HTML = """
<html>
<head><title>Hakkımızda - Örnek Denizli Tekstil</title></head>
<body>
<nav>Menü | Hakkımızda | Ürünler | İletişim</nav>
<header>Örnek Denizli Tekstil - %100 yerli üretim!</header>
<main>
<h1>Hakkımızda</h1>
<p>1998'den beri tekstil sektöründe faaliyet gösteren Denizli merkezli bir firmayız.</p>
<p>Üretim alanlarımız: tişört, pamuklu kumaş, spor giyim ve teknik tekstiller.</p>
<p>Telefon: +90 258 000 0000 - E-posta: info@ornektekstil.com</p>
</main>
</body>
</html>
"""


if __name__ == "__main__":
    storage = QueueDataStorage()
    storage.save(
        {
            "kaynak": "manual_test",
            "hedef_url": "https://example.test/company",
            "ham_metin": DIRTY_HTML,
        }
    )
    print(f"Test mesajı kuyruğa eklendi. Backend: {storage.backend}")
