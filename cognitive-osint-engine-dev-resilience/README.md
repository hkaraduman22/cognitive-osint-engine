# Cognitive OSINT Engine

Yasal ve herkese açık kaynaklardan (firma web siteleri, ticaret odaları, OSB rehberleri, iş ilanı ve sektör forumları) firma bilgisi toplayan, Groq LLM ile analiz edip güven puanı üreten bir **B2B firma ve profesyonel rehberi** MVP'sidir.

Örnek kullanım: kullanıcı "İstanbul CNC freze üreticileri" yazar → sistem şehir/sektör anahtar kelimelerini ayırır → çok kaynaklı bir tarama başlatır → bulunan firmaları LLM ile doğrulayıp güven puanı ile birlikte veritabanına kaydeder → Delphi masaüstü arayüzünde (veya doğrudan API üzerinden) listeler.

## Sistem Yetenekleri

- JWT tabanlı kimlik doğrulama + **refresh token rotasyonu** (çalıntı token tekrar kullanılırsa otomatik iptal)
- **Docker Compose** ile tek komutla ayağa kalkan tam yığın (Postgres + Redis + FastAPI + Worker)
- DuckDuckGo tabanlı çok kaynaklı tarama (genel arama, OSB, ticaret odası, iş ilanı, sektör forumu varyasyonları)
- **User-Agent / Accept-Language / Referer rotasyonu** ve isteğe bağlı proxy desteği; 403 (bot engeli) alındığında farklı bir kimlikle **tek seferlik** otomatik yeniden deneme
- Groq LLM (`llama-3.1-8b-instant`) ile firma tespiti, açıklama ve güven puanı üretimi; 429 (rate limit) hatalarında otomatik retry
- Genişletilmiş firma verisi: ad, sektör, şehir, **adres, website, telefon (normalize edilmiş format), e-posta**, güven puanı, kaynak URL, son güncelleme
- Unicode/Türkçe uyumlu firma tekilleştirme (aynı firma farklı kaynaklardan gelirse birleştirilir, veri kaybetmez)
- **Job Status** takibi — bir taramanın `processing` / `finished` / `error` durumu API üzerinden sorgulanabilir
- Docker servislerinde `restart: unless-stopped` — bir servis çökerse kendini otomatik onarır
- Delphi VCL masaüstü istemcisi

## Mimari

```text
Delphi VCL (veya doğrudan Swagger/curl)
    │ HTTP/JWT
    ▼
FastAPI Core API ──────────────► Postgres (firma/kullanıcı/arama verisi)
    │ subprocess tetikler
    ▼
Scraper Bot (DDG + UA rotasyonu) ──► Redis Kuyruğu ──► Analiz Worker
                                                            │
                                                            ▼
                                                        Groq LLM
                                                            │
                                                            ▼
                                                  Firma API'si (POST /companies)
```

Ana bileşenler:

- `autonomous-osint-agent/core-api`: FastAPI + SQLAlchemy backend (auth, firma, arama, job-status uç noktaları)
- `autonomous-osint-agent/docker-compose.yml`: Postgres, Redis, API ve Worker servislerini tanımlar
- `scraper-bot`: açık web kaynaklarını UA/proxy rotasyonuyla tarayan producer
- `redis_listener.py`: Redis kuyruğunu tüketen analiz worker'ı
- `analiz.py`: metin temizleme, Groq analizi, retry mekanizması ve güven puanı filtresi
- `delphi-vcl-frontend`: masaüstü kullanıcı arayüzü (kaynak kod — derleme notu aşağıda)
- `tests`: kanonik test paketi (19 test)

## Gereksinimler

