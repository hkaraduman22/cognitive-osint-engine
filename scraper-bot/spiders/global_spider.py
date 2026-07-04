from typing import List
from ddgs import DDGS
from core.interfaces import IUrlFetcher


class FreeGlobalUrlFetcher(IUrlFetcher):
    """Resmi ve güncel 'ddgs' kütüphanesini kullanan ücretsiz global toplayıcı."""

    @property
    def source_id(self) -> str:
        return "global_ddg"

    def fetch(self, query: str) -> List[str]:
        urls = []
        # Sadece kurumsal siteleri hedeflemek için sorguyu optimize ediyoruz
        search_query = f"{query} kurumsal iletişim"

        try:
            # DDGS kütüphanesi HTTP 202
            with DDGS() as ddgs:
                # max_results=5 ile en iyi 5 sonucu çekiyoruz
                results = ddgs.text(search_query, max_results=5)

                for res in results:
                    href = res.get("href", "")
                    if href.startswith('http'):
                        urls.append(href)

            # Wikipedia, LinkedIn gibi OSINT için işimize yaramayacak ağları eliyoruz
            yasakli_siteler = ['wikipedia.org', 'instagram.com', 'linkedin.com', 'facebook.com', 'twitter.com',
                               'youtube.com']
            final_urls = [u for u in urls if not any(yasakli in u.lower() for yasakli in yasakli_siteler)]

            # Sadece en iyi 3 benzersiz kurumsal siteyi döndür
            return list(set(final_urls))[:3]

        except Exception as e:
            print(f"[-] Global API Hatası: {e}")
            return []