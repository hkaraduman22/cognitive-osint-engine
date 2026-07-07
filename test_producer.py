import os
from dotenv import load_dotenv

try:
    import redis
except ImportError:
    redis = None

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
QUEUE_NAME = os.getenv("OSINT_REDIS_QUEUE", "osint:raw_text")

DIRTY_HTML = '''
<html>
<head><title>Hakkımızda - Örnek Denizli Tekstil</title></head>
<body>
<nav>Menu | Hakkımızda | Ürünler | İletişim</nav>
<header>Örnek Denizli Tekstil - %100 yerli üretim!</header>
<main>
<h1>Hakkımızda</h1>
<p>Biz, 1998'den beri tekstil sektöründe faaliyet gösteren, Denizli merkezli bir firmayız. Fabrikamız Denizli Organize Sanayi Bölgesi'nde yer almakta olup; üretimimiz <strong>terzi işi</strong> ve seri üretimi kapsamaktadır.</p>
<p>Üretim Alanlarımız: tişört, pamuklu kumaş, spor giyim ve teknik tekstiller.</p>
<section>
<h2>İletişim</h2>
<p>Adres: Denizli OSB, 3. cadde, No:12\nTelefon: +90 258 000 0000\nE-posta: info@ornektekstil.com</p>
</section>
</main>
<footer>© 2026 Örnek Tekstil | <a href='/privacy'>Privacy</a> | Social Links</footer>
<script>var a = 1; /* ads and trackers */</script>
</body>
</html>
'''

if __name__ == '__main__':
    if redis is None:
        print('redis kütüphanesi yüklenmemiş. Lütfen pip install redis')
        raise SystemExit(1)

    client = redis.from_url(REDIS_URL, decode_responses=True)
    try:
        client.ping()
    except Exception as e:
        print('Redis bağlantısı kurulamadı:', e)
        raise SystemExit(1)

    # Push the dirty HTML to the queue
    client.lpush(QUEUE_NAME, DIRTY_HTML)
    print('Test mesajı kuyruğa başarıyla eklendi.')
