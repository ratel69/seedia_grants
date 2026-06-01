"""
PARP – Ścieżka SMART + Starts-ups Are Us Crawler
Źródło: https://www.parp.gov.pl + https://www.funduszeunijne.gov.pl
Typ: MŚP, B+R, smart city, KPO/FENG
"""
import requests
from bs4 import BeautifulSoup
from base_crawler import BaseCrawler

TARGETS = [
    {
        "url": "https://www.parp.gov.pl/component/content/article/90571:sciezka-smart-nabor-wnioskow-ruszyl",
        "title": "Ścieżka SMART – nabór wniosków (PARP/FENG)",
        "source": "PARP Ścieżka SMART",
    },
    {
        "url": "https://www.parp.gov.pl/component/content/article/90662:polskie-startupy-smart-city-z-szansa-na-miedzynarodowy-rozwoj-startuje-nowy-nabor-parp",
        "title": "Starts-ups Are Us – smart city (PARP)",
        "source": "PARP Starts-ups Are Us",
    },
    {
        "url": "https://www.parp.gov.pl/nabory",
        "title": "PARP – aktywne nabory",
        "source": "PARP",
    },
]

class PARPSmartCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("PARP SMART", "https://www.parp.gov.pl")

    def fetch_grants(self):
        grants = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "pl-PL,pl;q=0.9",
        }

        for target in TARGETS:
            url = target["url"]
            try:
                resp = requests.get(url, headers=headers, timeout=20)
                if resp.status_code != 200:
                    print(f"[PARP-SMART] HTTP {resp.status_code} for {url}")
                    continue

                soup = BeautifulSoup(resp.text, "lxml")

                # Usuń nawigację i stopkę
                for tag in soup(["nav", "footer", "script", "style", "header"]):
                    tag.decompose()

                main = soup.find("main") or soup.find("article") or soup.find("div", class_=lambda x: x and "article" in str(x).lower())
                content = main.get_text(" ", strip=True)[:8000] if main else soup.get_text(" ", strip=True)[:8000]

                grants.append({
                    "url": url,
                    "title": target["title"],
                    "content": content,
                    "source": target["source"],
                })
                print(f"[PARP-SMART] ✓ {target['title']}")
            except Exception as e:
                print(f"[PARP-SMART] Error {url}: {e}")

        return grants


if __name__ == "__main__":
    crawler = PARPSmartCrawler()
    results = crawler.fetch_grants()
    for r in results:
        print(f"  → {r['title']} | {r['url']}")
    print(f"Total: {len(results)}")
