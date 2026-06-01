"""
CEF Digital / HaDEA / Global Gateway Crawler
Typ: infrastruktura cyfrowa, backbone, 180M€+
"""
import requests
from base_crawler import BaseCrawler, clean_text

PAGES = [
    ("https://hadea.ec.europa.eu/news/new-cef-digital-calls-open-proposals-digital-global-gateways-2026-03-17_en",
     "CEF-DIG-2026-GATEWAYS – Global Gateway backbone (180M€)"),
    ("https://hadea.ec.europa.eu/calls-proposals_en",
     "HaDEA – aktywne nabory 2026"),
]

class CEFDigitalCrawler(BaseCrawler):
    source_name = "CEF Digital / Global Gateway"
    source_url  = "https://hadea.ec.europa.eu"
    programme   = "Connecting Europe Facility – Digital"

    def crawl(self):
        grants = []
        headers = {"User-Agent": "Mozilla/5.0 (compatible; SEEDiA-GrantBot/1.0)"}

        for url, fallback_title in PAGES:
            try:
                resp = requests.get(url, headers=headers, timeout=20)
                if resp.status_code != 200:
                    print(f"[CEF] HTTP {resp.status_code} for {url}")
                    continue

                raw_content = clean_text(resp.text)[:8000]

                grants.append({
                    "grant_name": fallback_title,
                    "url": url,
                    "raw_content": raw_content,
                    "source_name": self.source_name,
                    "programme": self.programme,
                })
                print(f"[CEF] ✓ {fallback_title}")
            except Exception as e:
                print(f"[CEF] Error {url}: {e}")

        return grants


if __name__ == "__main__":
    c = CEFDigitalCrawler()
    for r in c.crawl():
        print(f"  → {r['grant_name']} | {r['url']}")
