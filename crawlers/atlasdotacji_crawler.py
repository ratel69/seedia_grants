"""
Atlas Dotacji — agregator naborów dla JST i MŚP
Źródło: https://atlasdotacji.pl
Typ: JST + MŚP, agreguje nabory KPO/FENG/regionalne, smart city, transport
"""
import requests
from base_crawler import BaseCrawler, clean_text

# Wyszukiwanie po kategoriach smart city i JST
PAGES = [
    ("https://atlasdotacji.pl/nabory/?query=smart+city&for=jst",
     "Atlas Dotacji – nabory smart city dla JST"),
    ("https://atlasdotacji.pl/nabory/?query=transport+miejski&for=jst",
     "Atlas Dotacji – transport miejski JST 2026"),
    ("https://atlasdotacji.pl/nabory/fe-fdba2206a9e2",
     "Atlas Dotacji – Starts-ups Are Us smart city (do 25.06.2026)"),
]

class AtlasDotacjiCrawler(BaseCrawler):
    source_name = "Atlas Dotacji"
    source_url  = "https://atlasdotacji.pl"
    programme   = "Agregator – KPO / FENG / FE Regionalne"

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
                    print(f"[AtlasDotacji] HTTP {resp.status_code} for {url}")
                    continue

                raw_content = clean_text(resp.text)[:8000]
                if len(raw_content) < 200:
                    print(f"[AtlasDotacji] Zbyt mała treść dla {url}")
                    continue

                grants.append({
                    "grant_name": fallback_title,
                    "url": url,
                    "raw_content": raw_content,
                    "source_name": self.source_name,
                    "programme": self.programme,
                })
                print(f"[AtlasDotacji] ✓ {fallback_title}")
            except Exception as e:
                print(f"[AtlasDotacji] Error {url}: {e}")

        return grants


if __name__ == "__main__":
    c = AtlasDotacjiCrawler()
    for r in c.crawl():
        print(f"  → {r['grant_name']} | {len(r['raw_content'])} znaków")
