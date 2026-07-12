# OSINT Search API

Delphi arayüzünden (veya doğrudan Swagger'dan) gelen arama isteklerini kabul eden, asenkron OSINT taraması tetikleyen ve doğrulanmış sonuçları PostgreSQL veritabanına kaydeden FastAPI uygulaması.

> Projenin tamamı (Docker kurulumu, mimari, demo akışı, bilinen sınırlamalar) için kök dizindeki `README.md` dosyasına bakın. Bu dosya yalnızca `core-api` alt projesine özeldir.

## Mimari

- Python / FastAPI / SQLAlchemy / Pydantic
- PostgreSQL (Docker Compose ile otomatik ayağa kalkar)
- N-Tier: Controller/Router, Service, Repository
- JWT tabanlı kimlik doğrulama + refresh token rotasyonu

## Çalıştırma

Önerilen yol kök dizindeki Docker Compose'dur:

```powershell
cd ..
docker compose up -d
```

Docker'sız çalıştırmak isterseniz:

1. Ortam değişkenlerini ayarlayın (`.env.example`'ı kopyalayıp doldurun): `DATABASE_URL`, `JWT_SECRET`, `GROQ_API_KEY`
2. Paketleri yükleyin: `pip install -r requirements.txt`
3. API'yi başlatın: `uvicorn app.main:app --reload`

## Ana Uç Noktalar

- `POST /auth/register`, `POST /auth/login` — kayıt/giriş (access + refresh token döner)
- `POST /auth/refresh`, `POST /auth/logout` — oturum yenileme/iptal
- `POST /api/v1/search/` — arama geçmişi kaydı oluşturur, `search_history_id` döner
- `POST /api/v1/companies/scan` — gerçek taramayı tetikler (auth opsiyoneldir)
- `GET /api/v1/companies/scan-status?arama_id=X` — tarama durumu (`processing`/`finished`/`error`)
- `GET /api/v1/companies?arama_id=X` — firma sonuçları (ad, sektör, şehir, adres, website, telefon, e-posta, güven puanı)
- `GET /api/v1/stats/industry-distribution` — sektöre göre firma dağılımı
