"""Redis listener / LLM Worker (Dev 3)

This listener consumes raw HTML/text items from Redis (queue: osint_raw_queue),
cleans the text, calls Gemini via google-generativeai, and posts high-confidence
company records to the Core API.
"""

import json
import logging
import os
import re
import time
from typing import Optional, Tuple

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover - optional dependency
    genai = None

try:
    import redis
except Exception:  # pragma: no cover - optional dependency
    redis = None


load_dotenv()
# Load app-specific env values from the core-api .env file if present
core_api_env = os.path.join(os.path.dirname(__file__), "autonomous-osint-agent", "core-api", ".env")
if os.path.exists(core_api_env):
    load_dotenv(dotenv_path=core_api_env, override=False)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("redis_listener")


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
QUEUE_NAME = os.getenv("OSINT_REDIS_QUEUE", "osint_raw_queue")
COMPANY_API_URL = os.getenv("COMPANY_API_URL", "http://127.0.0.1:8000/api/v1/companies")
COMPANY_API_KEY = os.getenv("COMPANY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")


def clean_text(raw: str) -> str:
    """Clean HTML or plain text to minimize token count and noise.

    - Strip HTML tags via BeautifulSoup
    - Normalize whitespace, remove newlines/tabs, compress multiple spaces
    """
    if not raw:
        return ""

    # If it looks like HTML, parse and extract visible text
    try:
        soup = BeautifulSoup(raw, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = " ".join(soup.stripped_strings)
    except Exception:
        text = raw

    # Normalize whitespace
    text = text.replace("\t", " ").replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()

    # Aggressively trim long text to a safe length to reduce token usage
    MAX_CHARS = 15000
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS]

    return text


def extract_json_from_model(text: str) -> Optional[dict]:
    """Attempt to extract a JSON object from model text response."""
    if not text:
        return None

    # Remove markdown code fences
    if text.startswith("```"):
        # drop leading triple backticks block markers
        parts = text.split("\n", 1)
        if len(parts) > 1:
            text = parts[1].rsplit("```", 1)[0]

    # Find first JSON object
    m = re.search(r"(\{.*\})", text, flags=re.DOTALL)
    if not m:
        logger.debug("Model response contains no JSON object: %s", text[:200])
        return None

    json_text = m.group(1)
    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        logger.exception("Failed to parse JSON from model output")
        return None


def configure_gemini() -> Optional[object]:
    if genai is None:
        logger.warning("google-generativeai paketine ulaşılamıyor; Gemini çağrıları yapılamayacak")
        return None
    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY çevresel değişkeni ayarlı değil; Gemini çağrıları yapılamayacak")
        return None

    try:
        genai.configure(api_key=GEMINI_API_KEY)

        preferred = [
            "models/gemini-flash-lite-latest",
            "models/gemini-3.1-flash-lite",
            "models/gemini-3.5-flash",
            "models/gemini-2.0-flash-lite",
            "models/gemini-2.0-flash",
            "models/gemini-2.5-flash",
        ]

        # Attempt to list available models and pick the first that supports generateContent
        chosen_name = None
        fallback_name = None
        available_generate_models = set()
        try:
            models = None
            if hasattr(genai, "list_models"):
                models = genai.list_models()
            elif hasattr(genai, "get_models"):
                models = genai.get_models()

            if models:
                # models may be a list of dicts or objects
                for m in models:
                    # normalize accessors
                    name = None
                    methods = None
                    try:
                        if isinstance(m, dict):
                            name = m.get("name")
                            methods = m.get("supported_generation_methods") or m.get("supportedMethods")
                        else:
                            name = getattr(m, "name", None)
                            methods = getattr(m, "supported_generation_methods", None) or getattr(m, "supportedMethods", None)
                    except Exception:
                        continue

                    if not name:
                        continue

                    # some providers embed methods as list of strings
                    if methods and isinstance(methods, (list, tuple)):
                        if any("generateContent" in str(x) for x in methods):
                            available_generate_models.add(name)
                            if fallback_name is None:
                                fallback_name = name

            if available_generate_models:
                for candidate in preferred:
                    if candidate in available_generate_models:
                        chosen_name = candidate
                        break

        except Exception:
            logger.debug("Model listeleme sırasında hata; fallback kullanılacak", exc_info=True)

        if not chosen_name and fallback_name:
            chosen_name = fallback_name

        # Preferred fallbacks if list_models didn't yield a candidate
        fallback_candidates = preferred + ["gemini-2.5-flash", "gemini-pro"]
        if not chosen_name:
            for candidate in fallback_candidates:
                try:
                    # quick check by attempting to construct model object
                    _ = genai.GenerativeModel(candidate)
                    chosen_name = candidate
                    break
                except Exception:
                    continue

        if not chosen_name:
            logger.error("Uygun bir Gemini modeli bulunamadı; model oluşturulamıyor")
            return None

        model = genai.GenerativeModel(chosen_name)
        logger.info("Gemini model yapılandırıldı: %s", chosen_name)
        return model
    except Exception:
        logger.exception("Gemini yapılandırılırken hata oluştu")
        return None


