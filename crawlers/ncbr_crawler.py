from base_crawler import BaseCrawler, fetch_html, clean_text
from bs4 import BeautifulSoup
from typing import List, Dict
import re

class NCBRCrawler(BaseCrawler):
    source_name = "NCBR — harmonogram konkursów"
    source_url = "https://www.gov.pl/web/ncbr/harmonogram-konkursow-2026"
    programme = "NCBR"

    KEYWORDS = [
        "smart", "mobilność", "energia", "miasto", "AI", "infrastruktura",
        "B+R", "demonstrator", "innowacje", "elektromobilność", "klimat",
        "transport", "cyfryzacja", "zielona transformacja"
    ]

    def crawl(self) -> List[Dict]:
        html = fetch_html(self.source_url)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        results = []

        # Gov.pl uses article/list structure
        articles = soup.find_all(["article", "li", "div"], class_=re.compile(r"(item|row|konkurs|call|program)", re.I))

        links = soup.find_all("a", href=re.compile(r"(konkurs|nabor|program|call)", re.I))

        seen_urls = set()
        for link in links[:40]:
            title = link.get_text(strip=True)
            href = link.get("href", "")
            if not href.startswith("http"):
                href = "https://www.gov.pl" + href
            if href in seen_urls or len(title) < 15:
                continue
            seen_urls.add(href)

            parent_text = ""
            parent = link.find_parent(["li", "tr", "div", "article"])
            if parent:
                parent_text = parent.get_text(separator=" ", strip=True)

            results.append({
                "grant_name": title,
                "url": href,
                "raw_content": f"Źródło: NCBR\nNazwa: {title}\n{parent_text}\nLink: {href}",
                "source_name": self.source_name,
                "programme": self.programme
            })

        # Also get main page text as one entry for AI to parse
        main_text = clean_text(html)
        if main_text:
            results.append({
                "grant_name": "NCBR Harmonogram konkursów 2026 — przegląd",
                "url": self.source_url,
                "raw_content": f"Źródło: NCBR\n{main_text[:8000]}",
                "source_name": self.source_name,
                "programme": self.programme
            })

        return results[:25]
