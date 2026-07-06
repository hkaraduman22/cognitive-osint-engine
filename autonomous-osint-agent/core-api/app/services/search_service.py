import json
import logging
import os
from typing import Any

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.repositories.search_repository import SearchRepository

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self, db: Session):
        self.search_repository = SearchRepository(db)

    def enqueue_search(self, user_id: int, query: str):
        """
        Gelen arama isteğini veritabanına kaydeder.
        Not: Arka plan işini (run_scraper_background) doğrudan router/endpoint içinden 
        FastAPI BackgroundTasks ile tetiklemek asenkron mimari için en sağlıklısıdır.
        """
        self.search_repository.save_search_history(user_id=user_id, query=query)
        return {"message": "Arama alındı, asenkron işlem başlatıldı"}

    def list_records(self):
        return self.search_repository.list_records()

    def list_history(self, user_id: int):
        return self.search_repository.get_last_searches(user_id=user_id)


async def run_scraper_background(target_domain: str, keyword: str) -> list[dict]:
    """
    Asenkron HTTP GET ile hedef web sitesini çeker, temizler ve LLM'e göndererek
    personel bilgilerini JSON formatında ayıklar.
    """
    extracted_text = ""
    personnel_results: list[dict] = []

    logger.info("🚀 [BOT UYANDIRILDI] Hedef: %s, Anahtar Kelime: %s", target_domain, keyword)

    try:
        logger.info("⏳ RAM'de HTML kazıma işlemi başlatılıyor...")
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(target_domain)
            response.raise_for_status()
            html = response.text

        logger.info("HTML fetched from %s, bytes=%d", target_domain, len(html))

        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        extracted_text = "\n".join(soup.stripped_strings)
        logger.info("HTML metni başarıyla temizlendi. Karakter sayısı: %d", len(extracted_text))
    except httpx.HTTPError as exc:
        logger.exception("Hedef domain %s ile HTTP hatası oluştu", target_domain)
        print(f"HTTP error fetching {target_domain}: {exc}", flush=True)
        return []
    except Exception as exc:
        logger.exception("Hedef domain %s için temizleme sırasında hata", target_domain)
        print(f"Error cleaning HTML for {target_domain}: {exc}", flush=True)
        return []

    if not extracted_text:
        logger.info("Hedef domain %s için okunabilir metin bulunamadı.", target_domain)
        return []

    logger.info("🧠 LLM analizi yapılıyor (gpt-4o-mini)...")
    system_prompt = (
        "Sen uzman bir OSINT veri ayıklama ajanısın. Sana verilen web sitesi metnini analiz et. "
        "Bu metin içindeki şirket çalışanlarını, yöneticileri veya personeli bul. "
        "Her bir kişi için 'Ad Soyad' ve 'Ünvan' bilgilerini çıkar. "
        "Sadece JSON formatında, [{'name': '...', 'title': '...'}] şeklinde yanıt dön. "
        "Eğer kimseyi bulamazsan boş liste [] dön."
    )

    user_prompt = (
        f"Web sitesi metni:\n\n{extracted_text}\n\n"
        f"Aşağıdaki anahtar kelimeye bağlı olarak ilgili personeli bul: {keyword}\n"
        "Yanıtını yalnızca geçerli JSON olarak ver."
    )

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("❌ OPENAI_API_KEY çevresel değişkeni tanımlı değil. Lütfen .env dosyanızı kontrol edin.")
        return []

    llm_payload: dict[str, Any] = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": 500,
        "temperature": 0.0,
        "top_p": 1.0,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openai_api_key}",
                    "Content-Type": "application/json",
                },
                json=llm_payload,
            )
            response.raise_for_status()
            llm_response = response.json()
        llm_text = llm_response["choices"][0]["message"]["content"].strip()
        logger.info("Received LLM response (choices=%d)", len(llm_response.get("choices", [])))

        # Markdown code block cleanup
        if llm_text.startswith("```"):
            llm_text = llm_text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    except httpx.HTTPError as exc:
        logger.exception("LLM isteği sırasında hata oluştu")
        return []
    except Exception as exc:
        logger.exception("LLM işlemi sırasında beklenmeyen hata")
        return []

    try:
        personnel_results = json.loads(llm_text)
    except json.JSONDecodeError:
        logger.error("LLM yanıtı JSON'a parse edilemedi: %s", llm_text)
        personnel_results = []

    logger.info("🎉 LLM personel çıkarımı sonucu başarıyla terminale yazdırıldı:\n%s", json.dumps(personnel_results, indent=2, ensure_ascii=False))
    return personnel_results