def post_company_to_api(payload: dict) -> Tuple[bool, int]:
    headers = {"Content-Type": "application/json"}
    if COMPANY_API_KEY:
        headers["Authorization"] = f"Bearer {COMPANY_API_KEY}"
    try:
        logger.info("[Listener] POST URL=%s", COMPANY_API_URL)
        logger.info("[Listener] POST payload=%s", payload)
        logger.info("[Listener] POST request sending")
        resp = requests.post(COMPANY_API_URL, json=payload, headers=headers, timeout=15)
        logger.info("[Listener] POST status=%s", resp.status_code)
        logger.info("[Listener] Response body=%s", resp.text)
        return (resp.ok, resp.status_code)
    except requests.RequestException:
        logger.exception("Core API'ye POST isteği başarısız oldu")
        logger.info("[Listener] Retry=False")
        logger.info("[Listener] Discard=True")
        return (False, 0)


def extract_input_text(raw_message: str) -> Tuple[str, str | None, str | None, int | None]:
    """Normalize incoming queue payload to the text sent to the LLM.

    Expected canonical payload is a JSON object with ham_metin.
    Fallback to raw message keeps backward compatibility for plain-text producers.
    """
    try:
        parsed_payload = json.loads(raw_message)
        logger.info("[Listener] JSON parse başarılı")
    except json.JSONDecodeError:
        logger.warning("[Listener] JSON parse başarısız; plain text fallback uygulanıyor")
        return clean_text(raw_message), None, None, None

    if not isinstance(parsed_payload, dict):
        logger.warning("JSON payload object değil; ham mesaj fallback ile işlenecek")
        return clean_text(raw_message), None, None, None

    source = parsed_payload.get("kaynak")
    target_url = parsed_payload.get("hedef_url")
    raw_text = parsed_payload.get("ham_metin")
    raw_search_history_id = parsed_payload.get("search_history_id")

    search_history_id = None
    if raw_search_history_id is not None:
        try:
            candidate = int(raw_search_history_id)
            if candidate > 0:
                search_history_id = candidate
                logger.info("[Listener] search_history_id=%s", search_history_id)
        except (TypeError, ValueError):
            logger.warning("search_history_id geçersiz; ilişki kaydı atlanacak")
            logger.warning("[Listener] search_history_id parse hatası")

    if search_history_id is None:
        logger.info("[Listener] search_history_id=None")

    if raw_text is None or not str(raw_text).strip():
        logger.warning(
            "JSON payload içinde ham_metin yok veya boş; mesaj atlandı (veri kaybı riski loglandı). kaynak=%s hedef_url=%s payload_keys=%s",
            source,
            target_url,
            sorted(parsed_payload.keys()),
        )
        return "", source, target_url, search_history_id

    return clean_text(str(raw_text)), source, target_url, search_history_id


