from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class IDataStorage(ABC):
    """RAM üzerinde veri saklama işlemlerini tanımlayan arayüz."""
    @abstractmethod
    def save(self, data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def get_all(self) -> List[Dict[str, Any]]:
        pass

class IUrlFetcher(ABC):
    """Arama motoru veya dizin üzerinden hedef URL'leri toplayan arayüz."""
    @property
    @abstractmethod
    def source_id(self) -> str:
        pass

    @abstractmethod
    def fetch(self, query: str) -> List[str]:
        pass

class IHtmlParser(ABC):
    """Hedef URL'nin HTML içeriğini indirip temiz metne ve kontaklara dönüştüren arayüz."""
    @abstractmethod
    def parse(self, url: str) -> Optional[Dict[str, Any]]:
        pass

class IAiEngine(ABC):
    @abstractmethod
    async def analiz_et(self, ham_metin: str) -> Dict[str, Any]:
        pass