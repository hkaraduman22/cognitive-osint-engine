# ruff: noqa: E402

import sys
from pathlib import Path
from unittest.mock import MagicMock


SCRAPER_PATH = Path(__file__).resolve().parents[1] / "scraper-bot"
if str(SCRAPER_PATH) not in sys.path:
    sys.path.insert(0, str(SCRAPER_PATH))

from core.coordinator import DataDrivenCoordinator


def test_turkish_istanbul_selects_local_source() -> None:
    coordinator = DataDrivenCoordinator(parser=MagicMock(), storage=MagicMock())

    fetchers, cleaned_query = coordinator._resolve_fetchers(
        "İstanbul CNC freze üreticileri"
    )

    assert "İstanbul" not in cleaned_query
    assert "CNC freze üreticileri" == cleaned_query
    assert any(fetcher.source_id == "istanbul_osb" for fetcher in fetchers)
