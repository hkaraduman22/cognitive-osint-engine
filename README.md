# Cognitive OSINT Engine

Bu proje, belirlenen sektörlerdeki firmaları ve profesyonelleri yasal açık kaynaklardan (OSINT) tespit eden akıllı bir veri toplama ve analiz sistemidir.

## Proje Mimarisi ve Ekip
Sistem 4 temel modülden oluşmaktadır:
- **Core API & Altyapı:** Veritabanı ve servis yönetimi.
- **Veri Toplama (Scraper):** Ham veri ve metin çıkarma.
- **Analiz Modülü (NLP):** Metin işleme, unvan ayıklama ve güven puanlama.
- **Yönetim Paneli (Delphi):** Görselleştirme ve raporlama.

## Geliştirici Notu (Geliştirici 3)
Analiz motoru (`nlp-analiz`) iskeleti kurulmuştur. 
- `analiz.py` dosyası üzerinden NLP mantığı ve LLM entegrasyonu geliştirilmektedir.
- **Veri Formatı:** Tüm sistemler arası iletişim JSON formatında standardize edilmiştir.

## 🔗 Veri Sözleşmesi (Data Contract)
Analiz motorundan çıkan (ve Altyapı/Delphi tarafından beklenen) veri paketi formatı:

```json
{
  "kisi_adi": "string",
  "unvan": "string",
  "firma_adi": "string",
  "guven_skoru": "int",
  "analiz_tarihi": "YYYY-MM-DD"
}