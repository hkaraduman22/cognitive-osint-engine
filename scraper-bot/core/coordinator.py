import re
from typing import List, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor
from core.interfaces import IHtmlParser, IDataStorage, IUrlFetcher
from core.base_spider import BaseSpider
from core.config_loader import ConfigLoader
from spiders.generic_spider import GenericUrlFetcher
from spiders.global_spider import FreeGlobalUrlFetcher


class DataDrivenCoordinator:
    def __init__(self, parser: IHtmlParser, storage: IDataStorage, config_path: str = "sources.json"):
        self._parser = parser
        self._storage = storage
        self._sources_db: Dict[str, Any] = ConfigLoader.load_sources(config_path)

    def _resolve_fetchers(self, query: str) -> Tuple[List[IUrlFetcher], str]:
        normalized_query = query.lower()

        # Her zaman DuckDuckGo'yu (Global) ekle! Bu sayede veri havuzumuz hep geniş kalır.
        selected_fetchers: List[IUrlFetcher] = [FreeGlobalUrlFetcher()]

        cleaned_query = query
        city_found = False

        for city, components in self._sources_db.items():
            if city in normalized_query:
                city_found = True

                # Şehir adını sorgudan siliyoruz ki hedef sitenin arama motoru bozulmasın
                compiled_clean = re.compile(re.escape(city), re.IGNORECASE)
                cleaned_query = compiled_clean.sub("", cleaned_query).strip()

                # Şehir bulunduysa, o şehre özel OSB ve Rehber botlarını da orduya kat
                if "osb" in components:
                    selected_fetchers.append(GenericUrlFetcher(f"{city}_osb", components["osb"]))
                if "rehber" in components:
                    selected_fetchers.append(GenericUrlFetcher(f"{city}_rehber", components["rehber"]))

                break  # Sadece ilk eşleşen şehri almak yeterli

        if not city_found:
            print("[!] Eşleşen yerel kaynak bulunamadı. Sadece Global OSINT (DuckDuckGo) kullanılacak.")

        return selected_fetchers, cleaned_query

    def execute(self, query: str) -> None:
        fetchers, cleaned_query = self._resolve_fetchers(query)

        print(f"[!] {len(fetchers)} adet tarayıcı bot eşzamanlı olarak başlatılıyor...\n")
        with ThreadPoolExecutor(max_workers=len(fetchers)) as executor:
            futures = [
                executor.submit(BaseSpider(fetcher, self._parser, self._storage).run, cleaned_query)
                for fetcher in fetchers
            ]
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    print(f"[-] İş parçacığı hatası: {e}")