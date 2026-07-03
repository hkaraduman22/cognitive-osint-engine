"""
Geliştirici 3: Analiz ve NLP Motoru
Görev: Ham metinleri analiz eder, kişi/unvan bilgilerini çıkarır ve
sistem standartlarına uygun JSON formatında paketler.
"""

import json

class AnalizMotoru:
    def __init__(self):
        self.version = "1.0.0"
        print(f"Analiz Motoru v{self.version} başlatıldı.")

    def ham_metni_ayristir(self, ham_metin):
        """
        Girdi: Ham web metni (str)
        Çıktı: Sözleşmeye uygun JSON paketi (dict)
        """
        # TODO: Burada LLM (Gemini/OpenAI) API çağrısı yapılacak.
        # Şimdilik örnek bir çıktı hazırlıyoruz.
        
        analiz_sonucu = {
            "kisi_adi": "Örnek Yönetici",
            "unvan": "Genel Müdür",
            "firma_adi": "Bilinmeyen Firma",
            "guven_skoru": 0, # LLM'in cevabına göre doldurulacak
            "analiz_tarihi": "2026-07-03"
        }
        
        return analiz_sonucu

    def json_cikti_uret(self, veri_dict):
        """
        Veriyi Delphi ve Altyapı'nın (Dev 1) beklediği formata çevirir.
        """
        return json.dumps(veri_dict, ensure_ascii=False, indent=4)

# Test Etmek İçin:
if __name__ == "__main__":
    motor = AnalizMotoru()
    ham_veri = "ABC Teknoloji Genel Müdürü Ahmet Bey yeni ofise geçti."
    
    # 1. Analiz et
    sonuc_dict = motor.ham_metni_ayristir(ham_veri)
    
    # 2. JSON'a çevir ve göster
    json_cikti = motor.json_cikti_uret(sonuc_dict)
    print("--- Geliştirici 1'e Gidecek Veri Paketi ---")
    print(json_cikti)