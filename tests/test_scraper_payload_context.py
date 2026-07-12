# ruff: noqa: E402

import sys
from pathlib import Path
from unittest.mock import MagicMock


SCRAPER_PATH = Path(__file__).resolve().parents[1] / "scraper-bot"
if str(SCRAPER_PATH) not in sys.path:
    sys.path.insert(0, str(SCRAPER_PATH))

from core.base_spider import BaseSpider


def test_scraper_payload_keeps_original_search_query() -> None:
    fetcher = MagicMock()
    fetcher.source_id = "test_source"
    fetcher.fetch.return_value = ["https://example.com/company"]
    parser = MagicMock()
    parser.parse.return_value = {
        "telefonlar": [],
        "e_postalar": [],
        "ham_metin": "CNC freze üreticisi",
    }
    storage = MagicMock()

    BaseSpider(fetcher, parser, storage).run(
        "CNC freze üreticileri",
        search_history_id=9,
        search_query="İstanbul CNC freze üreticileri",
    )

    payload = storage.save.call_args.args[0]
    assert payload["search_query"] == "İstanbul CNC freze üreticileri"
    assert payload["search_history_id"] == 9
