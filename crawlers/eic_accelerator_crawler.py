"""
EIC Accelerator Crawler
Źródło: https://eic.ec.europa.eu/eic-funding-opportunities/eic-accelerator_en
Typ: MŚP deep-tech, do 2.5M€ grantu + equity
"""
import requests
from bs4 import BeautifulSoup
from base_crawler import BaseCrawler, clean_text

PAGES = [
    ("https://eic.ec.europa.eu/eic-funding-opportunities/eic-accelerator_en",
     "EIC Accelerator – Open Call 2026"),
    ("https://eic.ec.europa.eu/eic-funding-opportunities/eic-accelerator/eic-accelerator-challenges-2026_en",
     "EIC Accelerator Challenges 2026 (220M€)"),
]

class EICAcceleratorCrawler(BaseCrawler):
    source_name = "EIC Accelerator"
    source_url  = "https://eic.ec.europa.eu"
    programme   = "Horizon Europe / EIC"

    def crawl(self):
        grants = []
        headers = {"User-Agent": "Mozilla/5.0 (compatible; SEEDiA-GrantBot/1.0)"}

        for url, fallback_title in PAGES:
            try:
                resp = requests.get(url, headers=headers, timeout=20)
                if resp.status_code != 200:
                    print(f"[EICAccelerator] HTTP {resp.status_code} for {url}")
                    continue

                raw_content = clean_text(resp.text)[:8000]

                grants.append({
                    "grant_name": fallback_title,
                    "url": url,
                    "raw_content": raw_content,
                    "source_name": self.source_name,
                    "programme": self.programme,
                })
                print(f"[EICAccelerator] ✓ {fallback_title}")
            except Exception as e:
                print(f"[EICAccelerator] Error {url}: {e}")

        return grants


if __name__ == "__main__":
    c = EICAcceleratorCrawler()
    for r in c.crawl():
        print(f"  → {r['grant_name']} | {r['url']}")
