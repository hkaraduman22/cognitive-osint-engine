import sys
import os
import asyncio
from core.interfaces import IUrlFetcher, IHtmlParser, IDataStorage,IAiEngine

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)


class BaseSpider:
    """Tek bir kaynak için veri toplama ve ayrıştırma iş akışını yöneten sınıf."""

    def __init__(self, fetcher: IUrlFetcher, parser: IHtmlParser, storage: IDataStorage,ai_engine: IAiEngine):
        self._fetcher = fetcher
        self._parser = parser
        self._storage = storage
        self._ai_engine = ai_engine

    def run(self, query: str) -> None:
        print(f"[*] '{self._fetcher.source_id}' kaynağı üzerinden '{query}' aranıyor...")
        urls = self._fetcher.fetch(query)

        for url in urls:
            parsed_data = self._parser.parse(url)

            if parsed_data:
                ham_metin = parsed_data.get("ham_metin", "")

                ai_analiz_sonucu = {}
                if ham_metin:
                    try:
                        ai_analiz_sonucu = asyncio.run(self._ai_engine.analiz_et(ham_metin))
                    except Exception as e:
                        print(f"   [-] Yapay Zeka (LLM) Analiz Hatası: {e}")
                        ai_analiz_sonucu = {"hata": str(e)}

                self._storage.save({
                    "kaynak": self._fetcher.source_id,
                    "arama_kriteri": query,
                    "hedef_url": url,
                    "iletisim_bilgileri": {
                        "telefonlar": parsed_data.get("telefonlar", []),
                        "e_postalar": parsed_data.get("e_postalar", [])
                    },
                    "ai_analizi": ai_analiz_sonucu,
                    "ham_metin": ham_metin
                })