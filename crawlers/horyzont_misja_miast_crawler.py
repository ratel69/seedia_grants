"""
Horyzont Europa — Misja 100 Miast + Klaster 5 (CIVITAS)
Źródło: https://research-and-innovation.ec.europa.eu + KPK
Typ: JST + konsorcjum miasto+firma, smart cities mission, mobilność
"""
import requests
from base_crawler import BaseCrawler, clean_text

PAGES = [
    ("https://research-and-innovation.ec.europa.eu/funding/funding-opportunities/funding-programmes-and-open-calls/horizon-europe/eu-missions-horizon-europe/climate-neutral-and-smart-cities_en",
     "Horyzont Europa – Misja 100 Miast neutralnych klimatycznie (120M€/rok)"),
    ("https://projekty.ug.edu.pl/2026/05/25/horyzont-europa-klaster-5-klimat-energia-transport-nabory-do-15-wrzesnia-2026-r/",
     "Horyzont Europa Klaster 5 – Klimat, Transport, Mobilność (deadline 15.09.2026)"),
    ("https://www.kpk.gov.pl/horyzont-europa/misje-ue/misja-smart-cities",
     "KPK – Misja Smart Cities: nabory i warunki uczestnictwa"),
]

class HoryzonMisjaMiastCrawler(BaseCrawler):
    source_name = "Horyzont Europa – Misja Miast"
    source_url  = "https://research-and-innovation.ec.europa.eu"
    programme   = "Horizon Europe / EU Mission Smart Cities"

    def crawl(self):
        grants = []
        headers = {"User-Agent": "Mozilla/5.0 (compatible; SEEDiA-GrantBot/1.0)"}

        for url, fallback_title in PAGES:
            try:
                resp = requests.get(url, headers=headers, timeout=20)
                if resp.status_code != 200:
                    print(f"[MisjaMiast] HTTP {resp.status_code} for {url}")
                    continue

                raw_content = clean_text(resp.text)[:8000]
                if len(raw_content) < 200:
                    print(f"[MisjaMiast] Zbyt mała treść dla {url}")
                    continue

                grants.append({
                    "grant_name": fallback_title,
                    "url": url,
                    "raw_content": raw_content,
                    "source_name": self.source_name,
                    "programme": self.programme,
                })
                print(f"[MisjaMiast] ✓ {fallback_title}")
            except Exception as e:
                print(f"[MisjaMiast] Error {url}: {e}")

        return grants


if __name__ == "__main__":
    c = HoryzonMisjaMiastCrawler()
    for r in c.crawl():
        print(f"  → {r['grant_name']} | {len(r['raw_content'])} znaków")
