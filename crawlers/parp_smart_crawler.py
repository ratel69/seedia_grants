"""
PARP – Ścieżka SMART + Starts-ups Are Us Crawler
Typ: MŚP, wdrożenie B+R, smart city, KPO/FENG
"""
import requests
from base_crawler import BaseCrawler, clean_text

PAGES = [
    ("https://www.parp.gov.pl/component/content/article/90571:sciezka-smart-nabor-wnioskow-ruszyl",
     "Ścieżka SMART – nabór MŚP maj-czerwiec 2026 (700M PLN)"),
    ("https://www.parp.gov.pl/component/content/article/90662:polskie-startupy-smart-city-z-szansa-na-miedzynarodowy-rozwoj-startuje-nowy-nabor-parp",
     "Starts-ups Are Us – smart city (PARP, 2M PLN)"),
]

class PARPSmartCrawler(BaseCrawler):
    source_name = "PARP Ścieżka SMART"
    source_url  = "https://www.parp.gov.pl"
    programme   = "FENG / KPO"

    def crawl(self):
        grants = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "pl-PL,pl;q=0.9",
        }

        for url, fallback_title in PAGES:
            try:
                resp = requests.get(url, headers=headers, timeout=20)
                if resp.status_code != 200:
                    print(f"[PARP-SMART] HTTP {resp.status_code} for {url}")
                    continue

                raw_content = clean_text(resp.text)[:8000]

                grants.append({
                    "grant_name": fallback_title,
                    "url": url,
                    "raw_content": raw_content,
                    "source_name": self.source_name,
                    "programme": self.programme,
                })
                print(f"[PARP-SMART] ✓ {fallback_title}")
            except Exception as e:
                print(f"[PARP-SMART] Error {url}: {e}")

        return grants


if __name__ == "__main__":
    c = PARPSmartCrawler()
    for r in c.crawl():
        print(f"  → {r['grant_name']} | {r['url']}")
