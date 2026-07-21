import asyncio
import json
import logging
import os
import re
import unicodedata
from datetime import date
from typing import Any, List

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

try:
    from groq import AsyncGroq, RateLimitError
except ImportError:
    AsyncGroq = None
    RateLimitError = Exception

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
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    description: str | None = None
    source: str | None = None
    confidence_score: int = Field(ge=0, le=100)
    analiz_tarihi: str
    officials: List[OfficialGiris] = []

    @field_validator("location", mode="before")
    @classmethod
    def normalize_location(cls, value: Any) -> str | None:
        """
        LLM 'location' alanını bazen dict olarak dönüyor (örn. {"city": "İstanbul", "district": "Kartal"}).
        Pydantic sadece string kabul ettiği için bu durumda kayıt tamamen düşüyordu (validation error).
        Burada dict'i "şehir, ilçe" formatında bir string'e çeviriyoruz; bilinmeyen bir şema gelirse
        dict içindeki tüm basit değerleri birleştirerek veri kaybını en aza indiriyoruz.
        """
        if value is None or isinstance(value, str):
            return value
        if isinstance(value, dict):
            city = value.get("city") or value.get("il") or value.get("sehir") or value.get("şehir")
            district = value.get("district") or value.get("ilce") or value.get("ilçe")
            parts = [str(part).strip() for part in (city, district) if part]
            if parts:
                return ", ".join(parts)
            joined = ", ".join(
                str(v).strip() for v in value.values() if isinstance(v, (str, int, float)) and str(v).strip()
            )
            return joined or None
        return str(value)


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

KNOWN_LOCATIONS = {
    "adana", "adiyaman", "afyonkarahisar", "agri", "aksaray", "amasya",
    "ankara", "antalya", "ardahan", "artvin", "aydin", "balikesir",
    "bartin", "batman", "bayburt", "bilecik", "bingol", "bitlis", "bolu",
    "burdur", "bursa", "canakkale", "cankiri", "corum", "denizli",
    "diyarbakir", "duzce", "edirne", "elazig", "erzincan", "erzurum",
    "eskisehir", "gaziantep", "giresun", "gumushane", "hakkari", "hatay",
    "igdir", "isparta", "istanbul", "izmir", "kahramanmaras", "karabuk",
    "karaman", "kars", "kastamonu", "kayseri", "kilis", "kirikkale",
    "kirklareli", "kirsehir", "kocaeli", "konya", "kutahya", "malatya",
    "manisa", "mardin", "mersin", "mugla", "mus", "nevsehir", "nigde",
    "ordu", "osmaniye", "rize", "sakarya", "samsun", "siirt", "sinop",
    "sivas", "sanliurfa", "sirnak", "tekirdag", "tokat", "trabzon",
    "tunceli", "usak", "van", "yalova", "yozgat", "zonguldak",
    "avcilar", "basaksehir", "beylikduzu", "cankaya", "pendik", "sincan",
}

BLOCKED_ENTITY_TERMS = {
    "jobsavior", "kariyer", "eleman net", "takvim", "haritayer", "nato",
    "ticaret odasi", "sanayi odasi", "belediye", "bakanligi", "universite",
    "cumhurbaskanligi", "baskanligi", "dernegi", "ihracatcilari birligi",
    "organize sanayi bolgesi", "osb", "is ilanlari", "is arama platformu",
}

BLOCKED_SOURCE_DOMAINS = {
    "jobsavior.com", "kariyer.net", "eleman.net", "takvim.com.tr",
    "haritayer.com", "wikipedia.org", "linkedin.com", "indeed.com",
}

QUERY_STOP_WORDS = {
    "firma", "firmalari", "firmasi", "sirket", "sirketleri", "ureticileri",
    "ureticisi", "hizmet", "sektor", "sektoru", "sanayi", "servisleri",
    "servisi", "ve", "ile", "icin",
}


def _normalize_text(value: str | None) -> str:
    if not value:
        return ""
    folded = value.casefold().replace("ı", "i")
    return "".join(
        character
        for character in unicodedata.normalize("NFKD", folded)
        if not unicodedata.combining(character)
    )


