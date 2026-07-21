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
    field_of_work: str | None = None
    city: str | None = None
    country: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    confidence_score: int = Field(ge=0, le=100, default=85)


class AnalizSonucu(BaseModel):
    name: str
    industry: str | None = None
    sub_industry: str | None = None
    field_of_activity: str | None = None
    company_size: str | None = None
    country: str | None = None
    location: str | None = None  # City
    website: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    map_location: str | None = None
    foundation_year: int | None = None
    description: str | None = None
    source: str | None = None
    confidence_score: int = Field(ge=0, le=100, default=85)
    analiz_tarihi: str | None = None
    officials: List[OfficialGiris] = []


load_dotenv()
logger = logging.getLogger("AnalizMotoru")


class AnalizMotoru:
    def __init__(self) -> None:
        groq_api_key: str | None = os.getenv("GROQ_API_KEY")
        if AsyncGroq and groq_api_key:
            self.client = AsyncGroq(api_key=groq_api_key)
        else:
            self.client = None

        self.model: str = "llama-3.3-70b-versatile"
        self.api_url: str = os.getenv("COMPANY_API_URL", "http://127.0.0.1:8000/api/v1/companies")
        self.api_key: str | None = os.getenv("COMPANY_API_KEY")

        self.prompt_template: str = (
            "Web sitesinin ham metnini analiz et. Bu metinden şirketleri ve varsa bu şirketlerin yetkililerini (yönetim kadrosu vb.) bul.\n"
            "Her şirket için şu alanları içeren bir JSON array döndür:\n"
            "name, industry, sub_industry, field_of_activity, company_size, country, location (şehir), website, phone, email, address, map_location, foundation_year (sayı), description, source, confidence_score (0-100 arası)\n"
            "ve şirket yetkilileri için bir 'officials' listesi (içinde full_name, title, field_of_work, city, country, email, phone, linkedin_url, confidence_score olan objeler).\n\n"
            "EKSTRA TALİMATLAR: Eğer metin bir iş ilanı veya kariyer sayfası ise, açık pozisyonlardan yola çıkarak 'description' alanına şirketin departman yapısını ve organizasyon şemasını özetle. Eğer metin bir haber ise, 'description' alanına yeni yatırımları özetle ve haberde adı geçen yeni yöneticileri 'officials' listesine ekle.\n\n"
            "UYARI: Eğer metinde yetkili adı geçmiyorsa, 'officials' listesini boş bırakma! "
            "FastAPI doğrulaması için listeye otomatik olarak şu objeyi ekle: {\"full_name\": \"Belirtilmemiş\", \"title\": \"Bilinmeyen Unvan\"}.\n\n"
            "Yalnızca JSON array döndür, açıklama yazma. Metin:\n[HAM_METIN]"
        )

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

        cleaned_text: str = re.sub(r"<[^>]+>", " ", ham_metin)
        cleaned_text = re.sub(r"\s{2,}", " ", cleaned_text).strip()[:15000]

        try:
            full_prompt: str = self.prompt_template.replace("[HAM_METIN]", cleaned_text)

            response = await self.client.chat.completions.create(
                messages=[
                    {"role": "system",
                     "content": "Sen bir OSINT veri analiz uzmanısın. Çıktı olarak sadece geçerli bir JSON array ver."},
                    {"role": "user", "content": full_prompt}
                ],
                model=self.model,
                response_format={"type": "json_object"}
            )

            content: str = response.choices[0].message.content.strip()
            data: Any = json.loads(content)

            if isinstance(data, dict):
                if "name" in data:
                    # Model tek bir şirket objesi döndürdüyse bunu listeye sar
                    data = [data]
                else:
                    # Model sonuçları {"companies": [...]} gibi sarmaladıysa
                    liste_trouvee = None
                    for k, v in data.items():
                        if isinstance(v, list):
                            liste_trouvee = v
                            break
                    
                    if liste_trouvee is not None:
                        data = liste_trouvee
                    elif "confidence_score" in data:
                        data = [data]
                    else:
                        data = []

            results: list[dict[str, Any]] = []
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

            elites: list[dict[str, Any]] = [item for item in results if item.get("confidence_score", 0) >= 85]

            if elites and self.api_url:
                await self._post_companies_to_api_async(elites)

            return results

        except Exception as e:
            logger.error(f"GROQ_ERROR: {e}")
            return [self._build_fallback_result(str(e))]

    async def _post_companies_to_api_async(self, companies: list[dict[str, Any]]) -> None:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        if not httpx:
            logger.error("HTTPX kütüphanesi bulunamadı, API'ye gönderilemiyor.")
            return

        async with httpx.AsyncClient() as client:
            for c in companies:
                payload: dict[str, Any] = {
                    "name": c.get("name", "Bilinmeyen Firma"),
                    "industry": c.get("industry", "Avukat/Hukuk"),
                    "sub_industry": c.get("sub_industry"),
                    "field_of_activity": c.get("field_of_activity"),
                    "company_size": c.get("company_size"),
                    "country": c.get("country"),
                    "city": c.get("location", "Denizli"),
                    "website": c.get("website"),
                    "phone": c.get("phone"),
                    "email": c.get("email"),
                    "address": c.get("address"),
                    "map_location": c.get("map_location"),
                    "foundation_year": c.get("foundation_year"),
                    "source": c.get("source"),
                    "description": c.get("description"),
                    "confidence_score": c.get("confidence_score", 85),
                    "officials": c.get("officials", [{"full_name": "Belirtilmemiş", "title": "Bilinmeyen Unvan", "confidence_score": 85}])
                }
                try:
                    resp = await client.post(self.api_url, json=payload, headers=headers, timeout=15)
                    if resp.status_code in (200, 201):
                        logger.info(f"   BAŞARI: {payload['name']} ve yetkilileri sisteme kaydedildi.")
                    else:
                        logger.error(f"   API Reddi: {resp.status_code} - {resp.text}")
                except Exception as e:
                    logger.error(f"   API bağlantı hatası: {e}")