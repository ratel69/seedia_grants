from base_crawler import BaseCrawler, fetch_html, clean_text
from bs4 import BeautifulSoup
from typing import List, Dict
import re

class PARPCrawler(BaseCrawler):
    source_name = "PARP — harmonogram naborów"
    source_url = "https://www.parp.gov.pl/harmonogram-naborow"
    programme = "PARP"

    KEYWORDS = [
        "smart city", "mobilność", "mobility", "energia", "ładowanie",
        "MŚP", "innowacje", "B+R", "cyfryzacja", "infrastruktura",
        "zielona", "klimat", "AI", "automatyzacja", "transport",
        "miasto", "elektromobilność"
    ]

    def crawl(self) -> List[Dict]:
        html = fetch_html(self.source_url)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        results = []

        # PARP publishes a table/list of upcoming calls
        rows = soup.find_all(["tr", "li", "div"], class_=re.compile(r"(row|item|nabor|call|harmonogram)", re.I))

        # Fallback: get all links that look like nabory
        if not rows:
            links = soup.find_all("a", href=re.compile(r"(nabor|konkurs|call|dofinansowanie)", re.I))
            for link in links[:30]:
                title = link.get_text(strip=True)
                href = link.get("href", "")
                if not href.startswith("http"):
                    href = "https://www.parp.gov.pl" + href
                if len(title) > 20:
                    results.append({
                        "grant_name": title,
                        "url": href,
                        "raw_content": f"Źródło: PARP\nNazwa: {title}\nLink: {href}\n" + self._fetch_detail(href),
                        "source_name": self.source_name,
                        "programme": self.programme
                    })
            return results[:20]

        for row in rows[:30]:
            text = row.get_text(separator=" ", strip=True)
            link_tag = row.find("a")
            if not link_tag:
                continue
            title = link_tag.get_text(strip=True)
            href = link_tag.get("href", "")
            if not href.startswith("http"):
                href = "https://www.parp.gov.pl" + href
            if len(title) > 15 and self._is_relevant(text):
                results.append({
                    "grant_name": title,
                    "url": href,
                    "raw_content": f"Źródło: PARP\nNazwa: {title}\n{text}\nLink: {href}",
                    "source_name": self.source_name,
                    "programme": self.programme
                })

        return results[:20]

    def _is_relevant(self, text: str) -> bool:
        text_lower = text.lower()
        return any(kw.lower() in text_lower for kw in self.KEYWORDS)

    def _fetch_detail(self, url: str) -> str:
        try:
            html = fetch_html(url)
            return clean_text(html)[:3000] if html else ""
        except:
            return ""