def process_message(model, redis_client, queue_name: str, raw_message: str) -> None:
    """Main processing: clean, call Gemini, evaluate score and post if high-quality."""
    logger.info("[Listener] Queue received")
    logger.info("[Listener] Payload=%s", raw_message)
    cleaned, source, target_url, search_history_id = extract_input_text(raw_message)
    if not cleaned:
        logger.warning("Boş ya da temizlenemeyen metin atlandı")
        logger.info("[Listener] Discard=True")
        logger.info("[Listener] Finished")
        return

    if source or target_url:
        logger.debug("İşlenen payload metadata: kaynak=%s hedef_url=%s", source, target_url)

    system_instruction = (
        "SEN BIR OSINT SIRKET ESLESTIRME MOTORUSUN. "
        "Gorevin, scraper'dan gelen sirket adaylarini kullanici sorgusuna gore filtrelemektir. "
        "Yanlis pozitif uretmek en buyuk hatadir. Emin degilsen sirketi dondurme. "
        "\n\n"
        "KURALLAR: "
        "1) Kullanici sorgusundaki sehir, sektor, faaliyet alani ve anahtar kelimelerle yuksek derecede uyum ara. "
        "Aday sirket bu sinyallerin tamamina guclu sekilde uymuyorsa reddet. "
        "2) Sirket adinda anahtar kelimenin gecmesi tek basina yeterli degildir. "
        "Karari faaliyet alanina gore ver. "
        "Ornek: Cengaver Lojistik Petrol Otomotiv Insaat Tekstil adinda gecse bile faaliyet lojistikse REDDET. "
        "3) Sehir belirtilmisse yalnizca o sehirde faaliyet gosteren sirketleri kabul et, diger sehirleri reddet. "
        "4) Su kurumlari ASLA sirket kabul etme: Ticaret Odasi, Belediye, Universite, Bakanlik, Vakif, Dernek, kamu kurumu, meslek odasi, federasyon. "
        "5) Anahtar kelime benzerligi tek basina yeterli degildir. "
        "Ornek Ankara Hali sorgusunda hali ureticisi/magazasi/fabrikasi/toptancisi/zemin kaplama kabul; hali saha/spor tesisi/futbol kulubu reddet. "
        "Ornek Denizli tekstil sorgusunda tekstil/konfeksiyon/kumas uretimi/hazir giyim/dokuma/iplik uretimi kabul; lojistik/sigorta/yazilim/web tasarim/reklam/medya/restoran/market/otel reddet. "
        "6) Sirket sektoru veya faaliyet alani net degilse REDDET. Tahmin yapma. "
        "7) Confidence kurallari: 100 = sehir + sektor + faaliyet alani tamamen uyuyor; 95 = cok guclu eslesme; 90 = uyuyor ama kucuk belirsizlik var; 85 = zayif ama hala kabul edilebilir iliski. 80 ve altini uretme. "
        "8) Sorguyla ilgisi olmayan hicbir sirketi dondurme. 5 dogru sonuc, 20 yanlis sonuctan daha degerlidir. "
        "\n\n"
        "JSON disinda hicbir sey yazma. "
        "Her sirket icin yalnizca su alanlari dondur: name, industry, city, confidence. "
        "Uygun aday yoksa yalnizca bos JSON dondur: {}"
    )

    # Build prompt
    prompt = f"System: {system_instruction}\n\nInput:\n{cleaned}"

    if model is None:
        logger.error("Gemini modeli yapılandırılmamış; mesaj kuyruğa geri konuyor")
        try:
            logger.info("[Listener] Retry=True")
            logger.info("[Listener] Retry reason=model_not_configured")
            redis_client.lpush(queue_name, raw_message)
        except Exception:
            logger.exception("Mesaj kuyruğa tekrar eklenirken hata oluştu")
        time.sleep(2)
        logger.info("[Listener] Finished")
        return

    try:
        # Use model.generate_content similar to other modules if available
        logger.info("[Listener] Gemini request")
        response = model.generate_content(prompt)
        model_text = getattr(response, "text", str(response))
        logger.info("[Listener] Gemini response alındı")
        logger.info("[Listener] Gemini response=%s", model_text)
        logger.debug("Gemini yanıtı: %s", model_text[:400])

    except Exception as exc:
        # Handle rate-limit (429) and other transient issues
        msg = str(exc)
        logger.error("[Listener] Gemini exception type=%s message=%s", type(exc).__name__, msg)
        if "429" in msg or "Too Many Requests" in msg:
            logger.warning("Gemini 429 alındı; mesaj kuyruğa geri konuyor ve 10s uyku uygulanıyor")
            try:
                logger.info("[Listener] Retry=True")
                logger.info("[Listener] Retry reason=gemini_429")
                redis_client.lpush(queue_name, raw_message)
            except Exception:
                logger.exception("Mesaj kuyruğa tekrar eklenirken hata oluştu")
            time.sleep(10)
            logger.info("[Listener] Finished")
            return
        logger.exception("Gemini çağrısı sırasında hata oluştu")
        # requeue to avoid data loss
        try:
            logger.info("[Listener] Retry=True")
            logger.info("[Listener] Retry reason=gemini_exception")
            redis_client.lpush(queue_name, raw_message)
        except Exception:
            logger.exception("Mesaj kuyruğa tekrar eklenirken hata oluştu")
        time.sleep(2)
        logger.info("[Listener] Finished")
        return

    parsed = extract_json_from_model(model_text)
    if not parsed:
        logger.info("Modelden geçerli JSON gelmedi; veri elendi ve loglandı")
        logger.info("[Listener] Discard=True")
        logger.info("[Listener] Finished")
        return

    logger.info("[Listener] LLM company object=%s", parsed)

    # Validate expected keys
    name = parsed.get("name")
    city = parsed.get("city")
    industry = parsed.get("industry")
    confidence = parsed.get("confidence_score")

    logger.info("[Listener] Company name=%s", name)

    try:
        confidence = int(confidence)
    except Exception:
        logger.warning("confidence_score numeric değil veya yok; veri elendi")
        logger.info("[Listener] Confidence=%s", confidence)
        logger.info("[Listener] Confidence passed=False")
        logger.info("[Listener] Discard=True")
        logger.info("[Listener] Finished")
        return

    logger.info("[Listener] Confidence=%s", confidence)

    if confidence >= 85:
        logger.info("[Listener] Confidence passed=True")
        payload = {"name": name, "city": city, "industry": industry, "confidence_score": confidence, "officials": []}
        if search_history_id is not None:
            payload["search_history_id"] = search_history_id
        ok, status = post_company_to_api(payload)
        if ok:
            logger.info("Elit veri API'ye gönderildi (status=%s): %s", status, name)
            logger.info("[Listener] POST başarılı")
        else:
            # If API rate limited, attempt to requeue and delay
            if status == 429:
                logger.warning("Core API 429 döndü; mesaj kuyruğa geri konuyor ve 10s uyku uygulanıyor")
                try:
                    logger.info("[Listener] Retry=True")
                    logger.info("[Listener] Retry reason=api_429")
                    redis_client.lpush(queue_name, raw_message)
                except Exception:
                    logger.exception("Mesaj kuyruğa tekrar eklenirken hata oluştu")
                time.sleep(10)
                logger.info("[Listener] Finished")
                return
            logger.error("API'ye gönderilemedi, status=%s; veri loglandı ve atlandı", status)
            logger.info("[Listener] Retry=False")
            logger.info("[Listener] Discard=True")
    else:
        logger.info("Düşük puanlı veri elendi (confidence=%s): %s", confidence, name)
        logger.info("[Listener] Confidence passed=False")
        logger.info("[Listener] Discard=True")

    # Throttle to avoid hitting Gemini rate limits
    time.sleep(2)
    logger.info("[Listener] İşlem başarıyla tamamlandı")
    logger.info("[Listener] Finished")


