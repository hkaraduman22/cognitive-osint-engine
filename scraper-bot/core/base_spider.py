from core.interfaces import IUrlFetcher, IHtmlParser, IDataStorage

class BaseSpider:
    def __init__(self, fetcher: IUrlFetcher, parser: IHtmlParser, storage: IDataStorage):
        self._fetcher = fetcher
        self._parser = parser
        self._storage = storage

    def run(self, query: str, search_history_id: int | None = None) -> None:
        print(f"[*] '{self._fetcher.source_id}' araniyor...")
        urls = self._fetcher.fetch(query)

        for url in urls:
            parsed_data = self._parser.parse(url)
            if parsed_data:
                payload = {
                    "query": query,
                    "kaynak": self._fetcher.source_id,
                    "hedef_url": url,
                    "iletisim_bilgileri": {
                        "telefonlar": parsed_data.get("telefonlar", []),
                        "e_postalar": parsed_data.get("e_postalar", [])
                    },
                    "ham_metin": parsed_data.get("ham_metin", "")
                }
                if search_history_id is not None:
                    payload["search_history_id"] = search_history_id
                self._storage.save(payload)