import asyncio
import importlib.util
from pathlib import Path
from unittest.mock import AsyncMock

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
listener_spec = importlib.util.spec_from_file_location(
    "listener_under_test",
    PROJECT_ROOT / "redis_listener.py",
)
assert listener_spec is not None and listener_spec.loader is not None
listener_module = importlib.util.module_from_spec(listener_spec)
listener_spec.loader.exec_module(listener_module)


def test_plain_text_message_is_supported() -> None:
    engine = AsyncMock()
    engine.analiz_et.return_value = [{"name": "Örnek Firma", "confidence_score": 90}]

    result = asyncio.run(
        listener_module.process_queue_message("Düz firma metni", engine)
    )

    assert result["kaynak"] == "Bilinmeyen"
    engine.analiz_et.assert_awaited_once_with(
        "Düz firma metni",
        search_history_id=None,
        source_url=None,
        search_query=None,
    )


def test_non_object_json_message_is_rejected() -> None:
    engine = AsyncMock()

    with pytest.raises(ValueError, match="JSON nesnesi"):
        asyncio.run(listener_module.process_queue_message('["geçersiz"]', engine))

    engine.analiz_et.assert_not_awaited()
