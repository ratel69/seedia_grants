import requests
import time
from bs4 import BeautifulSoup
from typing import List, Dict
import pdfplumber
import io

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SEEDiA-GrantBot/1.0)"
}

def fetch_html(url: str, timeout: int = 20) -> str:
    """Fetch HTML content from URL."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"[crawler] fetch_html error {url}: {e}")
        return ""

def fetch_pdf_text(url: str) -> str:
    """Download PDF and extract text."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        with pdfplumber.open(io.BytesIO(r.content)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages[:10])
    except Exception as e:
        print(f"[crawler] fetch_pdf error {url}: {e}")
        return ""

def clean_text(html: str) -> str:
    """Strip HTML tags and clean whitespace."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return "\n".join(lines)

class BaseCrawler:
    source_name: str = "Unknown"
    source_url: str = ""
    programme: str = ""

    def crawl(self) -> List[Dict]:
        """
        Returns list of dicts with keys:
        - grant_name
        - url
        - raw_content
        - source_name
        - programme
        """
        raise NotImplementedError
