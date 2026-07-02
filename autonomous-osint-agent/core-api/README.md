# OSINT Search API

Bu proje, Delphi arayüzünden gelen arama isteklerini kabul eden, asenkron OSINT taraması yapan ve temizlenen sonuçları PostgreSQL veritabanına kaydeden bir Python FastAPI uygulamasıdır.

## Mimari
- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- N-Tier: Controller, Service, Repository
- JWT tabanlı kimlik doğrulama

## Çalıştırma
1. Ortam değişkenlerini ayarlayın:
   - `DATABASE_URL`
   - `JWT_SECRET`
2. Paketleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
3. API'yi başlatın:
   ```bash
   uvicorn app.main:app --reload
   ```

## Ana uç noktalar
- `POST /auth/register`
- `POST /auth/login`
- `POST /search`
- `GET /history`
- `GET /records`
- `GET /admin/users`
- `GET /admin/logs`
