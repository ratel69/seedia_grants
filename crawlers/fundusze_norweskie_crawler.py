"""
Fundusze Norweskie i EOG — Program Rozwoju Lokalnego i Smart City
Źródło: https://www.gov.pl/web/fundusze-regiony
Typ: JST — Smart City 4.0, AI w usługach miejskich, odporność, 94M€
Wnioskodawcy: miasta (110 wybranych miast polskich)
"""
import requests
from base_crawler import BaseCrawler, clean_text

PAGES = [
    ("https://www.gov.pl/web/fundusze-regiony/a",
     "Fundusze Norweskie – Smart City 4.0 i odporność miast (94M€)"),
    ("https://www.norwaygrants.org/en/sectors/local-development-and-poverty-reduction/",
     "Norway Grants – Local Development 2026"),
]

class FunduszeNorweskieCrawler(BaseCrawler):
    source_name = "Fundusze Norweskie / EOG"
    source_url  = "https://www.norwaygrants.org"
    programme   = "Fundusze Norweskie i EOG 2021-2028"

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
                    print(f"[NorwayGrants] HTTP {resp.status_code} for {url}")
                    continue

                raw_content = clean_text(resp.text)[:8000]
                if len(raw_content) < 200:
                    print(f"[NorwayGrants] Zbyt mała treść dla {url}")
                    continue

                grants.append({
                    "grant_name": fallback_title,
                    "url": url,
                    "raw_content": raw_content,
                    "source_name": self.source_name,
                    "programme": self.programme,
                })
                print(f"[NorwayGrants] ✓ {fallback_title}")
            except Exception as e:
                print(f"[NorwayGrants] Error {url}: {e}")

        return grants


if __name__ == "__main__":
    c = FunduszeNorweskieCrawler()
    for r in c.crawl():
        print(f"  → {r['grant_name']} | {len(r['raw_content'])} znaków")
