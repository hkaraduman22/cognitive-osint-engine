import asyncio
import json
import os
import re
import urllib.error
import urllib.request
from datetime import date
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover - optional dependency guard
    genai = None


class AnalizSonucu(BaseModel):
    name: str
    website: str | None = None
    location: str | None = None
    description: str | None = None
    source: str | None = None
    confidence_score: int = Field(ge=0, le=100)
    analiz_tarihi: str


load_dotenv()


class AnalizMotoru:
    def __init__(self):
        self.model = None
        self.prompt_template = (
            "Web sitesinin ham metnini analiz et. Bu metinden şirketleri bul, her biri için "
            "name, website, location, description, source ve confidence_score (0-100) alanlarını JSON array halinde döndür. "
            "Yalnızca JSON array ver. Ek açıklama yazma. Örnek:\n"
            "[{{\"name\":\"Örnek Şirket\",\"website\":\"https://example.com\",\"location\":\"İstanbul\", "
            "\"description\":\"Türkiye merkezli yazılım şirketi\",\"source\":\"web\",\"confidence_score\":92}}]\n"
            "Metin: {ham_metin}"
        
        )
        self.api_url = os.getenv("COMPANY_API_URL")
        self.api_key = os.getenv("COMPANY_API_KEY")
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
        score = 50

        if any(word in text for word in ["şirket", "firma", "kurumsal", "kurucu", "genel müdür", "lider"]):
            score += 15
        if any(word in text for word in ["teknoloji", "yazılım", "ai", "yapay zeka", "sistem"]):
            score += 10
        if any(word in text for word in ["yıl", "yıllık", "deneyim", "başarı"]):
            score += 8
        if len(ham_metin.split()) > 30:
            score += 5

        score = max(0, min(100, score))
        return {
            "name": "Belirsiz",
            "website": None,
            "location": None,
            "description": "Belirsiz",
            "source": None,
            "confidence_score": score,
            "analiz_tarihi": date.today().isoformat(),
            "hata": reason,
        }

    def _clean_text_for_llm(self, ham_metin: str) -> str:
        cleaned_text = ham_metin
        cleaned_text = re.sub(r"(?is)<script.*?>.*?</script>", " ", cleaned_text)
        cleaned_text = re.sub(r"(?is)<style.*?>.*?</style>", " ", cleaned_text)
        cleaned_text = re.sub(r"<[^>]+>", " ", cleaned_text)
        patterns = [
            r"(?im)^\s*(home|about|contact|services|products|privacy|terms|sitemap|blog|career|login|register|faq|support).*",
            r"(?im)^(follow us|connect with us|social media|subscribe to|newsletter).*",
            r"(?im)\b(privacy policy|terms of service|cookie policy|cookies|powered by)\b",
            r"(?im)\b(menu|navigation|footer|header|sidebar|site map)\b",
            r"https?://\S+",
            r"www\.\S+",
            r"\|",
            r"©.*",
            r"Cookie[s]? Policy.*",
        ]
        for pattern in patterns:
            cleaned_text = re.sub(pattern, " ", cleaned_text)
        cleaned_text = re.sub(r"\s{2,}", " ", cleaned_text).strip()
        return cleaned_text[:15000]

    def _extract_json_payload(self, raw_text: str) -> str:
        text = raw_text.strip()
        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "").strip()
        if text.startswith("["):
            start = text.find("[")
            end = text.rfind("]")
        else:
            start = text.find("{")
            end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1]
        return text

    async def analiz_et(self, ham_metin: str) -> list[dict[str, Any]]:
        if not ham_metin or not ham_metin.strip():
            return [self._build_fallback_result("", "Boş metin")]

        cleaned_text = self._clean_text_for_llm(ham_metin)
        prompt = self.prompt_template.format(ham_metin=cleaned_text)

        if self.model is None:
            return [self._build_fallback_result(ham_metin, "LLM modeli hazır değil")]

        try:
            if self.model is None:
                return self._build_fallback_result(ham_metin, "LLM modeli hazır değil")

            response = await asyncio.to_thread(self.model.generate_content, prompt)
            text = self._extract_json_payload(response.text)
            data = json.loads(text)

            if isinstance(data, dict):
                data = [data]

            results = []
            for item in data:
                # 1. Otomatik tarih damgasını ekle
                item["analiz_tarihi"] = date.today().isoformat()
                
                # 2. Veriyi Pydantic modeliyle doğrula
                valid_data = AnalizSonucu(**item)
                
                # 3. Model verisini sözlüğe çevirip listeye ekle
                results.append(valid_data.model_dump() if hasattr(valid_data, "model_dump") else valid_data.dict())

            # 4. Sadece 85 ve üzeri güven skoruna sahip olanları süz
            elites = [item for item in results if item.get("confidence_score", 0) >= 85]
            
            # 5. API'ye gönderim (Eğer API adresi tanımlıysa)
            if elites and self.api_url:
                status, error = await asyncio.to_thread(self._post_companies_to_api, elites)
                if error:
                    print(f"API gönderme hatası: {error}")
                else:
                    print(f"{len(elites)} elit şirket API'ye gönderildi, durum: {status}")

            return results

        except ValidationError as ve:
            print(f"SÖZLEŞME HATASI (Veri formatı yanlış): {ve}")
            return [self._build_fallback_result(ham_metin, "VALIDATION_ERROR")]
        except json.JSONDecodeError as exc:
            print(f"JSON_PARSE_ERROR: {exc}")
            return [self._build_fallback_result(ham_metin, "JSON_PARSE_ERROR")]
        except Exception as exc:
            print(f"GENEL HATA: {exc}")
            return [self._build_fallback_result(ham_metin, "LLM_ERROR")]

    def _post_companies_to_api(self, companies: list[dict[str, Any]]) -> tuple[int, str | None]:
        if not self.api_url:
            return 0, "COMPANY_API_URL yok"

        payload = json.dumps(companies, ensure_ascii=False).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        request = urllib.request.Request(self.api_url, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return response.getcode(), None
        except urllib.error.HTTPError as exc:
            return exc.code, str(exc)
        except urllib.error.URLError as exc:
            return 0, str(exc)


async def main():
    motor = AnalizMotoru()
    sonuc = await motor.analiz_et("ABC Teknoloji'nin CEO'su Ahmet Yılmaz yeni ofisini tanıttı.")
    print(json.dumps(sonuc, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())