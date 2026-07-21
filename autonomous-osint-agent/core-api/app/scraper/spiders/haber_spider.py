import time
from typing import List
from ddgs import DDGS
from app.scraper.core.interfaces import IUrlFetcher

class HaberUrlFetcher(IUrlFetcher):
    """DuckDuckGo DDGS kullanarak şirketin yatırım ve haberlerini arayan toplayıcı."""

    def __init__(self, delay: float = 0.5):
        self._delay = delay

    @property
    def source_id(self) -> str:
        return "haber_yatirim"

    def fetch(self, query: str) -> List[str]:
        if self._delay > 0:
            time.sleep(self._delay)

        search_query = f"{query} yatırım haber yeni atama CEO müdür".strip()
        urls = []

        try:
            with DDGS() as ddgs:
                results = ddgs.text(search_query, max_results=5)
                for res in results:
                    href = res.get("href", "")
                    if href.startswith('http'):
                        urls.append(href)

            yasakli_siteler = ['wikipedia.org', 'instagram.com', 'facebook.com', 'twitter.com', 'youtube.com']
            final_urls = [u for u in urls if not any(yasakli in u.lower() for yasakli in yasakli_siteler)]

            return list(set(final_urls))[:3]
        except Exception as e:
            print(f"[-] Haber API Hatası: {e}")
            return []
