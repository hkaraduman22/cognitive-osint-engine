from core.interfaces import IUrlFetcher, IHtmlParser, IDataStorage


class BaseSpider:
    """Tek bir kaynak için veri toplama ve ayrıştırma iş akışını yöneten sınıf."""

    def __init__(self, fetcher: IUrlFetcher, parser: IHtmlParser, storage: IDataStorage):
        self._fetcher = fetcher
        self._parser = parser
        self._storage = storage

    def run(self, query: str) -> None:
        print(f"[*] '{self._fetcher.source_id}' kaynağı üzerinden '{query}' aranıyor...")
        urls = self._fetcher.fetch(query)

        for url in urls:
            raw_text = self._parser.parse(url)
            if raw_text:
                self._storage.save({
                    "kaynak": self._fetcher.source_id,
                    "hedef_url": url,
                    "ham_metin": raw_text
                })