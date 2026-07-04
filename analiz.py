import asyncio
import json
import os
from datetime import date
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover - optional dependency guard
    genai = None


class AnalizSonucu(BaseModel):
    kisi_adi: str
    unvan: str
    firma_adi: str
    guven_skoru: int = Field(ge=0, le=100)
    analiz_tarihi: str


load_dotenv()


class AnalizMotoru:
    def __init__(self):
        self.model = None
        self.prompt_template = """
        Şu ham metni oku. İçindeki kişinin adını, unvanını ve şirket adını bul.
        Ayrıca metnin güvenilirliğine göre 0-100 arasında bir güven skoru ver.
        Sadece geçerli bir JSON çıktısı ver. Başka açıklama ekleme.
        Format: {{"kisi_adi": "...", "unvan": "...", "firma_adi": "...", "guven_skoru": 80, "analiz_tarihi": "2026-07-03"}}
        Metin: {ham_metin}
        """
        self._configure_model()

    def _configure_model(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or genai is None:
            self.model = None
            return

        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-3.5-flash")
        except Exception as exc:  # pragma: no cover - depends on runtime environment
            print(f"LLM yapılandırma hatası: {exc}")
            self.model = None

    def _build_fallback_result(self, ham_metin: str, reason: str | None = None) -> dict[str, Any]:
        text = ham_metin.lower()
        score = 55

        if any(word in text for word in ["ceo", "cto", "kurucu", "genel müdür", "başkan", "lider", "ortağ"]):
            score += 20
        if any(word in text for word in ["teknoloji", "yazılım", "ai", "yapay zeka", "bilgi", "sistem"]):
            score += 10
        if any(word in text for word in ["yıl", "yıllık", "deneyim", "başarı", "ofis", "ünvan"]):
            score += 8
        if len(ham_metin.split()) > 20:
            score += 5

        score = max(0, min(100, score))
        return {
            "kisi_adi": "Belirsiz",
            "unvan": "Belirsiz",
            "firma_adi": "Belirsiz",
            "guven_skoru": score,
            "analiz_tarihi": date.today().isoformat(),
            "hata": reason,
        }

    def _extract_json_payload(self, raw_text: str) -> str:
        text = raw_text.strip()
        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "").strip()
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1]
        return text

    async def analiz_et(self, ham_metin: str) -> dict[str, Any]:
        if not ham_metin or not ham_metin.strip():
            return self._build_fallback_result("", "Boş metin")

        try:
            if self.model is None:
                return self._build_fallback_result(ham_metin, "LLM modeli hazır değil")

            full_prompt = self.prompt_template.format(ham_metin=ham_metin)
            response = await asyncio.to_thread(self.model.generate_content, full_prompt)
            text = self._extract_json_payload(response.text)
            data = json.loads(text)
            valid_data = AnalizSonucu(**data)

            if hasattr(valid_data, "model_dump"):
                return valid_data.model_dump()
            return valid_data.dict()

        except ValidationError as ve:
            print(f"SÖZLEŞME HATASI (Veri formatı yanlış): {ve}")
            return self._build_fallback_result(ham_metin, "VALIDATION_ERROR")
        except json.JSONDecodeError as exc:
            print(f"JSON_PARSE_ERROR: {exc}")
            return self._build_fallback_result(ham_metin, "JSON_PARSE_ERROR")
        except Exception as exc:
            print(f"GENEL HATA: {exc}")
            return self._build_fallback_result(ham_metin, "LLM_ERROR")


async def main():
    motor = AnalizMotoru()
    sonuc = await motor.analiz_et("ABC Teknoloji'nin CEO'su Ahmet Yılmaz yeni ofisini tanıttı.")
    print(json.dumps(sonuc, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())