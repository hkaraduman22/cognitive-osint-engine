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
_core_api_env = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "autonomous-osint-agent",
    "core-api",
    ".env",
)
if os.path.exists(_core_api_env):
    load_dotenv(_core_api_env, override=False)
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

        # TEMİZ KOD: Süslü parantez çakışmalarını engellemek için {ham_metin} yerine [HAM_METIN] kullanılmıştır.
        self.prompt_template: str = (
            "Web sitesinin ham metnini analiz et. Bu metinden şirketleri ve varsa bu şirketlerin yetkililerini, kurucularını veya emlak danışmanlarını bul. "
            "Her şirket için şu alanları içeren bir JSON array döndür:\n"
            "name, website, location, description, source, confidence_score (0-100 arası) "
            "ve şirket yetkilileri için bir 'officials' listesi (içinde full_name và title olan objeler).\n\n"
            "UYARI: Eğer metinde yetkili adı geçmiyorsa, 'officials' listesini boş bırakma! "
            "FastAPI doğrulaması için listeye otomatik olarak şu objeyi ekle: {\"full_name\": \"Belirtilmemiş\", \"title\": \"Bilinmeyen Unvan\"}.\n\n"
            "Yalnızca JSON array döndür, açıklama yazma. Metin:\n[HAM_METIN]"
        )

    def _clean_text_for_llm(self, raw_text: str) -> str:
        """LLM maliyetini ve gürültüyü azaltmak için ham web metnini temizler."""
        text = re.sub(
            r"<(script|style|nav|footer|header|aside)\b[^>]*>.*?</\1>",
            " ",
            raw_text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"https?://\S+", " ", text)
        text = re.sub(r"\b(?:privacy policy|cookie policy)\b", " ", text, flags=re.IGNORECASE)
        return re.sub(r"\s{2,}", " ", text).strip()[:15000]

    def _build_fallback_result(self, reason: str) -> dict[str, Any]:
        """
        Herhangi bir hata durumunda sistemin durmaması için koruyucu fallback verisi üretir.
        """
        return {
            "name": "Belirsiz", "website": None, "location": "Denizli",
            "description": "Fallback", "source": "web", "confidence_score": 50,
            "analiz_tarihi": date.today().isoformat(), "hata": reason,
            "officials": [{"full_name": "Belirtilmemiş", "title": "Bilinmeyen Unvan"}]
        }

    async def analiz_et(
        self,
        ham_metin: str,
        search_history_id: int | None = None,
        source_url: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Gelen ham metni temizler, Groq API üzerinden LLM analizine gönderir ve doğrulanmış sonuçları döner.
        """
        if not ham_metin or not ham_metin.strip():
            return [self._build_fallback_result("Boş metin")]

        if self.client is None:
            return [self._build_fallback_result("Groq client hazır değil")]

        # HTML etiketlerinin temizlenmesi ve gereksiz boşlukların sıkıştırılması
        cleaned_text = self._clean_text_for_llm(ham_metin)

        try:
            # KRİTİK HATA DÜZELTMESİ: .format() yerine güvenli .replace() kullanılarak
            # metindeki JS/CSS süslü parantezlerinin format motorunu çökertmesi kalıcı olarak engellenmiştir.
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

            # JSON yapısının array formatına normalize edilmesi lojiği
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

            results: list[dict[str, Any]] = []
            if isinstance(data, list):
                for item in data:
                    item["analiz_tarihi"] = date.today().isoformat()

                    # Eksik yetkili bilgilerinin şema doğrulaması için tamamlanması
                    if "officials" in item and isinstance(item["officials"], list):
                        for off in item["officials"]:
                            if not off.get("full_name"):
                                off["full_name"] = "Belirtilmemiş"
                            if not off.get("title"):
                                off["title"] = "Unvan Belirtilmemiş"
                    else:
                        item["officials"] = [{"full_name": "Belirtilmemiş", "title": "Bilinmeyen Unvan"}]

                    try:
                        # Pydantic şema doğrulaması (Validation)
                        valid_data = AnalizSonucu(**item)
                        results.append(valid_data.model_dump())
                    except Exception as val_err:
                        logger.warning(f"Format hatası nedeniyle öğe atlandı: {val_err}")
                        continue

            # Sadece 85 puan ve üzeri olan yüksek nitelikli elit şirketlerin filtrelenmesi
            elites: list[dict[str, Any]] = [item for item in results if item.get("confidence_score", 0) >= 85]

            if elites and self.api_url:
                await self._post_companies_to_api_async(
                    elites,
                    search_history_id=search_history_id,
                    source_url=source_url,
                )

            return results

        except Exception as e:
            logger.error(f"GROQ_ERROR: {e}")
            return [self._build_fallback_result(str(e))]

    async def _post_companies_to_api_async(
        self,
        companies: list[dict[str, Any]],
        search_history_id: int | None = None,
        source_url: str | None = None,
    ) -> None:
        """
        Nitelikli elit verileri Core API'ye asenkron olarak güvenli şekilde POST eder.
        """
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        if not httpx:
            return

        async with httpx.AsyncClient() as client:
            for c in companies:
                payload: dict[str, Any] = {
                    "name": c.get("name", "Bilinmeyen Firma"),
                    "industry": c.get("description", "Avukat/Hukuk"),
                    "city": c.get("location", "Denizli"),
                    "confidence_score": c.get("confidence_score", 85),
                    "officials": c.get("officials", [{"full_name": "Belirtilmemiş", "title": "Bilinmeyen Unvan"}])
                }
                if search_history_id is not None:
                    payload["search_history_id"] = search_history_id
                if source_url:
                    payload["source_url"] = source_url
                try:
                    resp = await client.post(self.api_url, json=payload, headers=headers, timeout=15)
                    if resp.status_code in (200, 201):
                        logger.info(f"   BAŞARI: {payload['name']} ve yetkilileri sisteme kaydedildi.")
                    else:
                        logger.error(f"   API Reddi: {resp.status_code} - {resp.text}")
                except Exception as e:
                    logger.error(f"   API bağlantı hatası: {e}")
