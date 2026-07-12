import json
import os
from typing import Dict, Any

class ConfigLoader:
    """Sistem kaynaklarının konfigürasyon dosyalarını yükleyen yardımcı sınıf."""

    @staticmethod
    def load_sources(file_name: str = "sources.json") -> Dict[str, Any]:
        """JSON formatındaki kaynak veri yapısını okur ve sözlük olarak döner."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[-] Hata: Konfigürasyon dosyası bulunamadı: {file_path}")
            return {}