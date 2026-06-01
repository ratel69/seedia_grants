"""
EUI – European Urban Initiative Crawler
Źródło: https://www.urban-initiative.eu/calls-proposals
Typ: projekty miejskie, 60M€ ERDF
"""
import requests
from base_crawler import BaseCrawler, clean_text

PAGES = [
    ("https://www.urban-initiative.eu/calls-proposals/fourth-call-proposals-innovative-actions",
     "EUI Fourth Call – Innovative Actions (60M€ ERDF)"),
    ("https://www.urban-initiative.eu/news/new-innovative-action-call-proposals-launches-early-2026",
     "EUI – New Innovative Action Call 2026"),
]

class EUICrawler(BaseCrawler):
    source_name = "European Urban Initiative (EUI)"
    source_url  = "https://www.urban-initiative.eu"
    programme   = "European Urban Initiative / ERDF"

    def crawl(self):
        grants = []
        headers = {"User-Agent": "Mozilla/5.0 (compatible; SEEDiA-GrantBot/1.0)"}

        for url, fallback_title in PAGES:
            try:
                resp = requests.get(url, headers=headers, timeout=20)
                if resp.status_code != 200:
                    print(f"[EUI] HTTP {resp.status_code} for {url}")
                    continue

                raw_content = clean_text(resp.text)[:8000]

                grants.append({
                    "grant_name": fallback_title,
                    "url": url,
                    "raw_content": raw_content,
                    "source_name": self.source_name,
                    "programme": self.programme,
                })
                print(f"[EUI] ✓ {fallback_title}")
            except Exception as e:
                print(f"[EUI] Error {url}: {e}")

        return grants


if __name__ == "__main__":
    c = EUICrawler()
    for r in c.crawl():
        print(f"  → {r['grant_name']} | {r['url']}")
