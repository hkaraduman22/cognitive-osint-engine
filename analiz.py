import asyncio
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

# --- Veri Sözleşmesi (Schema) ---
class AnalizSonucu(BaseModel):
    kisi_adi: str
    unvan: str
    firma_adi: str
    guven_skoru: int = Field(ge=0, le=100)
    analiz_tarihi: str

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
            
            text = response.text.replace("```json", "").replace("```", "").strip()
            
            # JSON'ı sözlüğe çevir
            data = json.loads(text)
            
            # Pydantic ile "Sözleşme Doğrulaması" yap (Bekçi devrede!)
            valid_data = AnalizSonucu(**data)
            
            # Doğrulanmış veriyi sözlük olarak döndür
            return valid_data.model_dump()
            
        except ValidationError as ve:
            print(f"SÖZLEŞME HATASI (Veri formatı yanlış): {ve}")
            return {"hata": "VALIDATION_ERROR", "detay": str(ve)}
        except Exception as e:
            print(f"GENEL HATA: {e}")
            return {"hata": "JSON_PARSE_ERROR", "kisi_adi": "Analiz edilemedi"}

async def main():
    motor = AnalizMotoru()
    # Test verisi
    sonuc = await motor.analiz_et("ABC Teknoloji'nin CEO'su Ahmet Yılmaz yeni ofisini tanıttı.")
    print(json.dumps(sonuc, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())