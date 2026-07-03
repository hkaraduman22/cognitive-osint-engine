import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Dict, Any
from core.interfaces import IUrlFetcher

class GenericUrlFetcher(IUrlFetcher):
    """Konfigürasyon tabanlı, dinamik HTTP metotlarını destekleyen evrensel toplayıcı sınıf."""

    def __init__(self, source_id: str, config: Dict[str, Any]):
        self._source_id = source_id
        self._config = config
        self._session = requests.Session()
        self._headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:152.0) Gecko/20100101 Firefox/152.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }

    @property
    def source_id(self) -> str:
        return self._source_id

    def _initialize_session(self) -> None:
        """Oturum çerezlerini doğrulamak için gerekliyse ön ziyaret gerçekleştirir."""
        init_url = self._config.get("init_url")
        if init_url:
            try:
                self._session.get(init_url, headers=self._headers, timeout=10)
                self._headers['Referer'] = init_url
            except requests.exceptions.RequestException:
                pass

    def fetch(self, query: str) -> List[str]:
        self._initialize_session()
        method = self._config.get("method", "GET").upper()
        base_url = self._config.get("base_url", "")

        try:
            if method == "GET":
                target_url = base_url.replace("{query}", query)
                response = self._session.get(target_url, headers=self._headers, timeout=10)
            elif method == "POST":
                param_name = self._config.get("search_param", "q")
                payload = {param_name: query}
                if "extra_payload" in self._config:
                    payload.update(self._config["extra_payload"])
                response = self._session.post(base_url, headers=self._headers, data=payload, timeout=10)
            else:
                return []

            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            domain = "/".join(response.url.split('/')[:3]) + "/"
            urls = []

            # Akıllı Link Seçici (Smart Link Selector)
            css_selector = self._config.get("link_selector")
            link_elements = soup.select(css_selector) if css_selector else soup.find_all('a', href=True)

            for link in link_elements:
                href = link.get('href')
                if not href or href in ['#', '/', 'javascript:void(0);'] or href.startswith('mailto:'):
                    continue

                if href.startswith('http'):
                    full_url = href
                elif href.startswith('www.'):
                    full_url = "https://" + href
                else:
                    full_url = urljoin(domain, href)

                if len(full_url) > 10:
                    urls.append(full_url)

            return list(set(urls))[:3]

        except Exception as e:
            print(f"[-] {self._source_id} bağlantı hatası: {e}")
            return []