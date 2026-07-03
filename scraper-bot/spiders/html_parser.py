import re
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
from core.interfaces import IHtmlParser


class GeneralHtmlParser(IHtmlParser):
    """Web sayfalarından metin ve iletişim bilgilerini (Regex ile) ayıklayan sınıf."""

    def __init__(self):
        self._headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        # Düzenli İfadeler (Regex) - E-posta ve Telefon tespiti
        self._email_regex = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        # Temel Türkçe telefon formatlarını yakalayacak basit regex
        self._phone_regex = re.compile(r'(?:\+90|0)?\s*[1-9]\d{2}\s*\d{3}\s*\d{2}\s*\d{2}')

    def parse(self, url: str) -> Optional[Dict[str, Any]]:
        try:
            res = requests.get(url, headers=self._headers, timeout=15)
            if res.status_code != 200:
                return None

            soup = BeautifulSoup(res.content, 'html.parser')

            # HTML etiketlerini yok sayıp sadece görünür metni alıyoruz
            raw_text = soup.get_text(separator=' ', strip=True)

            # Regex ile verileri çekip mükerrerleri (set ile) temizliyoruz
            emails = list(set(self._email_regex.findall(raw_text)))
            phones = list(set(self._phone_regex.findall(raw_text)))

            return {
                "telefonlar": phones[:3],
                "e_postalar": emails[:3],
                # NLP modelinin belleğini taşırmamak için ilk 2500 karakteri alıyoruz
                "ham_metin": raw_text[:2500]
            }
        except Exception:
            return None