def _extract_requested_location(search_query: str | None) -> str | None:
    query_tokens = set(re.findall(r"[a-z0-9]+", _normalize_text(search_query)))
    return next((location for location in KNOWN_LOCATIONS if location in query_tokens), None)


def _extract_sector_keywords(search_query: str | None) -> set[str]:
    normalized_query = _normalize_text(search_query)
    location = _extract_requested_location(search_query)
    return {
        token
        for token in re.findall(r"[a-z0-9]+", normalized_query)
        if len(token) >= 3 and token != location and token not in QUERY_STOP_WORDS
    }


def is_relevant_company(
    company: dict[str, Any],
    search_query: str | None,
    source_url: str | None,
) -> bool:
    """LLM sonucunu şehir, sektör ve firma türü kurallarıyla doğrular."""
    normalized_name = _normalize_text(company.get("name"))
    normalized_description = _normalize_text(company.get("description"))
    normalized_location = _normalize_text(company.get("location"))
    normalized_source = _normalize_text(source_url)
    entity_text = f"{normalized_name} {normalized_description}"

    if any(term in entity_text for term in BLOCKED_ENTITY_TERMS):
        return False
    if any(domain in normalized_source for domain in BLOCKED_SOURCE_DOMAINS):
        return False

    requested_location = _extract_requested_location(search_query)
    if requested_location and requested_location not in normalized_location:
        return False

    sector_keywords = _extract_sector_keywords(search_query)
    if sector_keywords and not any(keyword in entity_text for keyword in sector_keywords):
        return False

    return bool(normalized_name)