- **Docker Desktop** (önerilen ve doğrulanmış ana yol)
- Groq API anahtarı ([console.groq.com](https://console.groq.com)) — LLM analizi için
- (İsteğe bağlı) RAD Studio 10.4+ — yalnızca Delphi arayüzünü kaynak koddan derlemek isterseniz

## Kurulum ve Çalıştırma (Docker — önerilen yol)

```powershell
cd C:\Users\Admin\Desktop\camart\autonomous-osint-agent
Copy-Item core-api\.env.example core-api\.env
```

`core-api\.env` dosyasını açıp `GROQ_API_KEY` alanını kendi anahtarınızla doldurun. Diğer alanlar (JWT_SECRET vb.) demo için varsayılan değerlerle çalışır; **prod'a çıkarken `JWT_SECRET` mutlaka değiştirilmelidir.**

```powershell
docker compose up -d
```

Servislerin sağlıklı ayakta olduğunu doğrulayın:

```powershell
docker compose ps
```

4 servis de `Up` (postgres/redis için `healthy`) görünmelidir. Swagger arayüzü: `http://localhost:8000/docs`

**Önemli:** `docker-compose.yml` içindeki bazı ortam değişkenleri (`DATABASE_URL`, `QUEUE_BACKEND=redis`) `.env` dosyasını kasıtlı olarak override eder — Docker ortamı her zaman Postgres + Redis kullanır, `.env`'deki `sqlite` varsayılanı yalnızca Docker'sız çalıştırmayı etkiler.

Konfigürasyon değiştirdiğinizde (`docker-compose.yml` düzenlemesi gibi) **`docker compose restart` yeterli değildir** — konteynerlerin yeniden oluşturulması gerekir:

```powershell
docker compose up -d
```

## Delphi İstemcisi

Kaynak kod `delphi-vcl-frontend/` altında, RAD Studio ile `OsintFrontend.dproj` açılarak derlenir.

**Bilinen durum:** Mevcut derlenmiş `OsintFrontend.exe`, en son eklenen özellikleri (DPAPI ile kalıcı oturum, sonuç tablosu, Job Status göstergesi) **içermiyor** — bu ortamda RAD Studio bulunmadığı için kaynak kod derlenemedi. Backend bu eski `.exe` ile tam geriye dönük uyumludur (bkz. `TROUBLESHOOTING.md`). RAD Studio erişimi olan biri projeyi derlerse yeni özellikler otomatik devreye girer.

## Test

```powershell
.venv\Scripts\python.exe -m pytest tests\ -v
```

Beklenen sonuç:

```text
19 passed
```

## Demo Akışı

Önerilen sorgu:

```text
İstanbul CNC freze üreticileri
```

Sunum sırası (Docker ayaktayken):

1. `docker compose ps` ile 4 servisin de çalıştığını gösterin.
2. Swagger (`/docs`) veya Delphi'den kayıt olun/giriş yapın.
3. `POST /api/v1/search/` ile arama kaydı oluşturun, `search_history_id` alın.
4. `POST /api/v1/companies/scan` ile taramayı tetikleyin.
5. `GET /api/v1/companies/scan-status?arama_id=...` ile durumun `processing` → `finished` geçişini gösterin.
6. `GET /api/v1/companies?arama_id=...` ile firma, şehir, adres, website, telefon, e-posta, güven puanı ve kaynak URL'yi gösterin.

İkinci örnek sorgu: `Avcılar Arçelik servisi`

Canlı internet veya Groq erişimi sorunlu olursa önceden taranmış verilerle (`GET /api/v1/companies?min_puan=0`) devam edilebilir — bkz. `TROUBLESHOOTING.md`.

## Veri ve Etik Sınırlar

Sistem yalnızca kamuya açık ve yasal kaynaklar için tasarlanmıştır. CAPTCHA, oturum kontrolü veya platform güvenliği aşılmaz. Gizli kişisel veri toplanmaz ve yayımlanmamış iletişim bilgisi tahmin edilmez. 403 alındığında yapılan tek seferlik kimlik rotasyonu bilinçli olarak sınırlıdır — Cloudflare/WAF korumalı siteler aşılmaya çalışılmaz.

## Bilinen Sınırlamalar

- Canlı web sonuçları kaynakların erişilebilirliğine ve DDG'nin o anki sonuçlarına göre değişebilir; aynı sorgu farklı çalıştırmalarda farklı sayıda sonuç üretebilir.
- Groq'un günlük token kotası hesaba göre sınırlıdır; doldurulursa fallback devreye girer ve o sayfa için sonuç kaydedilmez (veri kaybı değil, güvenli atlama).
- Delphi arayüzünün en son özellikleri (yukarıya bakın) derlenmedi.
- Personel endpoint'i MVP'de örnek/stub yanıt üretmektedir.
- Firma tekilleştirme küçük MVP veri hacmine göre uygulama katmanında yapılır (yüksek hacimde SQL seviyesinde indexlenmesi gerekir).
- Cloudflare/WAF korumalı siteler (örn. kariyer.net) UA rotasyonuyla aşılamaz — kasıtlı bir sınır.
- Proje içinde eski geliştirme kopyaları repo dışına arşivlendi (`../camart_ARCHIVE_cognitive-osint-engine`); kanonik kök bu README'nin bulunduğu dizindir.

## Teslim Durumu

- Docker Compose ile tek komutla ayağa kalkma: başarılı
- Auth + refresh token rotasyonu: başarılı
- Canlı çok kaynaklı scraper + UA rotasyonu: başarılı
- Arama–firma ilişkisi + Job Status takibi: başarılı
- Genişletilmiş firma verisi (adres/website/telefon/e-posta): başarılı
- Tekilleştirme ve veri doğrulama: başarılı
- Docker servis dayanıklılığı (`restart: unless-stopped`): başarılı, doğrulandı
- Kanonik test paketi: **19/19 başarılı**

Teslimat öncesi kontrol listesi için `CHECKLIST.md`, demo sırasında olası sorunlar için `TROUBLESHOOTING.md` dosyasına bakın.
