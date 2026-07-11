# Cognitive OSINT Engine

Yasal ve herkese açık kaynaklardan firma bilgileri toplayan, içerikleri analiz eden ve sonuçları kullanıcı sorgularıyla ilişkilendiren B2B firma rehberi MVP'sidir.

Proje iki günlük kurtarma çalışması kapsamında mevcut kod korunarak çalışır hâle getirilmiştir. Docker, Redis veya Memurai gerektirmez. Süreçler arası mesaj kuyruğu varsayılan olarak yerel SQLite kullanır.

## MVP özellikleri

- JWT tabanlı kullanıcı kaydı ve girişi
- Arama geçmişi
- DDGS ve yapılandırılmış açık kaynaklar üzerinden web taraması
- HTML metni ve iletişim bilgisi çıkarma
- SQLite tabanlı kalıcı mesaj kuyruğu
- Groq tabanlı firma analizi ve güven puanı
- Firma–arama geçmişi ilişkisi
- Kaynak URL ve son güncelleme tarihi
- Unicode/Türkçe uyumlu firma tekilleştirme
- Delphi VCL masaüstü istemcisi
- Docker'sız Windows kurulumu

## Mimari

```text
Delphi VCL
    │ HTTP/JWT
    ▼
FastAPI Core API
    │ arama kimliği
    ▼
Scraper Bot ──► SQLite Queue ──► Analiz Listener
                                      │
                                      ▼
                                  Groq LLM
                                      │
                                      ▼
                            Firma API'si / SQLite DB
```

Ana bileşenler:

- `autonomous-osint-agent/core-api`: FastAPI ve SQLAlchemy backend
- `scraper-bot`: açık web kaynaklarını tarayan producer
- `redis_listener.py`: SQLite/Redis kuyruğunu tüketen analiz worker'ı
- `analiz.py`: metin temizleme, Groq analizi ve güven puanı filtresi
- `delphi-vcl-frontend`: masaüstü kullanıcı arayüzü
- `tests`: kanonik MVP test paketi

## Gereksinimler

- Windows 10/11
- Python 3.12 veya üzeri
- İnternet bağlantısı (yalnızca canlı web taraması ve Groq için)
- İsteğe bağlı Groq API anahtarı

Docker, WSL, Redis ve Memurai zorunlu değildir.

## Kurulum

PowerShell terminalini proje kökünde açın:

```powershell
cd C:\Users\Admin\Desktop\camart
```

Sanal ortam yoksa oluşturun:

```powershell
py -m venv .venv
```

Sanal ortamı etkinleştirin:

```powershell
.\.venv\Scripts\Activate.ps1
```

Bağımlılıkları yükleyin:

```powershell
python -m pip install -r autonomous-osint-agent\core-api\requirements.txt
```

## Ortam ayarları

Örnek dosyayı kopyalayın:

```powershell
Copy-Item autonomous-osint-agent\core-api\.env.example autonomous-osint-agent\core-api\.env
```

`.env` içindeki zorunlu olmayan Groq anahtarını kendi hesabınıza göre ayarlayın:

```dotenv
GROQ_API_KEY=
```

Anahtar boşsa sistem durmaz; analiz motoru kontrollü fallback sonucu üretir. Gerçek LLM firma sınıflandırması için anahtar gereklidir.

Gizli anahtarları Git'e eklemeyin.

## Çalıştırma

### Kolay yöntem

Proje kökünde:

```powershell
.\start_services.bat
```

Bu betik iki terminal açar:

1. FastAPI — `http://127.0.0.1:8000`
2. SQLite Queue Listener

Swagger:

```text
http://127.0.0.1:8000/docs
```

### Servisleri elle başlatma

Birinci PowerShell:

```powershell
cd autonomous-osint-agent\core-api
..\..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

İkinci PowerShell:

```powershell
cd C:\Users\Admin\Desktop\camart
.\.venv\Scripts\python.exe redis_listener.py
```

### Manuel kuyruk testi

Üçüncü PowerShell:

```powershell
.\.venv\Scripts\python.exe test_producer.py
```

Listener terminalinde `Kuyruktan Görev Alındı` mesajı görülmelidir.

## Test

Tüm kanonik test paketi:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Beklenen sonuç:

```text
14 passed
```

Statik kod kontrolü:

```powershell
.\.venv\Scripts\ruff.exe check autonomous-osint-agent\core-api\app analiz.py redis_listener.py scraper-bot tests
```

Beklenen sonuç:

```text
All checks passed!
```

## Demo akışı

Önerilen sorgu:

```text
İstanbul CNC freze üreticileri
```

Sunum sırası:

1. API ve listener'ı başlatın.
2. Delphi uygulamasından kayıt olun veya giriş yapın.
3. Arama ekranına örnek sorguyu girin.
4. Arama geçmişi kimliğinin oluştuğunu gösterin.
5. Scraper'ın açık kaynakları taradığını gösterin.
6. Listener'ın SQLite kuyruğundan mesaj aldığını gösterin.
7. Sonuç ekranında firma, şehir, sektör, güven puanı ve kaynak URL'yi gösterin.

Canlı internet veya LLM anahtarı kullanılamıyorsa test edilmiş yerel akış için `test_producer.py` kullanılabilir.

İkinci örnek sorgu:

```text
Avcılar Arçelik servisi
```

## Kuyruk backend'i

Varsayılan:

```dotenv
QUEUE_BACKEND=sqlite
OSINT_QUEUE_DB=
OSINT_REDIS_QUEUE=osint_raw_queue
```

SQLite kuyruğu ayrı Windows süreçleri arasında çalışır ve harici servis gerektirmez.
`OSINT_QUEUE_DB` boş bırakılırsa proje kökündeki `osint_queue.db` otomatik kullanılır.

Gelecekte Redis kullanılacaksa:

```dotenv
QUEUE_BACKEND=redis
REDIS_URL=redis://localhost:6379/0
```

## Veri ve etik sınırlar

Sistem yalnızca kamuya açık ve yasal kaynaklar için tasarlanmıştır. CAPTCHA, oturum kontrolü veya platform güvenliği aşılmaz. Gizli kişisel veri toplanmaz ve yayımlanmamış iletişim bilgisi tahmin edilmez.

## Bilinen sınırlamalar

- Canlı web sonuçları kaynakların erişilebilirliğine göre değişebilir.
- Gerçek LLM analizi için `GROQ_API_KEY` gerekir.
- Personel endpoint'i MVP'de örnek yanıt üretmektedir.
- Firma tekilleştirme küçük MVP veri hacmine göre uygulama katmanında yapılır.
- Proje içinde eski geliştirme kopyaları bulunur; kanonik kök bu README'nin bulunduğu dizindir.
- SQLite kuyruğu yüksek trafikli dağıtık üretim sistemi için değil, yerel MVP için seçilmiştir.
- Kalan test uyarıları üçüncü taraf Starlette ve `python-jose` paketlerinden gelir.

## Teslim durumu

- API başlangıcı: başarılı
- SQLite süreçler arası kuyruk: başarılı
- Canlı scraper: başarılı
- Arama–firma ilişkisi: başarılı
- Kaynak URL ve güncelleme tarihi: başarılı
- Tekilleştirme ve veri doğrulama: başarılı
- Kanonik test paketi: 14/14 başarılı
- Statik analiz: başarılı
