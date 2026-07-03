import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Optional, Dict, Any
from core.interfaces import IHtmlParser

class GeneralHtmlParser(IHtmlParser):
    """Web sayfalarından metin ve iletişim bilgilerini ayıklayan akıllı sınıf."""

    def __init__(self):
        self._headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:152.0) Gecko/20100101 Firefox/152.0'}
        self._email_regex = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        self._phone_regex = re.compile(r'(?:\+?90|0)?\s*\(?\d{3}\)?\s*\d{3}\s*[\-\.]?\s*\d{2}\s*[\-\.]?\s*\d{2}')

    def parse(self, url: str) -> Optional[Dict[str, Any]]:
        try:
            res = requests.get(url, headers=self._headers, timeout=10)

            if res.status_code != 200:
                print(f"   [-] Web sitesi engelledi veya kapalı: {url} (HTTP Kod: {res.status_code})")
                return None

            soup = BeautifulSoup(res.content, 'html.parser')
            raw_text = soup.get_text(separator=' ', strip=True)

            emails = list(set(self._email_regex.findall(raw_text)))
            phones = list(set(self._phone_regex.findall(raw_text)))

            if not emails or not phones:
                for link in soup.find_all('a', href=True):
                    href = link['href'].lower()
                    if any(keyword in href for keyword in ['iletisim', 'contact', 'hakkinda', 'about']) or \
                            any(keyword in link.text.lower()
                                for keyword in
                                ['iletişim', 'contact', 'hakkında', 'about']):
                        contact_url = urljoin(url, link['href'])
                        try:
                            print(f"   [*] Anasayfada eksik bilgi. İletişim sayfası taranıyor: {contact_url}")
                            res_contact = requests.get(contact_url, headers=self._headers, timeout=5)
                            soup_contact = BeautifulSoup(res_contact.content, 'html.parser')
                            contact_text = soup_contact.get_text(separator=' ', strip=True)

                            emails.extend(self._email_regex.findall(contact_text))
                            phones.extend(self._phone_regex.findall(contact_text))
                            raw_text += " " + contact_text
                            break
                        except Exception:
                            pass

            return {
                "telefonlar": list(set([p.strip() for p in phones]))[:3],
                "e_postalar": list(set(emails))[:3],
                "ham_metin": raw_text[:3000]
            }

        except Exception as e:
            print(f"   [-] Siteye erişilemedi (Timeout/Hata): {url} -> {e}")
            return None