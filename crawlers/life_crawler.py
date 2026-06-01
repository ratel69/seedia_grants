from base_crawler import BaseCrawler, fetch_html, clean_text
from bs4 import BeautifulSoup
from typing import List, Dict

class LIFECrawler(BaseCrawler):
    source_name = "LIFE / CINEA"
    source_url = "https://cinea.ec.europa.eu/life-calls-proposals-2026_en"
    programme = "LIFE"

    BACKUP_URL = "https://cinea.ec.europa.eu/programmes/life/life-calls-proposals_en"

    def crawl(self) -> List[Dict]:
        results = []

        for url in [self.source_url, self.BACKUP_URL]:
            html = fetch_html(url)
            if not html:
                continue
            soup = BeautifulSoup(html, "html.parser")
            main_text = clean_text(html)

            results.append({
                "grant_name": f"LIFE/CINEA — nabory 2026 ({url})",
                "url": url,
                "raw_content": f"Źródło: LIFE/CINEA\n{main_text[:8000]}",
                "source_name": self.source_name,
                "programme": self.programme
            })

            # Find specific call links
            for link in soup.find_all("a", href=True):
                href = link.get("href", "")
                title = link.get_text(strip=True)
                if not href.startswith("http"):
                    href = "https://cinea.ec.europa.eu" + href
                if (
                    any(kw in href.lower() for kw in ["call", "proposal", "life", "climate", "energy", "nature"])
                    and len(title) > 15
                    and href != url
                ):
                    detail = self._fetch_detail(href)
                    if detail:
                        results.append({
                            "grant_name": title,
                            "url": href,
                            "raw_content": f"Źródło: LIFE/CINEA\nNazwa: {title}\n{detail}",
                            "source_name": self.source_name,
                            "programme": self.programme
                        })

            if results:
                break

        # Deduplicate by URL
        seen = set()
        unique = []
        for r in results:
            if r["url"] not in seen:
                seen.add(r["url"])
                unique.append(r)

        return unique[:15]

    def _fetch_detail(self, url: str) -> str:
        try:
            html = fetch_html(url)
            return clean_text(html)[:4000] if html else ""
        except:
            return ""
