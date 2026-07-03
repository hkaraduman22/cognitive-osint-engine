from typing import List, Dict, Any
from core.interfaces import IDataStorage

class RamDataStorage(IDataStorage):
    """Verileri diske yazmadan sadece RAM üzerinde (liste içinde) izole tutan sınıf."""
    def __init__(self):
        self._storage: List[Dict[str, Any]] = []

    def save(self, data: Dict[str, Any]) -> None:
        self._storage.append(data)

    def get_all(self) -> List[Dict[str, Any]]:
        return self._storage