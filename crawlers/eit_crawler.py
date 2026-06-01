from base_crawler import BaseCrawler, fetch_html, clean_text
from bs4 import BeautifulSoup
from typing import List, Dict
import re

class EITCrawler(BaseCrawler):
    source_name = "EIT Urban Mobility"
    source_url = "https://www.eiturbanmobility.eu/join-us/call-for-proposals/"
    programme = "EIT"

    def crawl(self) -> List[Dict]:
        html = fetch_html(self.source_url)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        results = []
        main_text = clean_text(html)

        # Add main page as overview entry
        results.append({
            "grant_name": "EIT Urban Mobility — aktywne nabory",
            "url": self.source_url,
            "raw_content": f"Źródło: EIT Urban Mobility\n{main_text[:8000]}",
            "source_name": self.source_name,
            "programme": self.programme
        })

        # Find individual call links
        seen = set()
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            title = link.get_text(strip=True)
            if not href.startswith("http"):
                href = "https://www.eiturbanmobility.eu" + href
            if (
                any(kw in href.lower() for kw in ["call", "proposal", "open", "apply", "raptor", "innovation"])
                and href not in seen
                and len(title) > 10
            ):
                seen.add(href)
                detail = self._fetch_detail(href)
                results.append({
                    "grant_name": title,
                    "url": href,
                    "raw_content": f"Źródło: EIT Urban Mobility\nNazwa: {title}\n{detail}",
                    "source_name": self.source_name,
                    "programme": self.programme
                })

        return results[:15]

    def _fetch_detail(self, url: str) -> str:
        try:
            html = fetch_html(url)
            return clean_text(html)[:4000] if html else ""
        except:
            return ""
