"""
PARP – Ścieżka SMART + Starts-ups Are Us Crawler
Typ: MŚP, wdrożenie B+R, smart city, KPO/FENG
"""
import requests
from base_crawler import BaseCrawler, clean_text

# PARP blokuje boty na stronie głównej — używamy artykułów z ogłoszeniami naborów
PAGES = [
    ("https://www.funduszeunijne.gov.pl/nabory/#/domyslne=1/10502=3740",
     "Ścieżka SMART – nabór MŚP (PARP/FENG, 700M PLN)"),
    ("https://www.gov.pl/web/fundusze-regiony/sprawdz-oferte-funduszy-europejskich-i-kpo-dostepna-w-maju2",
     "PARP / FENG – nabory maj-czerwiec 2026"),
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
