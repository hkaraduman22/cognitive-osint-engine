import asyncio
import json
import logging
import os
import re
from datetime import date
from typing import Any, List

from dotenv import load_dotenv
from pydantic import BaseModel, Field

try:
    from groq import AsyncGroq
except ImportError:
    AsyncGroq = None

try:
    import httpx
except ImportError:
    httpx = None


class OfficialGiris(BaseModel):
    full_name: str
    title: str | None = "Unvan Belirtilmemiş"
    linkedin_url: str | None = None


class AnalizSonucu(BaseModel):
    name: str
    website: str | None = None
    location: str | None = None
    description: str | None = None
    source: str | None = None
    confidence_score: int = Field(ge=0, le=100)
    analiz_tarihi: str
    officials: List[OfficialGiris] = []


load_dotenv()
logger = logging.getLogger("AnalizMotoru")


class AnalizMotoru:
    def __init__(self):
        groq_api_key = os.getenv("GROQ_API_KEY")
        if AsyncGroq and groq_api_key:
            self.client = AsyncGroq(api_key=groq_api_key)
        else:
            self.client = None

        self.model = "llama-3.3-70b-versatile"
        self.api_url = os.getenv("COMPANY_API_URL", "http://127.0.0.1:8000/api/v1/companies")
        self.api_key = os.getenv("COMPANY_API_KEY")

        self.prompt_template = (
            "Web sitesinin ham metnini analiz et. Bu metinden şirketleri ve varsa bu şirketlerin yetkililerini, kurucularını veya emlak danışmanlarını bul. "
            "Her şirket için şu alanları içeren bir JSON array döndür:\n"
            "name, website, location, description, source, confidence_score (0-100 arası) "
            "ve şirket yetkilileri için bir 'officials' listesi (içinde full_name ve title olan objeler).\n\n"
            "UYARI: Eğer metinde yetkili adı geçmiyorsa, 'officials' listesini boş bırakma! "
            "FastAPI doğrulaması için listeye otomatik olarak şu objeyi ekle: {开口}\"full_name\": \"Belirtilmemiş\", \"title\": \"Bilinmeyen Unvan\"{闭口}.\n\n"
            "Yalnızca JSON array döndür, açıklama yazma. Metin:\n{ham_metin}"
        )
        self.prompt_template = self.prompt_template.replace("开口", "{").replace("闭口", "}")

    def _build_fallback_result(self, reason: str) -> dict[str, Any]:
        return {
            "name": "Belirsiz", "website": None, "location": "Denizli",
            "description": "Fallback", "source": "web", "confidence_score": 50,
            "analiz_tarihi": date.today().isoformat(), "hata": reason,
            "officials": [{"full_name": "Belirtilmemiş", "title": "Bilinmeyen Unvan"}]
        }

    async def analiz_et(self, ham_metin: str) -> list[dict[str, Any]]:
        if not ham_metin or not ham_metin.strip():
            return [self._build_fallback_result("Boş metin")]

        if self.client is None:
            return [self._build_fallback_result("Groq client hazır değil")]

        cleaned_text = re.sub(r"<[^>]+>", " ", ham_metin)
        cleaned_text = re.sub(r"\s{2,}", " ", cleaned_text).strip()[:15000]

        try:
            response = await self.client.chat.completions.create(
                messages=[
                    {"role": "system",
                     "content": "Sen bir OSINT veri analiz uzmanısın. Çıktı olarak sadece geçerli bir JSON array ver."},
                    {"role": "user", "content": self.prompt_template.format(ham_metin=cleaned_text)}
                ],
                model=self.model,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content.strip()
            data = json.loads(content)

            if isinstance(data, dict):
                liste_trouvee = None
                for k, v in data.items():
                    if isinstance(v, list):
                        liste_trouvee = v
                        break
                if liste_trouvee is not None:
                    data = liste_trouvee
                elif any(key in data for key in ["name", "confidence_score"]):
                    data = [data]
                else:
                    data = []

            results = []
            if isinstance(data, list):
                for item in data:
                    item["analiz_tarihi"] = date.today().isoformat()

                    if "officials" in item and isinstance(item["officials"], list):
                        for off in item["officials"]:
                            if not off.get("full_name"):
                                off["full_name"] = "Belirtilmemiş"
                            if not off.get("title"):
                                off["title"] = "Unvan Belirtilmemiş"
                    else:
                        item["officials"] = [{"full_name": "Belirtilmemiş", "title": "Bilinmeyen Unvan"}]

                    try:
                        valid_data = AnalizSonucu(**item)
                        results.append(valid_data.model_dump())
                    except Exception as val_err:
                        logger.warning(f"Format hatası nedeniyle öğe atlandı: {val_err}")
                        continue

            elites = [item for item in results if item.get("confidence_score", 0) >= 85]

            if elites and self.api_url:
                await self._post_companies_to_api_async(elites)

            return results

        except Exception as e:
            logger.error(f"GROQ_ERROR: {e}")
            return [self._build_fallback_result(str(e))]

    async def _post_companies_to_api_async(self, companies: list[dict[str, Any]]) -> None:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        if not httpx:
            return

        async with httpx.AsyncClient() as client:
            for c in companies:
                payload = {
                    "name": c.get("name", "Bilinmeyen Firma"),
                    "industry": c.get("description", "Avukat/Hukuk"),
                    "city": c.get("location", "Denizli"),
                    "confidence_score": c.get("confidence_score", 85),
                    "officials": c.get("officials", [{"full_name": "Belirtilmemiş", "title": "Bilinmeyen Unvan"}])
                }
                try:
                    resp = await client.post(self.api_url, json=payload, headers=headers, timeout=15)
                    if resp.status_code in (200, 201):
                        logger.info(f"   BAŞARI: {payload['name']} ve yetkilileri kaydedildi.")
                    else:
                        logger.error(f"   API Reddi: {resp.status_code} - {resp.text}")
                except Exception as e:
                    logger.error(f"   API bağlantı hatası: {e}")