def main():
    if redis is None:
        logger.error("redis kütüphanesi bulunamadı; lütfen 'redis' paketini yükleyin")
        return

    # Connect Redis
    try:
        client = redis.from_url(
            REDIS_URL,
            decode_responses=True,
            socket_timeout=15,
            retry_on_timeout=True,
        )
        client.ping()
        logger.info("Bağlanılan Redis: %s | Kuyruk: %s", REDIS_URL, QUEUE_NAME)
    except Exception:
        logger.exception("Redis'e bağlantı kurulamadı")
        return

    model = configure_gemini()

    logger.info("Dinleyici başlatılıyor; kuyruğu dinleniyor: %s", QUEUE_NAME)
    while True:
        try:
            # brpop ile blocking bekleme (5s timeout kullanarak periyodik yeniden denetim)
            item = client.brpop(QUEUE_NAME, timeout=5)
            if not item:
                continue

            _, raw_message = item
            logger.info("[Listener] Queue'dan mesaj alındı")
            if not raw_message or not raw_message.strip():
                logger.warning("Kuyruktan boş mesaj geldi, atlanıyor")
                continue

            try:
                process_message(model, client, QUEUE_NAME, raw_message)
            except Exception:
                logger.exception("Mesaj işlenirken beklenmeyen hata; mesaj kuyruğa geri konuyor")
                try:
                    logger.info("[Listener] Retry=True")
                    logger.info("[Listener] Retry reason=unexpected_process_error")
                    client.lpush(QUEUE_NAME, raw_message)
                except Exception:
                    logger.exception("Beklenmeyen hata sonrası mesaj kuyruğa geri eklenemedi")
                time.sleep(2)
                logger.info("[Listener] Finished")

        except KeyboardInterrupt:
            logger.info("Dinleyici kesildi (KeyboardInterrupt)")
            break
        except Exception:
            logger.exception("Kuyruk dinleme döngüsünde beklenmeyen hata")
            time.sleep(2)


if __name__ == "__main__":
    main()
