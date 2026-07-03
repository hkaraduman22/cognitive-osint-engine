import re
from typing import List, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor
from core.interfaces import IHtmlParser, IDataStorage, IUrlFetcher
from core.base_spider import BaseSpider
from core.config_loader import ConfigLoader
from spiders.generic_spider import GenericUrlFetcher
from spiders.global_spider import FreeGlobalUrlFetcher

class DataDrivenCoordinator:
    """Sorgu kriterlerine göre kaynakları filtreleyen ve paralel olarak çalıştıran koordinatör sınıf."""

    def __init__(self, parser: IHtmlParser, storage: IDataStorage, config_path: str = "sources.json"):
        self._parser = parser
        self._storage = storage
        self._sources_db: Dict[str, Any] = ConfigLoader.load_sources(config_path)

    def _resolve_fetchers(self, query: str) -> Tuple[List[IUrlFetcher], str]:
        """Sorgu metnindeki lokasyon verilerine göre uygun kaynakları belirler ve sorguyu temizler."""
        normalized_query = query.lower()
        selected_fetchers: List[IUrlFetcher] = []
        cleaned_query = query

        for city, components in self._sources_db.items():
            if city in normalized_query:
                compiled_clean = re.compile(re.escape(city), re.IGNORECASE)
                cleaned_query = compiled_clean.sub("", cleaned_query).strip()

                if "osb" in components:
                    selected_fetchers.append(GenericUrlFetcher(f"{city}_osb", components["osb"]))
                if "to" in components:
                    selected_fetchers.append(GenericUrlFetcher(f"{city}_to", components["to"]))

        if not selected_fetchers:
            print("[!] Eşleşen yerel kaynak bulunamadı. Ücretsiz DuckDuckGo OSINT moduna geçiliyor.")
            selected_fetchers.append(FreeGlobalUrlFetcher())

        return selected_fetchers, cleaned_query

    def execute(self, query: str) -> None:
        """Filtrelenen tüm toplayıcıları iş parçacığı havuzunda asenkron olarak yürütür."""
        fetchers, cleaned_query = self._resolve_fetchers(query)

        print(f"[!] {len(fetchers)} adet tarayıcı bot eşzamanlı olarak başlatılıyor...\n")
        with ThreadPoolExecutor(max_workers=len(fetchers)) as executor:
            futures = [
                executor.submit(BaseSpider(fetcher, self._parser, self._storage).run, cleaned_query)
                for fetcher in fetchers
            ]
            for future in futures:
                future.result()