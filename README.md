# Cognitive OSINT Engine

Bu proje, belirlenen sektörlerdeki firmaları ve profesyonelleri yasal açık kaynaklardan (OSINT) tespit eden akıllı bir veri toplama ve analiz sistemidir.

## Proje Mimarisi ve Ekip
Sistem 4 temel modülden oluşmaktadır:
- **Core API & Altyapı:** Veritabanı ve servis yönetimi.
- **Veri Toplama (Scraper):** Ham veri ve metin çıkarma.
- **Analiz Modülü (NLP):** Metin işleme, unvan ayıklama ve güven puanlama.
- **Yönetim Paneli (Delphi):** Görselleştirme ve raporlama.

## Geliştirici Notu (Geliştirici 3)
Analiz motoru (nlp-analiz) iskeleti kurulmuştur. 
- `analiz.py` dosyası üzerinden NLP mantığı geliştirilmektedir.
- Veri formatı: JSON (Standardize edilmiştir).

## Kurulum
1. Gerekli kütüphaneleri yükleyin: `pip install -r requirements.txt`
2. Analiz modülünü test etmek için `python analiz.py` komutunu kullanın.