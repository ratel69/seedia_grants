"""
EIC Accelerator Crawler
Źródło: https://eic.ec.europa.eu/eic-funding-opportunities/eic-accelerator_en
Typ: MŚP deep-tech, do 2.5M€ grantu + equity
"""
import requests
from bs4 import BeautifulSoup
from base_crawler import BaseCrawler

BASE_URL = "https://eic.ec.europa.eu"
PAGES = [
    "/eic-funding-opportunities/eic-accelerator_en",
    "/eic-funding-opportunities/eic-accelerator/eic-accelerator-challenges-2026_en",
]

class EICAcceleratorCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("EIC Accelerator", "https://eic.ec.europa.eu")

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

                # Tytuł strony jako nazwa grantu
                title_tag = soup.find("h1") or soup.find("title")
                title = title_tag.get_text(strip=True) if title_tag else "EIC Accelerator"

                # Zbierz treść do AI extraction
                main = soup.find("main") or soup.find("div", class_=lambda x: x and "content" in x.lower())
                content = main.get_text(" ", strip=True) if main else soup.get_text(" ", strip=True)
                content = content[:8000]

                grants.append({
                    "url": url,
                    "title": title,
                    "content": content,
                    "source": "EIC Accelerator",
                })
            except Exception as e:
                print(f"[EICAccelerator] Error fetching {url}: {e}")

        return grants


if __name__ == "__main__":
    crawler = EICAcceleratorCrawler()
    results = crawler.fetch_grants()
    for r in results:
        print(f"  → {r['title']} | {r['url']}")
    print(f"Total: {len(results)}")
