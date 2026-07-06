import time
from typing import List
from ddgs import DDGS
from core.interfaces import IUrlFetcher

class FreeGlobalUrlFetcher(IUrlFetcher):
    """Resmi ve güncel 'ddgs' kütüphanesini kullanan ücretsiz global toplayıcı.
       Query Expansion (Sorgu Genişletme) ve Jitter (Gecikme) özelliklerini destekler."""

    def __init__(self, suffix: str = "", delay: float = 0.0):
        self._suffix = suffix
        self._delay = delay
        self._base_id = "global_ddg"

    @property
    def source_id(self) -> str:
        # Botun adını suffix'e göre dinamik yapıyoruz
        if self._suffix:
            clean_suffix = self._suffix.strip().replace(" ", "_").lower()
            return f"{self._base_id}_{clean_suffix}"
        return self._base_id

    def fetch(self, query: str) -> List[str]:
        # Anti-Ban: Her thread'in aynı anda DDG'ye saldırmasını engellemek için Jitter
        if self._delay > 0:
            time.sleep(self._delay)

        urls = []
        # Sorguyu dinamik olarak genişlet (Örn: "Arçelik Denizli" + " Ticaret Odası")
        search_query = f"{query} {self._suffix} kurumsal iletişim".strip()

        try:
            with DDGS() as ddgs:
                results = ddgs.text(search_query, max_results=5)
                for res in results:
                    href = res.get("href", "")
                    if href.startswith('http'):
                        urls.append(href)

            yasakli_siteler = ['wikipedia.org', 'instagram.com', 'linkedin.com', 'facebook.com', 'twitter.com', 'youtube.com']
            final_urls = [u for u in urls if not any(yasakli in u.lower() for yasakli in yasakli_siteler)]

            return list(set(final_urls))[:3]

        except Exception as e:
            print(f"[-] {self.source_id} API Hatası: {e}")
            return []