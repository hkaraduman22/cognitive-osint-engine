import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Dict, Any, Optional
from core.interfaces import IUrlFetcher
from core.http_identity import build_headers, get_proxies

class GenericUrlFetcher(IUrlFetcher):
    """Konfigürasyon tabanlı, dinamik HTTP metotlarını destekleyen evrensel toplayıcı sınıf."""

    def __init__(self, source_id: str, config: Dict[str, Any]):
        self._source_id = source_id
        self._config = config
        self._session = requests.Session()

    @property
    def source_id(self) -> str:
        return self._source_id

    def _initialize_session(self) -> None:
        """Oturum çerezlerini doğrulamak için gerekliyse ön ziyaret gerçekleştirir."""
        init_url = self._config.get("init_url")
        if init_url:
            try:
                self._session.get(init_url, headers=build_headers(), proxies=get_proxies(), timeout=10)
            except requests.exceptions.RequestException:
                pass

    def _request_with_identity_retry(
        self, method: str, url: str, data: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        """
        İsteği atar; 403 (bot engeli) alınırsa farklı bir UA/dil/referer/proxy
        kimliğiyle YALNIZCA BİR KEZ tekrar dener (hızı korumak için döngü değil).
        """
        referer = self._config.get("init_url")
        response = self._perform_request(method, url, build_headers(referer=referer), data)
        if response.status_code == 403:
            print(f"   [~] {self._source_id}: 403 alındı, farklı kimlikle tekrar deneniyor: {url}")
            response = self._perform_request(method, url, build_headers(referer=referer), data)
        return response

    def _perform_request(
        self, method: str, url: str, headers: Dict[str, str], data: Optional[Dict[str, Any]]
    ) -> requests.Response:
        proxies = get_proxies()
        if method == "GET":
            return self._session.get(url, headers=headers, proxies=proxies, timeout=10)
        return self._session.post(url, headers=headers, data=data, proxies=proxies, timeout=10)

    def fetch(self, query: str) -> List[str]:
        self._initialize_session()
        method = self._config.get("method", "GET").upper()
        base_url = self._config.get("base_url", "")

        try:
            if method == "GET":
                target_url = base_url.replace("{query}", query)
                response = self._request_with_identity_retry("GET", target_url)
            elif method == "POST":
                param_name = self._config.get("search_param", "q")
                payload = {param_name: query}
                if "extra_payload" in self._config:
                    payload.update(self._config["extra_payload"])
                response = self._request_with_identity_retry("POST", base_url, payload)
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