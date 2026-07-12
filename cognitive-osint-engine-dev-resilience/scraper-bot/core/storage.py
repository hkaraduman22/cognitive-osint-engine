import redis
import json
import os
from typing import Dict, Any, List
from core.interfaces import IDataStorage
from core.sqlite_queue import SQLiteMessageQueue


class QueueDataStorage(IDataStorage):
    """MVP için varsayılan SQLite, gerektiğinde Redis kullanan kuyruk adaptörü."""

    def __init__(self) -> None:
        self.queue_name = os.getenv("OSINT_REDIS_QUEUE", "osint_raw_queue")
        self.backend = os.getenv("QUEUE_BACKEND", "sqlite").strip().lower()
        if self.backend == "redis":
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            self._redis = redis.from_url(redis_url, decode_responses=True)
            self._sqlite = None
        elif self.backend == "sqlite":
            self._redis = None
            self._sqlite = SQLiteMessageQueue()
        else:
            raise ValueError("QUEUE_BACKEND yalnızca 'sqlite' veya 'redis' olabilir.")

    def save(self, data: Dict[str, Any]) -> None:
        payload = json.dumps(data, ensure_ascii=False)
        if self._sqlite is not None:
            self._sqlite.push(self.queue_name, payload)
        else:
            self._redis.rpush(self.queue_name, payload)

    def get_all(self) -> List[Dict[str, Any]]:
        if self._sqlite is not None:
            values = self._sqlite.list_all(self.queue_name)
        else:
            values = self._redis.lrange(self.queue_name, 0, -1)
        return [json.loads(value) for value in values]

class RedisDataStorage(IDataStorage):
    """Verileri Redis listesine (Queue) atan Producer sınıfı."""
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            self.r = redis.from_url(redis_url, decode_responses=True)
        else:
            self.r = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.queue_name = os.getenv("OSINT_REDIS_QUEUE", "osint_raw_queue")

    def save(self, data: Dict[str, Any]) -> None:
        """Veriyi JSON formatında Redis kuyruğuna ekler."""
        try:
            self.r.rpush(self.queue_name, json.dumps(data))
        except Exception as e:
            print(f"[-] Redis Yazma Hatası: {e}")

    def get_all(self) -> List[Dict[str, Any]]:
        """Test amaçlı tüm kuyruğu çeker."""
        data = self.r.lrange(self.queue_name, 0, -1)
        return [json.loads(d) for d in data]
