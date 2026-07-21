import re
from typing import List, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor
from app.scraper.core.interfaces import IHtmlParser, IDataStorage, IUrlFetcher
from app.scraper.core.base_spider import BaseSpider
from app.scraper.core.config_loader import ConfigLoader
from app.scraper.spiders.generic_spider import GenericUrlFetcher
from app.scraper.spiders.global_spider import FreeGlobalUrlFetcher
from app.scraper.spiders.kariyer_spider import KariyerUrlFetcher
from app.scraper.spiders.haber_spider import HaberUrlFetcher

class DataDrivenCoordinator:
    def __init__(self, parser: IHtmlParser, storage: IDataStorage, config_path: str = "sources.json"):
        self._parser = parser
        self._storage = storage
        self._sources_db: Dict[str, Any] = ConfigLoader.load_sources(config_path)

    def _resolve_fetchers(self, query: str) -> Tuple[List[IUrlFetcher], str]:
        normalized_query = query.lower()

        selected_fetchers: List[IUrlFetcher] = [
            FreeGlobalUrlFetcher(suffix="", delay=0.0),
            FreeGlobalUrlFetcher(suffix="OSB", delay=0.5),
            FreeGlobalUrlFetcher(suffix="Ticaret Odası", delay=1.0),
            KariyerUrlFetcher(delay=1.5),
            HaberUrlFetcher(delay=2.0)
        ]

        cleaned_query = query
        city_found = False

        for city, components in self._sources_db.items():
            if city in normalized_query:
                city_found = True
                compiled_clean = re.compile(re.escape(city), re.IGNORECASE)
                cleaned_query = compiled_clean.sub("", cleaned_query).strip()

                if "osb" in components:
                    selected_fetchers.append(GenericUrlFetcher(f"{city}_osb", components["osb"]))
                if "rehber" in components:
                    selected_fetchers.append(GenericUrlFetcher(f"{city}_rehber", components["rehber"]))
                break

        if not city_found:
            print("[!] Eslesen yerel kaynak bulunamadi. Genel arama ordusu devreye alinacak.")

        return selected_fetchers, cleaned_query

    def execute(self, query: str) -> None:
        fetchers, cleaned_query = self._resolve_fetchers(query)

        print(f"[!] Toplam {len(fetchers)} adet tarayici bot eszamanli olarak baslatiliyor...\n")
        with ThreadPoolExecutor(max_workers=len(fetchers)) as executor:
            futures = [
                executor.submit(BaseSpider(fetcher, self._parser, self._storage).run, cleaned_query)
                for fetcher in fetchers
            ]
            for future in futures:
                try:
                    future.result()
                except Exception as exc:
                    print(f"[-] Is parcacigi calisirken hata olustu: {exc}")