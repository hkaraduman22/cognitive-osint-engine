import asyncio
import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) in sys.path:
    sys.path.remove(str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT))

listener_spec = importlib.util.spec_from_file_location(
    "canonical_redis_listener",
    PROJECT_ROOT / "redis_listener.py",
)
assert listener_spec is not None and listener_spec.loader is not None
listener_module = importlib.util.module_from_spec(listener_spec)
listener_spec.loader.exec_module(listener_module)
process_queue_message = listener_module.process_queue_message


def test_scraper_payload_reaches_analysis_engine() -> None:
    engine = AsyncMock()
    engine.analiz_et.return_value = [{"name": "Örnek Firma", "confidence_score": 90}]
    payload = json.dumps(
        {
            "kaynak": "test_source",
            "hedef_url": "https://example.com",
            "ham_metin": "İstanbul merkezli CNC freze üreticisi.",
            "search_history_id": 42,
        }
    )

    result = asyncio.run(process_queue_message(payload, engine))

    engine.analiz_et.assert_awaited_once_with(
        "İstanbul merkezli CNC freze üreticisi.",
        search_history_id=42,
        source_url="https://example.com",
    )
    assert result["kaynak"] == "test_source"
    assert result["search_history_id"] == 42
    assert result["analiz_sonuclari"][0]["confidence_score"] == 90


def test_empty_scraper_payload_is_rejected() -> None:
    engine = AsyncMock()

    with pytest.raises(ValueError, match="ham_metin"):
        asyncio.run(process_queue_message('{"ham_metin": ""}', engine))

    engine.analiz_et.assert_not_awaited()
