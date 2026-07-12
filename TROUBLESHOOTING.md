# Troubleshooting — Hızlı Çözüm Kılavuzu

Demo sırasında bir sorunla karşılaşırsanız, panik yapmadan aşağıdaki listede belirtiye en yakın maddeyi bulun.

---

## API yanıt vermiyor / `Connection refused` / `/docs` açılmıyor

**Hızlı çözüm:**
```powershell
cd autonomous-osint-agent
docker compose ps
docker compose logs api --tail=50
```
`api` servisi listede yoksa veya `Exited` durumdaysa:
```powershell
docker compose up -d
```
**Not:** `docker compose restart` bazen yeterli olmaz, özellikle `docker-compose.yml`'de bir değişiklik yapıldıysa (config değişikliklerini uygulamaz). Emin olmak için her zaman `docker compose up -d` kullanın.

---

## Bir servis çöktü ve kendiliğinden dirilmiyor

Tüm servislerde `restart: unless-stopped` politikası var — **gerçek bir çökmede** (uygulama içi hata) otomatik dirilir. Ancak container'ı siz `docker stop`/`docker kill` ile bilerek durdurduysanız, Docker bunu "kasıtlı durdurma" sayar ve **otomatik yeniden başlatmaz** (bu doğru/beklenen davranıştır, sonsuz döngüyü önler).

**Hızlı çözüm:**
```powershell
docker compose up -d
```

---

## Veritabanına bağlanamıyor (`could not connect to server` / 500 hataları)

**Hızlı çözüm:**
```powershell
docker compose ps postgres
```
`healthy` değilse:
```powershell
docker compose logs postgres --tail=50
docker compose restart postgres
```
30 saniye bekleyip `api` servisini de yeniden başlatın (postgres'in hazır olmasını beklemesi gerekir):
```powershell
docker compose restart api
```

---

## Groq LLM hatası — `429 Too Many Requests` / `rate_limit_exceeded`

**Belirti:** Worker loglarında `Rate limit reached ... tokens per day (TPD)`.

Bu **geçici değil, günlük kota** sorunudur — sistem zaten `llama-3.1-8b-instant` modeline geçirildi (ayrı, daha büyük bir kota havuzu) ve 429 durumunda 3 kez otomatik retry deniyor, ama günlük kota gerçekten dolduysa retry de işe yaramaz.

**Hızlı çözüm:**
1. [console.groq.com/settings/billing](https://console.groq.com/settings/billing) adresinden kalan kotayı kontrol edin.
2. Kota dolmuşsa: farklı bir Groq hesabı/API key'i `.env` dosyasında `GROQ_API_KEY` alanına yazıp `docker compose restart worker` çalıştırın.
3. Demo sırasında zaman yoksa: önceden taranmış mevcut verilerle devam edin (`GET /api/v1/companies?min_puan=0`) — bu, sistemin çalışmadığı anlamına gelmez, sadece o an yeni LLM analizi yapılamıyor demektir.

---

## Arama sonuç getirmiyor (boş liste dönüyor)

Bu **çoğu zaman bir hata değildir** — DuckDuckGo'nun o anki sonuçları her çalıştırmada değişebilir, bulunan adaylar kalite filtresine takılabilir (yanlış şehir, iş ilanı sitesi, kamu kurumu vb.).

**Hızlı çözüm:**
```powershell
docker compose logs worker --tail=100
```
loglarda `Sonuç kalite filtresinde elendi: ...` satırlarını arayın — bu, sistemin çalıştığını ama adayları haklı gerekçelerle elediğini gösterir. Farklı/daha genel bir sorgu deneyin (örn. "İstanbul CNC" yerine sadece "CNC İstanbul").

---

## `POST /api/v1/companies/scan` → 401 Unauthorized

Backend bu uç noktada **opsiyonel auth** kullanır: token gönderirseniz doğrulanır, göndermezseniz istek reddedilmez. 401 alıyorsanız muhtemelen **geçersiz/süresi dolmuş bir token gönderiliyor** (eksik değil).

**Hızlı çözüm:** `/auth/login` ile yeniden giriş yapıp taze bir `access_token` alın (varsayılan ömür 60 dakika).

---

## Türkçe karakterler (İ, ş, ğ) bozuk/soru işareti görünüyor

Bu genellikle **terminal/konsol encoding sorunudur, veri bozuk değildir**. `curl`/PowerShell çıktısını dosyaya yazıp UTF-8 olarak açarak doğrulayın:
```powershell
curl ... -o cikti.json
Get-Content cikti.json -Encoding UTF8
```
API/veritabanı seviyesinde veri her zaman doğru UTF-8 olarak saklanır.

---

## Docker Compose değişikliği yaptım ama etkisi görünmüyor

`docker-compose.yml` dosyasında bir değişiklik (örn. `restart:` politikası, ortam değişkeni) yaptıysanız, **`docker compose restart` bunu uygulamaz** — sadece içindeki süreci yeniden başlatır, container'ın kendisini yeniden oluşturmaz.

**Hızlı çözüm:**
```powershell
docker compose up -d
```
Bu komut, değişen servisleri otomatik olarak yeniden oluşturur (verinizi kaybetmezsiniz — Postgres verisi ayrı bir named volume'da tutulur).

---

## Delphi `.exe` açılmıyor / eski davranış sergiliyor

Mevcut derlenmiş `OsintFrontend.exe`, en son eklenen özellikleri (kalıcı oturum, sonuç tablosu, Job Status) içermez — bu ortamda RAD Studio olmadığı için kaynak kod derlenemedi. Bu **beklenen bir durumdur**, hata değildir; backend eski `.exe` ile tam uyumludur.

**Hızlı çözüm (yedek plan):** Delphi yerine Swagger UI (`http://localhost:8000/docs`) üzerinden aynı akışı (login → search → scan → scan-status → companies) canlı gösterin.

---

## Hiçbir şey işe yaramıyorsa — tam sıfırlama

```powershell
cd autonomous-osint-agent
docker compose down
docker compose up -d
docker compose ps
```
`docker compose down` container'ları siler ama **Postgres verisi named volume'da kalıcıdır**, kaybolmaz. Sadece servisler temiz bir durumdan yeniden başlar.
