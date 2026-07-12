# Teslimat Checklist

Bu liste, projeyi teslim etmeden / sunmadan hemen önce sırayla kontrol edilmelidir.

## 1. Dosya ve Klasör Kontrolü

- [ ] `autonomous-osint-agent/` (core-api, Dockerfile, docker-compose.yml) mevcut
- [ ] `scraper-bot/` mevcut
- [ ] `delphi-vcl-frontend/` mevcut (kaynak kod + `OsintFrontend.exe`)
- [ ] Kök dizinde `analiz.py`, `redis_listener.py` mevcut
- [ ] `tests/` klasörü mevcut (19 test dosyası/fonksiyonu)
- [ ] `README.md`, `CHECKLIST.md`, `TROUBLESHOOTING.md` mevcut
- [ ] `autonomous-osint-agent/core-api/.env` dosyası mevcut ve **gerçek** `GROQ_API_KEY` ile dolu (`.env.example` değil!)
- [ ] `.env` dosyasının `.gitignore` içinde olduğu ve yanlışlıkla commit edilmediği kontrol edildi
- [ ] `../camart_ARCHIVE_cognitive-osint-engine` gibi arşivlenmiş eski klasörler teslim paketine **dahil edilmedi**

## 2. Ortam ve Servis Kontrolü

- [ ] Docker Desktop çalışıyor
- [ ] `cd autonomous-osint-agent && docker compose up -d` hatasız tamamlandı
- [ ] `docker compose ps` → 4 servis de `Up` (postgres/redis `healthy`)
- [ ] `http://localhost:8000/docs` tarayıcıda açılıyor
- [ ] `GROQ_API_KEY` geçerli — bkz. `TROUBLESHOOTING.md` "Groq kota/anahtar kontrolü"
- [ ] Groq günlük kota durumu demo saatinden hemen önce kontrol edildi (console.groq.com/settings/billing)

## 3. Fonksiyonel Kontrol (kuru prova — demo saatinden önce mutlaka yapın)

- [ ] `POST /auth/register` veya `/auth/login` çalışıyor (200 dönüyor, `access_token`+`refresh_token` içeriyor)
- [ ] `POST /api/v1/search/` çalışıyor, `search_history_id` dönüyor
- [ ] `POST /api/v1/companies/scan` çalışıyor (202 dönüyor)
- [ ] `GET /api/v1/companies/scan-status?arama_id=X` → birkaç saniye içinde `processing`, ardından `finished` gösteriyor
- [ ] `GET /api/v1/companies?arama_id=X` en az 1 firma dönüyor (adres/website/telefon alanları dolu)
- [ ] `.venv\Scripts\python.exe -m pytest tests\ -v` → **19 passed**

## 4. Sunum Malzemeleri

- [ ] Demo sorgusu hazır: `İstanbul CNC freze üreticileri`
- [ ] Yedek sorgu hazır: `Avcılar Arçelik servisi`
- [ ] İnternet/Groq kesintisi ihtimaline karşı önceden taranmış veri var (`GET /companies?min_puan=0` ile mevcut kayıtlar gösterilebilir)
- [ ] Delphi `.exe` çalışmazsa yedek plan: Swagger UI (`/docs`) üzerinden aynı akışı canlı gösterme

## 5. Sunumda Açıkça Belirtilecek Bilinen Sınırlamalar

- [ ] Delphi arayüzünün son özellikleri (DPAPI oturum kalıcılığı, sonuç tablosu, Job Status göstergesi) kaynak kodda hazır ama bu ortamda derlenemedi (RAD Studio yok)
- [ ] Groq günlük token kotası hesaba göre sınırlı olabilir
- [ ] Canlı tarama sonuçları DDG'nin o anki sonuçlarına göre değişkenlik gösterebilir (aynı sorgu her seferinde aynı sayıda sonuç vermeyebilir)

## 6. Son Kontrol

- [ ] `git status` temiz veya bilinçli olarak neyin değiştiği anlaşılır durumda
- [ ] Sunumdan hemen önce servisler yeniden başlatıldı (temiz bir durumdan başlamak için): `docker compose restart`
