import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
from typing import List
from core.interfaces import IUrlFetcher


class FreeGlobalUrlFetcher(IUrlFetcher):
    """DuckDuckGo HTML versiyonunu POST metodu ile kazıyarak çalışan ücretsiz global toplayıcı."""

    @property
    def source_id(self) -> str:
        return "global_ddg"

    def fetch(self, query: str) -> List[str]:
        target_url = "https://html.duckduckgo.com/html/"

        # GET yerine POST yapıyoruz. DDG bunu gerçek bir form gönderimi sanıyor.
        payload = {'q': f'{query} iletişim'}

        # Mükemmel bir insan taklidi (Headers)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:152.0) Gecko/20100101 Firefox/152.0',
            'Origin': 'https://html.duckduckgo.com',
            'Referer': 'https://html.duckduckgo.com/',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        urls = []
        try:
            res = requests.post(target_url, headers=headers, data=payload, timeout=10)

            if res.status_code != 200:
                return []

            soup = BeautifulSoup(res.content, 'html.parser')

            for a in soup.find_all('a', class_='result__url'):
                href = a.get('href', '')
                if 'uddg=' in href:
                    # DDG'nin güvenlik yönlendirmesini temizleyip gerçek URL'yi alıyoruz
                    actual_url = unquote(href.split('uddg=')[1].split('&')[0])
                    urls.append(actual_url)

            return urls[:3]
        except Exception as e:
            print(f"[-] Global API Hatası: {e}")
            return []