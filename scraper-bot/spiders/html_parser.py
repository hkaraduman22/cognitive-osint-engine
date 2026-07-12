import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Optional, Dict, Any, List
from core.interfaces import IHtmlParser
from core.http_identity import build_headers, get_proxies


class GeneralHtmlParser(IHtmlParser):
    """Web sayfalarından metin ve iletişim bilgilerini ayıklayan akıllı ve modüler sınıf."""

    def __init__(self):
        self._session = requests.Session()
        self._email_regex = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        self._phone_regex = re.compile(
            r'(?<!\d)(?:\+90|0)\s*\(?\d{3}\)?\s*\d{3}\s*[\-\.]?\s*\d{2}\s*[\-\.]?\s*\d{2}(?!\d)')

        self._banned_protocols = ('mailto:', 'tel:', 'javascript:')
        self._banned_domains = ['facebook.com', 'twitter.com', 'linkedin.com', 'sharer']
        self._directory_sites = ['bulurum.com', 'dosb.org.tr', '11880.com.tr']
        self._contact_keywords = ['iletisim', 'contact', 'hakkinda', 'about', 'iletişim', 'hakkında','hakkimizda','hakkımızda','home']

    def parse(self, url: str) -> Optional[Dict[str, Any]]:
        """Ana orkestrasyon metodu."""
        soup = self._fetch_soup(url)
        if not soup:
            return None

        raw_text = self._extract_xray_text(soup)
        emails = self._extract_matches(self._email_regex, raw_text)
        phones = self._extract_matches(self._phone_regex, raw_text)

        # Deep Scan (Yönlendirme Zekası)
        if not emails or not phones:
            deep_urls = self._find_deep_scan_urls(soup, url)
            for deep_url in deep_urls:
                print(f"   [*] Derin Tarama (Deep Scan) başlatıldı: {deep_url}")
                # Referer'i bir onceki sayfa yaparak gercek gezinme davranisini taklit ediyoruz
                deep_soup = self._fetch_soup(deep_url, referer=url)
                if deep_soup:
                    deep_text = self._extract_xray_text(deep_soup)
                    emails.extend(self._extract_matches(self._email_regex, deep_text))
                    phones.extend(self._extract_matches(self._phone_regex, deep_text))
                    raw_text += " " + deep_text

        return self._format_results(phones, emails, raw_text)


    def _fetch_soup(self, url: str, referer: Optional[str] = None) -> Optional[BeautifulSoup]:
        """
        HTTP isteğini yapar ve BeautifulSoup objesi döner. 403 (bot engeli) alınırsa
        farklı bir UA/dil/referer/proxy kimliğiyle YALNIZCA BİR KEZ tekrar dener.
        """
        try:
            proxies = get_proxies()
            res = self._session.get(url, headers=build_headers(referer=referer), proxies=proxies, timeout=10)
            if res.status_code == 403:
                print(f"   [~] 403 alındı, farklı kimlikle tekrar deneniyor: {url}")
                res = self._session.get(url, headers=build_headers(referer=referer), proxies=proxies, timeout=10)
            if res.status_code == 200:
                return BeautifulSoup(res.content, 'html.parser')
            else:
                print(f"   [-] Web sitesi engelledi veya kapalı: {url} (HTTP Kod: {res.status_code})")
                return None
        except Exception as e:
            print(f"   [-] Siteye erişilemedi: {url} -> {e}")
            return None

    def _extract_xray_text(self, soup: BeautifulSoup) -> str:
        """Görünür metni, gizli meta etiketlerini ve mailto linklerini çıkarır."""
        text_parts = [soup.get_text(separator=' ', strip=True)]

        for meta in soup.find_all('meta', content=True):
            text_parts.append(meta['content'])

        for a in soup.find_all('a', href=True):
            if a['href'].startswith('mailto:'):
                text_parts.append(a['href'].replace('mailto:', ''))

        return " ".join(text_parts)

    def _find_deep_scan_urls(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Sayfadaki linkleri analiz eder ve yalnızca geçerli hedef URL'leri toplar."""
        target_urls = []
        current_domain = urlparse(base_url).netloc

        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            text = a.text.lower()

            # Anti-Junk Filtresi: Çöpleri ve sosyal medyayı atla
            if href.startswith(self._banned_protocols) or any(
                    banned in href.lower() for banned in self._banned_domains):
                continue

            #Dizin (Rehber) sitesindeysek, firmanın dış web sitesini bul
            if href.startswith('http') and current_domain not in href:
                if not any(directory in href for directory in self._directory_sites):
                    if 'web site' in text or 'ziyaret' in text or (a.parent and a.parent.get('itemprop') == 'url'):
                        target_urls.append(href)

            #Kendi sitesindeysek, İletişim/Hakkında sayfalarını bul
            elif any(k in href.lower() for k in self._contact_keywords) or any(
                    k in text for k in self._contact_keywords):
                if not any(directory in current_domain for directory in self._directory_sites):
                    target_urls.append(urljoin(base_url, href))

        # Listeyi benzersiz yap ve ilk 2 sonucu dön
        return list(set(target_urls))[:2]

    def _extract_matches(self, regex_pattern: re.Pattern, text: str) -> List[str]:
        """Verilen regex paternine göre eşleşmeleri bulur."""
        return list(set(regex_pattern.findall(text)))

    def _format_results(self, phones: List[str], emails: List[str], raw_text: str) -> Dict[str, Any]:
        """Çıktıyı temizler ve standart JSON sözleşmesine uygun hale getirir."""
        cleaned_phones = [p.strip() for p in phones if len(p.strip()) > 9]

        return {
            "telefonlar": list(set(cleaned_phones))[:3],
            "e_postalar": list(set(emails))[:3],
            "ham_metin": raw_text[:3000]
        }