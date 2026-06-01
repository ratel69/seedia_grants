"""
Portal Funduszy Europejskich / KPO Crawler
Typ: polskie nabory KPO, FENG, FE dla MŚP
"""
import requests
from base_crawler import BaseCrawler, clean_text

PAGES = [
    ("https://www.gov.pl/web/fundusze-regiony/sprawdz-oferte-funduszy-europejskich-i-kpo-dostepna-w-maju2",
     "Fundusze Europejskie i KPO – nabory maj 2026 (9 mld PLN)"),
    ("https://www.parp.gov.pl/nabory",
     "PARP – aktywne nabory 2026"),
]

class FunduszeUECrawler(BaseCrawler):
    source_name = "Portal Funduszy UE / KPO"
    source_url  = "https://www.funduszeunijne.gov.pl"
    programme   = "KPO / FENG / Fundusze Europejskie"

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
                    print(f"[FunduszeUE] HTTP {resp.status_code} for {url}")
                    continue

                raw_content = clean_text(resp.text)[:8000]

                grants.append({
                    "grant_name": fallback_title,
                    "url": url,
                    "raw_content": raw_content,
                    "source_name": self.source_name,
                    "programme": self.programme,
                })
                print(f"[FunduszeUE] ✓ {fallback_title}")
            except Exception as e:
                print(f"[FunduszeUE] Error {url}: {e}")

        return grants


if __name__ == "__main__":
    c = FunduszeUECrawler()
    for r in c.crawl():
        print(f"  → {r['grant_name']} | {r['url']}")
