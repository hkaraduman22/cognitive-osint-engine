"""
Hedef web sitelerinin bot-tespiti / 403 engellemesini azaltmak icin istek kimligini
(User-Agent, Accept-Language, Referer) her istekte degistiren ve istege bagli
proxy rotasyonu saglayan yardimci modul.

Not: Proxy kullanimi varsayilan olarak KAPALIDIR (SCRAPER_PROXY_LIST tanimli degilse
get_proxies() None doner) - boylece proxy'siz calisirken hicbir ek gecikme olusmaz.
"""
import itertools
import os
import random
from typing import Optional

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

ACCEPT_LANGUAGES = [
    "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "tr,en-US;q=0.9,en;q=0.8",
    "en-US,en;q=0.9,tr;q=0.8",
]

DEFAULT_REFERERS = [
    "https://www.google.com/",
    "https://www.google.com.tr/",
    "https://www.bing.com/",
]


def build_headers(referer: Optional[str] = None) -> dict:
    """
    Her cagrida farkli UA/dil/referer kombinasyonu doner. `referer` verilirse
    (orn. deep-scan zincirinde bir onceki sayfanin URL'i) gercek gezinme
    davranisini taklit etmek icin oncelikli olarak kullanilir.
    """
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": random.choice(ACCEPT_LANGUAGES),
        "Referer": referer or random.choice(DEFAULT_REFERERS),
    }


_proxy_cycle: Optional["itertools.cycle[str]"] = None


def _load_proxy_list() -> list[str]:
    raw = os.getenv("SCRAPER_PROXY_LIST", "").strip()
    if not raw:
        return []
    return [proxy.strip() for proxy in raw.split(",") if proxy.strip()]


def get_proxies() -> Optional[dict]:
    """
    SCRAPER_PROXY_LIST ortam degiskeninde virgulle ayrilmis proxy URL'leri
    (orn. "http://user:pass@host1:port,http://host2:port") varsa aralarinda
    sirayla doner. Tanimli degilse None doner - proxy kullanilmaz.
    """
    global _proxy_cycle
    proxy_list = _load_proxy_list()
    if not proxy_list:
        return None
    if _proxy_cycle is None:
        _proxy_cycle = itertools.cycle(proxy_list)
    proxy_url = next(_proxy_cycle)
    return {"http": proxy_url, "https": proxy_url}
