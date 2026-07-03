import asyncio
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

# .env dosyasından API anahtarını yükle
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class AnalizMotoru:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-3.5-flash')
        self.prompt_template = """
        Şu ham metni oku, içindeki isimleri ve ünvanları bul. 
        Sadece ve sadece geçerli bir JSON çıktısı ver. Başka hiçbir açıklama ekleme.
        Format: {{"kisi_adi": "...", "unvan": "...", "firma_adi": "...", "guven_skoru": 80, "analiz_tarihi": "2026-07-03"}}
        Metin: {ham_metin}
        """

    async def analiz_et(self, ham_metin):
        try:
            full_prompt = self.prompt_template.format(ham_metin=ham_metin)
            response = await asyncio.to_thread(self.model.generate_content, full_prompt)
            
            text = response.text
            print(f"DEBUG - LLM'den Gelen Ham Veri: {text}") # <--- BU SATIRI EKLEDİK
            
            # Temizlik
            clean_text = text.replace("```json", "").replace("```", "").strip()
            
            # JSON'a çevir
            return json.loads(clean_text)
            
        except Exception as e:
            # Hata satırını da yazdır
            import traceback
            traceback.print_exc()
            return {"hata": "JSON_PARSE_ERROR", "kisi_adi": "Analiz edilemedi"}
        
async def main():
    motor = AnalizMotoru()
    # Test verisi
    sonuc = await motor.analiz_et("ABC Teknoloji'nin CEO'su Ahmet Yılmaz yeni ofisini tanıttı.")
    print(json.dumps(sonuc, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())