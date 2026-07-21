import time
from typing import List
from ddgs import DDGS
from app.scraper.core.interfaces import IUrlFetcher

class KariyerUrlFetcher(IUrlFetcher):
    """DuckDuckGo DDGS kullanarak şirketin açık iş ilanlarını (Kariyer/LinkedIn) arayan toplayıcı."""

    def __init__(self, delay: float = 0.5):
        self._delay = delay

    @property
    def source_id(self) -> str:
        return "kariyer_is_ilani"

    def fetch(self, query: str) -> List[str]:
        if self._delay > 0:
            time.sleep(self._delay)
            
        search_query = f"{query} iş ilanı kariyer açık pozisyonlar".strip()
        urls = []

        try:
            with DDGS() as ddgs:
                results = ddgs.text(search_query, max_results=5)
                for res in results:
                    href = res.get("href", "")
                    if href.startswith('http'):
                        urls.append(href)

            # Sadece kariyer portallarına odaklan
            kariyer_siteleri = ['kariyer.net', 'linkedin.com/jobs', 'yenibiris.com', 'eleman.net']
            final_urls = [u for u in urls if any(k in u.lower() for k in kariyer_siteleri)]

            # Eğer kariyer siteleri bulunamazsa şirketlerin kendi sitelerini al
            if not final_urls:
                yasakli_siteler = ['wikipedia.org', 'instagram.com', 'facebook.com', 'twitter.com', 'youtube.com']
                final_urls = [u for u in urls if not any(y in u.lower() for y in yasakli_siteler)]

            return list(set(final_urls))[:2]
        except Exception as e:
            print(f"[-] Kariyer API Hatası: {e}")
            return []
