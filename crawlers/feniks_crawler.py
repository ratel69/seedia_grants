"""
FENiKS – Fundusze Europejskie na Infrastrukturę, Klimat, Środowisko
Źródło: https://feniks.gov.pl
Typ: JST — transport miejski, infrastruktura, zeroemisyjność
Wnioskodawcy: JST, związki metropolitalne, organizatorzy/operatorzy transportu
"""
import requests
from base_crawler import BaseCrawler, clean_text

PAGES = [
    ("https://feniks.gov.pl/aktualnosci-nowy-nabor-na-ekologiczny-transport-miejski/",
     "FENiKS FENX.03.01 – Ekologiczny transport miejski (700M PLN)"),
    ("https://feniks.gov.pl/nabory/",
     "FENiKS – aktywne nabory 2026"),
]

class FENiKSCrawler(BaseCrawler):
    source_name = "FENiKS (Infrastruktura, Klimat, Środowisko)"
    source_url  = "https://feniks.gov.pl"
    programme   = "FENiKS / EFRR / Fundusz Spójności"

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
                    print(f"[FENiKS] HTTP {resp.status_code} for {url}")
                    continue

                raw_content = clean_text(resp.text)[:8000]
                if len(raw_content) < 200:
                    print(f"[FENiKS] Zbyt mała treść dla {url}")
                    continue

                grants.append({
                    "grant_name": fallback_title,
                    "url": url,
                    "raw_content": raw_content,
                    "source_name": self.source_name,
                    "programme": self.programme,
                })
                print(f"[FENiKS] ✓ {fallback_title}")
            except Exception as e:
                print(f"[FENiKS] Error {url}: {e}")

        return grants


if __name__ == "__main__":
    c = FENiKSCrawler()
    for r in c.crawl():
        print(f"  → {r['grant_name']} | {len(r['raw_content'])} znaków")
