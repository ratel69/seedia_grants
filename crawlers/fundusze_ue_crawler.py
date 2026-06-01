"""
Portal Funduszy Europejskich / KPO Crawler
Źródło: https://www.funduszeunijne.gov.pl + https://www.gov.pl/web/fundusze-regiony
Typ: polskie nabory KPO, FENG, FE dla MŚP
"""
import requests
from bs4 import BeautifulSoup
from base_crawler import BaseCrawler

TARGETS = [
    {
        "url": "https://www.gov.pl/web/fundusze-regiony/sprawdz-oferte-funduszy-europejskich-i-kpo-dostepna-w-maju2",
        "title": "Fundusze Europejskie i KPO – nabory maj 2026",
        "source": "Portal Funduszy UE",
    },
    {
        "url": "https://www.funduszeunijne.gov.pl/nabory",
        "title": "Fundusze Unijne – aktywne nabory",
        "source": "Portal Funduszy UE",
    },
    {
        "url": "https://www.parp.gov.pl/component/content/article/90571:sciezka-smart-nabor-wnioskow-ruszyl",
        "title": "Ścieżka SMART PARP – nabór maj-czerwiec 2026 (700M PLN)",
        "source": "PARP / FENG",
    },
]

class FunduszeUECrawler(BaseCrawler):
    def __init__(self):
        super().__init__("Portal Funduszy UE / KPO", "https://www.funduszeunijne.gov.pl")

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
                    print(f"[FunduszeUE] HTTP {resp.status_code} for {url}")
                    continue

                soup = BeautifulSoup(resp.text, "lxml")
                for tag in soup(["nav", "footer", "script", "style", "header", "aside"]):
                    tag.decompose()

                # Szukaj głównej treści
                main = (
                    soup.find("main")
                    or soup.find("div", class_=lambda x: x and "article" in str(x).lower())
                    or soup.find("div", id=lambda x: x and "content" in str(x).lower())
                    or soup.body
                )
                content = main.get_text(" ", strip=True)[:8000] if main else ""

                grants.append({
                    "url": url,
                    "title": target["title"],
                    "content": content,
                    "source": target["source"],
                })
                print(f"[FunduszeUE] ✓ {target['title']}")
            except Exception as e:
                print(f"[FunduszeUE] Error {url}: {e}")

        return grants


if __name__ == "__main__":
    crawler = FunduszeUECrawler()
    results = crawler.fetch_grants()
    for r in results:
        print(f"  → {r['title']} | {r['url']}")
    print(f"Total: {len(results)}")
