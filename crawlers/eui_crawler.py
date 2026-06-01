"""
EUI – European Urban Initiative Crawler
Źródło: https://www.urban-initiative.eu/calls-proposals
Typ: projekty miejskie, 60M€ ERDF, dla miast i partnerów
"""
import requests
from bs4 import BeautifulSoup
from base_crawler import BaseCrawler

BASE_URL = "https://www.urban-initiative.eu"
PAGES = [
    "/calls-proposals",
    "/calls-proposals/fourth-call-proposals-innovative-actions",
]

class EUICrawler(BaseCrawler):
    def __init__(self):
        super().__init__("European Urban Initiative", "https://www.urban-initiative.eu")

    def fetch_grants(self):
        grants = []
        headers = {"User-Agent": "Mozilla/5.0 (compatible; SEEDiA-Bot/1.0)"}

        for path in PAGES:
            url = BASE_URL + path
            try:
                resp = requests.get(url, headers=headers, timeout=20)
                if resp.status_code != 200:
                    continue
                soup = BeautifulSoup(resp.text, "lxml")

                title_tag = soup.find("h1") or soup.find("title")
                title = title_tag.get_text(strip=True) if title_tag else "EUI Call for Proposals"

                main = soup.find("main") or soup.find("article") or soup.body
                content = main.get_text(" ", strip=True)[:8000] if main else ""

                grants.append({
                    "url": url,
                    "title": title,
                    "content": content,
                    "source": "European Urban Initiative",
                })
            except Exception as e:
                print(f"[EUI] Error fetching {url}: {e}")

        return grants


if __name__ == "__main__":
    crawler = EUICrawler()
    results = crawler.fetch_grants()
    for r in results:
        print(f"  → {r['title']} | {r['url']}")
    print(f"Total: {len(results)}")
