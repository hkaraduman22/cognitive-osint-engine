import redis
import json
from typing import Dict, Any, List
from core.interfaces import IDataStorage

class RedisDataStorage(IDataStorage):
    """Verileri Redis listesine (Queue) atan Producer sınıfı."""
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self.r = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.queue_name = "osint_raw_queue"

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