"""
CEF Digital / HaDEA / Global Gateway Crawler
Źródło: https://hadea.ec.europa.eu + https://eufundingportal.eu
Typ: infrastruktura cyfrowa, backbone, 180M€+
"""
import requests
from bs4 import BeautifulSoup
from base_crawler import BaseCrawler

TARGETS = [
    {
        "url": "https://hadea.ec.europa.eu/calls-proposals/cef-digital_en",
        "title": "CEF Digital – aktywne nabory (HaDEA)",
        "source": "CEF Digital / HaDEA",
    },
    {
        "url": "https://hadea.ec.europa.eu/news/new-cef-digital-calls-open-proposals-digital-global-gateways-2026-03-17_en",
        "title": "CEF-DIG-2026-GATEWAYS – Global Gateway backbone (180M€)",
        "source": "CEF Digital / HaDEA",
    },
]

class CEFDigitalCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("CEF Digital", "https://hadea.ec.europa.eu")

    def fetch_grants(self):
        grants = []
        headers = {"User-Agent": "Mozilla/5.0 (compatible; SEEDiA-Bot/1.0)"}

        for target in TARGETS:
            url = target["url"]
            try:
                resp = requests.get(url, headers=headers, timeout=20)
                if resp.status_code != 200:
                    print(f"[CEF] HTTP {resp.status_code} for {url}")
                    continue

                soup = BeautifulSoup(resp.text, "lxml")
                for tag in soup(["nav", "footer", "script", "style"]):
                    tag.decompose()

                main = soup.find("main") or soup.find("article") or soup.body
                content = main.get_text(" ", strip=True)[:8000] if main else ""

                grants.append({
                    "url": url,
                    "title": target["title"],
                    "content": content,
                    "source": target["source"],
                })
                print(f"[CEF] ✓ {target['title']}")
            except Exception as e:
                print(f"[CEF] Error {url}: {e}")

        return grants


if __name__ == "__main__":
    crawler = CEFDigitalCrawler()
    results = crawler.fetch_grants()
    for r in results:
        print(f"  → {r['title']} | {r['url']}")
    print(f"Total: {len(results)}")
