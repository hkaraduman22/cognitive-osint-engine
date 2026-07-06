"""Redis listener / LLM Worker (Dev 3)

This listener consumes raw HTML/text items from Redis (queue: osint:raw_text),
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
QUEUE_NAME = os.getenv("OSINT_REDIS_QUEUE", "osint:raw_text")
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

        # Attempt to list available models and pick the first that supports generateContent
        chosen_name = None
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
                            chosen_name = name
                            break

        except Exception:
            logger.debug("Model listeleme sırasında hata; fallback kullanılacak", exc_info=True)

        # Preferred fallbacks if list_models didn't yield a candidate
        preferred = ["gemini-1.5-flash", "gemini-pro", "gemini-1.5", "gemini-1.0"]
        if not chosen_name:
            for candidate in preferred:
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
        resp = requests.post(COMPANY_API_URL, json=payload, headers=headers, timeout=15)
        return (resp.ok, resp.status_code)
    except requests.RequestException:
        logger.exception("Core API'ye POST isteği başarısız oldu")
        return (False, 0)


def process_message(model, redis_client, queue_name: str, raw_message: str) -> None:
    """Main processing: clean, call Gemini, evaluate score and post if high-quality."""
    cleaned = clean_text(raw_message)
    if not cleaned:
        logger.warning("Boş ya da temizlenemeyen metin atlandı")
        return

    system_instruction = (
        "Sana internetten kazınmış ham bir metin vereceğim. Bu metni analiz et. "
        "Eğer içeride bir firmanın adı, şehri ve faaliyet gösterdiği sektör net olarak geçiyorsa bunları ayıkla. "
        "Bulduğun verilerin doğruluğuna ve netliğine 0 ile 100 arasında bir confidence_score ver. "
        'Çıktıyı kesinlikle ve sadece şu JSON formatında dön: {"name": "...", "city": "...", "industry": "...", "confidence_score": 90}'
    )

    # Build prompt
    prompt = f"System: {system_instruction}\n\nInput:\n{cleaned}"

    if model is None:
        logger.error("Gemini modeli yapılandırılmamış; mesaj atlanıyor")
        return

    try:
        # Use model.generate_content similar to other modules if available
        response = model.generate_content(prompt)
        model_text = getattr(response, "text", str(response))
        logger.debug("Gemini yanıtı: %s", model_text[:400])

    except Exception as exc:
        # Handle rate-limit (429) and other transient issues
        msg = str(exc)
        if "429" in msg or "Too Many Requests" in msg:
            logger.warning("Gemini 429 alındı; mesaj kuyruğa geri konuyor ve 10s uyku uygulanıyor")
            try:
                redis_client.lpush(queue_name, raw_message)
            except Exception:
                logger.exception("Mesaj kuyruğa tekrar eklenirken hata oluştu")
            time.sleep(10)
            return
        logger.exception("Gemini çağrısı sırasında hata oluştu")
        # requeue to avoid data loss
        try:
            redis_client.lpush(queue_name, raw_message)
        except Exception:
            logger.exception("Mesaj kuyruğa tekrar eklenirken hata oluştu")
        time.sleep(2)
        return

    parsed = extract_json_from_model(model_text)
    if not parsed:
        logger.info("Modelden geçerli JSON gelmedi; veri elendi ve loglandı")
        return

    # Validate expected keys
    name = parsed.get("name")
    city = parsed.get("city")
    industry = parsed.get("industry")
    confidence = parsed.get("confidence_score")

    try:
        confidence = int(confidence)
    except Exception:
        logger.warning("confidence_score numeric değil veya yok; veri elendi")
        return

    if confidence >= 85:
        payload = {"name": name, "city": city, "industry": industry, "confidence_score": confidence, "officials": []}
        ok, status = post_company_to_api(payload)
        if ok:
            logger.info("Elit veri API'ye gönderildi (status=%s): %s", status, name)
        else:
            # If API rate limited, attempt to requeue and delay
            if status == 429:
                logger.warning("Core API 429 döndü; mesaj kuyruğa geri konuyor ve 10s uyku uygulanıyor")
                try:
                    redis_client.lpush(queue_name, raw_message)
                except Exception:
                    logger.exception("Mesaj kuyruğa tekrar eklenirken hata oluştu")
                time.sleep(10)
                return
            logger.error("API'ye gönderilemedi, status=%s; veri loglandı ve atlandı", status)
    else:
        logger.info("Düşük puanlı veri elendi (confidence=%s): %s", confidence, name)

    # Throttle to avoid hitting Gemini rate limits
    time.sleep(2)


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
            if not raw_message or not raw_message.strip():
                logger.warning("Kuyruktan boş mesaj geldi, atlanıyor")
                continue

            process_message(model, client, QUEUE_NAME, raw_message)

        except KeyboardInterrupt:
            logger.info("Dinleyici kesildi (KeyboardInterrupt)")
            break
        except Exception:
            logger.exception("Kuyruk dinleme döngüsünde beklenmeyen hata")
            time.sleep(2)


if __name__ == "__main__":
    main()
