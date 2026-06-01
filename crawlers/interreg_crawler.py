from base_crawler import BaseCrawler, fetch_html, clean_text
from bs4 import BeautifulSoup
from typing import List, Dict

class InterregCrawler(BaseCrawler):
    source_name = "Interreg"
    source_url = "https://interreg.eu/calls-for-projects/"
    programme = "Interreg"

    SEEDIA_KEYWORDS = [
        "smart city", "urban", "mobility", "transport", "energy", "climate",
        "infrastructure", "digital", "innovation", "SME", "pilot"
    ]

    def crawl(self) -> List[Dict]:
        html = fetch_html(self.source_url)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        main_text = clean_text(html)
        results = []

        # Add overview page
        results.append({
            "grant_name": "Interreg — aktywne nabory projektów",
            "url": self.source_url,
            "raw_content": f"Źródło: Interreg\n{main_text[:8000]}",
            "source_name": self.source_name,
            "programme": self.programme
        })

        # Find individual call pages
        seen = set()
        call_links = soup.find_all("a", href=True)
        for link in call_links:
            href = link.get("href", "")
            title = link.get_text(strip=True)
            if not href.startswith("http"):
                href = "https://interreg.eu" + href
            if (
                any(kw in (title + href).lower() for kw in ["call", "open", "programme", "project"])
                and href not in seen
                and href != self.source_url
                and len(title) > 10
            ):
                seen.add(href)
                detail = self._fetch_detail(href)
                if detail:
                    results.append({
                        "grant_name": title,
                        "url": href,
                        "raw_content": f"Źródło: Interreg\nNazwa: {title}\n{detail}",
                        "source_name": self.source_name,
                        "programme": self.programme
                    })

        return results[:15]

    def _is_relevant(self, text: str) -> bool:
        text_lower = text.lower()
        return any(kw in text_lower for kw in self.SEEDIA_KEYWORDS)

    def _fetch_detail(self, url: str) -> str:
        try:
            html = fetch_html(url)
            return clean_text(html)[:4000] if html else ""
        except:
            return ""
