import asyncio
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from analiz import AnalizMotoru
from redis_listener import RedisSwarmListener


class DummyRedis:
    def __init__(self):
        self.messages = []

    async def ping(self):
        return True

    async def brpop(self, queue_name, timeout=0):
        if self.messages:
            return self.messages.pop(0)
        return None


@patch("redis_listener.aioredis")
@patch.object(AnalizMotoru, "analiz_et", new_callable=AsyncMock)
def test_listener_processes_message_and_filters_elites(
    mock_analyze, mock_redis_module
):
    os.environ["REDIS_URL"] = "redis://localhost:6379/0"
    os.environ["OSINT_REDIS_QUEUE"] = "osint:raw_text"

    mock_analyze.return_value = [
        {"name": "Elit Yazılım", "website": "https://elit.com", "location": "İstanbul", "description": "Yapay zeka platformu", "source": "web", "confidence_score": 90, "analiz_tarihi": "2026-07-06"},
        {"name": "Düşük Güven", "website": "https://dusuk.com", "location": "Ankara", "description": "Hizmet sağlayıcı", "source": "web", "confidence_score": 70, "analiz_tarihi": "2026-07-06"},
    ]

    dummy_redis = DummyRedis()
    dummy_redis.messages.append(("osint:raw_text", "Bu bir test metnidir."))
    mock_redis_module.from_url.return_value = dummy_redis

    listener = RedisSwarmListener()

    async def run_test():
        await listener.connect()
        processed = await listener.process_text("Bu bir test metnidir.")
        return processed

    processed = asyncio.run(run_test())

    assert len(processed) == 2
    assert any(item["confidence_score"] >= 85 for item in processed)
    assert any(item["confidence_score"] < 85 for item in processed)


@patch("redis_listener.aioredis")
def test_listener_handles_empty_queue(mock_redis_module):
    dummy_redis = DummyRedis()
    mock_redis_module.from_url.return_value = dummy_redis

    listener = RedisSwarmListener()

    async def run_test():
        await listener.connect()
        result = await listener.redis.brpop("osint:raw_text", timeout=1)
        return result

    result = asyncio.run(run_test())
    assert result is None
