# ruff: noqa: E402

import sys
from pathlib import Path


CORE_API_PATH = Path(__file__).resolve().parents[1] / "autonomous-osint-agent" / "core-api"
if str(CORE_API_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_API_PATH))

from app.routers.company_router import resolve_scraper_directory


def test_scraper_directory_is_resolved_from_workspace() -> None:
    scraper_directory = resolve_scraper_directory()

    assert scraper_directory.name == "scraper-bot"
    assert (scraper_directory / "main.py").is_file()
