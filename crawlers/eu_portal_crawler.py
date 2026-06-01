import requests
from base_crawler import BaseCrawler, fetch_html, clean_text
from bs4 import BeautifulSoup
from typing import List, Dict
import json

class EUPortalCrawler(BaseCrawler):
    source_name = "EU Funding & Tenders Portal"
    source_url = "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/calls-for-proposals"
    programme = "Horizon / EU"

    # EU Portal has a public API we can use directly
    API_URL = "https://api.tech.ec.europa.eu/search-api/prod/rest/search"

    SEARCH_TERMS = [
        "smart city",
        "urban mobility",
        "micromobility",
        "solar urban",
        "smart infrastructure",
        "resilient cities",
        "urban digital"
    ]

    def crawl(self) -> List[Dict]:
        results = []
        seen_ids = set()

        for term in self.SEARCH_TERMS:
            entries = self._search_api(term)
            for e in entries:
                if e.get("identifier") not in seen_ids:
                    seen_ids.add(e.get("identifier"))
                    results.append(e)

        if not results:
            # Fallback to HTML
            results = self._crawl_html()

        return results[:25]

    def _search_api(self, query: str) -> List[Dict]:
        """Use EU Funding & Tenders search API."""
        try:
            params = {
                "text": query,
                "pageSize": "10",
                "pageNumber": "1",
                "order": "DESC",
                "orderBy": "sortStatus",
                "facets": json.dumps([
                    {"name": "type", "values": ["1"]},  # Calls for proposals
                    {"name": "status", "values": ["31094501", "31094502"]}  # Open + Forthcoming
                ])
            }
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; SEEDiA-GrantBot/1.0)",
                "Accept": "application/json"
            }
            r = requests.get(self.API_URL, params=params, headers=headers, timeout=15)
            if r.status_code != 200:
                return []
            data = r.json()
            items = data.get("results", [])
            out = []
            for item in items:
                title = item.get("title", "")
                identifier = item.get("identifier", "")
                url = f"https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/calls-for-proposals/{identifier}"
                raw = f"Title: {title}\nIdentifier: {identifier}\n"
                raw += f"Programme: {item.get('programmePeriod', '')}\n"
                raw += f"Status: {item.get('statusLabel', '')}\n"
                raw += f"Deadline: {item.get('deadlineDate', '')}\n"
                raw += f"Budget: {item.get('budget', '')}\n"
                raw += f"Description: {item.get('description', '')[:2000]}\n"
                out.append({
                    "grant_name": title,
                    "url": url,
                    "raw_content": f"Źródło: EU Funding & Tenders Portal\n{raw}",
                    "source_name": self.source_name,
                    "programme": self.programme,
                    "identifier": identifier
                })
            return out
        except Exception as e:
            print(f"[eu_portal] API error for '{query}': {e}")
            return []

    def _crawl_html(self) -> List[Dict]:
        """Fallback HTML crawl."""
        html = fetch_html(self.source_url)
        if not html:
            return []
        main_text = clean_text(html)
        return [{
            "grant_name": "EU Funding & Tenders — aktywne nabory smart city/mobility",
            "url": self.source_url,
            "raw_content": f"Źródło: EU Funding & Tenders Portal\n{main_text[:8000]}",
            "source_name": self.source_name,
            "programme": self.programme
        }]