class AnalizMotoru:
    def __init__(self) -> None:
        groq_api_key: str | None = os.getenv("GROQ_API_KEY")
        if AsyncGroq and groq_api_key:
            self.client = AsyncGroq(api_key=groq_api_key)
        else:
            self.client = None

        # KOTA DÜZELTMESİ: llama-3.3-70b-versatile'ın günlük token kotası demo sırasında doldu
        # (Groq TPD limiti ayrı model bazında tutuluyor). 8b-instant hem ayrı bir kotaya sahip
        # hem de çok daha az token tüketiyor, bu yüzden varsayılan model olarak seçildi.
        self.model: str = "llama-3.1-8b-instant"
        self.max_retries: int = 3
        self.retry_base_delay_seconds: float = 3.0
        self.api_url: str = os.getenv("COMPANY_API_URL", "http://127.0.0.1:8000/api/v1/companies")
        self.api_key: str | None = os.getenv("COMPANY_API_KEY")

        # TEMİZ KOD: Süslü parantez çakışmalarını engellemek için {ham_metin} yerine [HAM_METIN] kullanılmıştır.
        self.prompt_template: str = (
            "Web sitesinin ham metnini analiz et. Bu metinden şirketleri ve varsa bu şirketlerin yetkililerini, kurucularını veya emlak danışmanlarını bul. "
            "Her şirket için şu alanları içeren bir JSON array döndür:\n"
            "name, website, location (yalnızca şehir/ilçe adı, düz metin olarak - asla obje/dict verme), "
            "address (bulunabiliyorsa açık adres, düz metin), phone (bulunabiliyorsa telefon), "
            "email (bulunabiliyorsa e-posta), description, source, confidence_score (0-100 arası) "
            "ve şirket yetkilileri için bir 'officials' listesi (içinde full_name và title olan objeler).\n\n"
            "UYARI: location alanını asla obje/dict olarak döndürme, sadece düz metin (string) olarak ver.\n"
            "UYARI: Eğer metinde yetkili adı geçmiyorsa, 'officials' listesini boş bırakma! "
            "FastAPI doğrulaması için listeye otomatik olarak şu objeyi ekle: {\"full_name\": \"Belirtilmemiş\", \"title\": \"Bilinmeyen Unvan\"}.\n\n"
            "Sonucu tek bir JSON NESNESİ (object) olarak, şu formatta döndür: "
            "{\"companies\": [ ... ]} — companies değeri yukarıdaki şirket objelerinin dizisi olsun. "
            "Başka hiçbir açıklama, madde işareti veya ek metin ekleme, sadece bu JSON nesnesini döndür. Metin:\n[HAM_METIN]"
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
        # KOTA DÜZELTMESİ: 15000 karakter LLM'e gereksiz yere fazla token harcatıyordu,
        # günlük kotayı hızla tüketiyordu. 4000 karakter analiz kalitesini büyük ölçüde korur.
        return re.sub(r"\s{2,}", " ", text).strip()[:4000]

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

    @staticmethod
    def _retry_after_seconds(error: "RateLimitError") -> float | None:
        """Groq'un döndürdüğü retry-after header'ını okumaya çalışır (yoksa None döner)."""
        try:
            value = error.response.headers.get("retry-after")
            return float(value) if value is not None else None
        except Exception:
            return None

    async def _create_chat_completion_with_retry(self, full_prompt: str):
        """
        Groq'a istek atar; 429 (rate limit) alınırsa kısa aralıklarla birkaç kez tekrar dener.
        Bu, dakikalık limit dalgalanmaları gibi geçici durumlarda veri kaybını azaltır.
        Günlük (TPD) kota tamamen tükenmişse retry'lar da başarısız olur ve fallback'e düşülür.
        """
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                return await self.client.chat.completions.create(
                    messages=[
                        {"role": "system",
                         "content": "Sen bir OSINT veri analiz uzmanısın. Çıktı olarak sadece geçerli bir JSON array ver."},
                        {"role": "user", "content": full_prompt}
                    ],
                    model=self.model,
                    response_format={"type": "json_object"}
                )
            except RateLimitError as error:
                last_error = error
                if attempt >= self.max_retries:
                    break
                wait_seconds = self._retry_after_seconds(error) or (self.retry_base_delay_seconds * attempt)
                wait_seconds = min(wait_seconds, 15.0)
                logger.warning(
                    "Groq rate limit alındı (deneme %s/%s), %.1f sn sonra tekrar denenecek.",
                    attempt, self.max_retries, wait_seconds,
                )
                await asyncio.sleep(wait_seconds)
        raise last_error

    async def analiz_et(
        self,
        ham_metin: str,
        search_history_id: int | None = None,
        source_url: str | None = None,
        search_query: str | None = None,
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
            full_prompt = (
                self.prompt_template.replace("[HAM_METIN]", cleaned_text)
                + f"\n\nKullanıcı arama sorgusu: {search_query or 'Belirtilmedi'}"
                + "\nYalnızca sorgudaki şehir ve faaliyet alanıyla doğrudan eşleşen gerçek şirketleri döndür."
                + " İş ilanı ve haber sitelerini, kamu kurumlarını, odaları, dernekleri,"
                + " üniversiteleri ve organize sanayi bölgesinin kendisini şirket olarak döndürme."
            )

            response = await self._create_chat_completion_with_retry(full_prompt)

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
                # SAĞLAMLIK DÜZELTMESİ: küçük model (8b-instant) bazen birden fazla şirketi
                # tek bir öğede iç içe liste olarak döndürüyor (örn. [[{...},{...}]]). Bu veriyi
                # kaybetmemek için tek seviye düzleştiriyoruz.
                flattened_data: list[Any] = []
                for entry in data:
                    if isinstance(entry, list):
                        flattened_data.extend(entry)
                    else:
                        flattened_data.append(entry)
                data = flattened_data

                for item in data:
                    if not isinstance(item, dict):
                        logger.warning("Düzleştirme sonrası hâlâ beklenmeyen öğe formatı atlandı: %r", item)
                        continue
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
                        validated_item = valid_data.model_dump()
                        if is_relevant_company(validated_item, search_query, source_url):
                            results.append(validated_item)
                        else:
                            logger.info(
                                "Sonuç kalite filtresinde elendi: %s (sorgu=%s)",
                                validated_item.get("name"),
                                search_query,
                            )
                    except Exception as val_err:
                        logger.warning(f"Format hatası nedeniyle öğe atlandı: {val_err}")
                        continue

            if results and self.api_url:
                await self._post_companies_to_api_async(
                    results,
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
                    "industry": c.get("description"),
                    "city": c.get("location"),
                    "address": c.get("address"),
                    "website": c.get("website"),
                    "phone": c.get("phone"),
                    "email": c.get("email"),
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
