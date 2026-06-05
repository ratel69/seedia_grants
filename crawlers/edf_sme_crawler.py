"""
EDF — European Defence Fund (Non-thematic SME Calls) + EUDIS Business Accelerator
Ocena dopasowania SEEDiA: 7/10
Tematy: surveillance systems, digital solutions, energy solutions, "add-on actions adapting civil solutions to defence"

URL: https://eudis.europa.eu/eudis-tracks/sme-calls_en
Portal: https://ec.europa.eu/info/funding-tenders/opportunities/portal/
"""
import requests
from bs4 import BeautifulSoup
from base_crawler import BaseCrawler


class EDFSmeCrawler(BaseCrawler):
    source_name = "EDF / EUDIS — European Defence Fund SME Calls"
    source_url = "https://eudis.europa.eu/eudis-tracks/sme-calls_en"
    programme = "European Defence Fund (EDF) WP 2026"

    RELEVANT_CALLS = [
        {
            "id": "EDF-2026-LS-DA-SME-NT",
            "title": "Development Actions by SMEs — Non-Thematic Call",
            "url": "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-details/edf-2026-ls-da-sme-nt",
            "description": (
                "Non-thematic development call for SMEs. Explicitly covers: surveillance systems, "
                "digital solutions, energy solutions, infrastructure protection, and 'add-on actions adapting "
                "civil solutions to defence sector'. Minimum 2 independent entities from 2 EU/NO countries. "
                "Budget: €30M dedicated to SME development actions. "
                "Directly relevant: SEEDiA AI cameras → military surveillance adaptation; "
                "infokiosks → field command support systems; jCharge → EV charging for military vehicles; "
                "incity.io SaaS → command & control dashboard. "
                "TRL requirements: TRL 4+ at start, TRL 6+ at end."
            ),
            "deadline": "2026-09-29",
            "budget": "€30M (SME Development Actions pool)",
            "eligibility": "Min 2 SMEs from min 2 EU/Norwegian countries. Entities must be EU/NO-controlled.",
        },
        {
            "id": "EDF-2026-LS-DIS-RA-SMERO-NT",
            "title": "Research Actions by SMEs and Research Organisations — Non-Thematic",
            "url": "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-details/edf-2026-ls-dis-ra-smero-nt",
            "description": (
                "Research-stage non-thematic call for SMEs and research organisations. "
                "Open to any defence-relevant topic at TRL 2-5. Part of the €60M SME pool for EDF WP 2026. "
                "Relevant for SEEDiA if developing new AI/sensing technologies with defence application. "
                "Can include academic partner (e.g. WAT — Polish Military University of Technology)."
            ),
            "deadline": "2026-09-29",
            "budget": "Part of €60M SME pool",
            "eligibility": "Min 2 entities (SME + research org) from 2 EU/NO countries.",
        },
        {
            "id": "EDF-2026-LS-DIS-NT",
            "title": "Disruptive Defence Technologies — STEP Call",
            "url": "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-details/edf-2026-ls-dis-nt",
            "description": (
                "Disruptive technology call for AI, deep-tech, clean energy, autonomous systems. "
                "Budget: €27M. Duration 12-24 months. TRL 4+. "
                "Relevant for SEEDiA AI cameras and autonomous monitoring platform incity.io. "
                "Min 2 independent companies, 2 EU/NO countries."
            ),
            "deadline": "2026-09-29",
            "budget": "€27M (Disruptive STEP)",
            "eligibility": "Min 2 independent companies, 2+ EU/NO countries. TRL 4+.",
        },
        {
            "id": "EUDIS-ACCELERATOR-2026",
            "title": "EUDIS Business Accelerator — Cohort Autumn 2026",
            "url": "https://eudis.europa.eu/eudis-tracks/sme-calls_en",
            "description": (
                "EU Defence Innovation Scheme Business Accelerator — non-monetary support programme "
                "for SMEs entering the defence market. Provides mentoring, coaching, network access "
                "and preparation for EDF calls. Autumn 2026 cohort starts September 2026. "
                "Ideal entry point for SEEDiA before submitting to EDF SME non-thematic call. "
                "Also includes EUDIS Defence Hackathon (3rd edition, multiple EU locations)."
            ),
            "deadline": "2026-09-01",
            "budget": "In-kind support (mentoring, coaching, EDF preparation)",
            "eligibility": "EU SMEs and start-ups entering defence/dual-use market.",
        },
    ]

    def crawl(self):
        # Try to fetch live data from EUDIS portal
        live_calls = self._fetch_eudis_portal()
        if live_calls:
            return live_calls
        # Fallback to static known calls
        return self._static_calls()

    def _fetch_eudis_portal(self):
        """Try to extract current open calls from EUDIS SME page."""
        try:
            headers = {"User-Agent": "Mozilla/5.0 (compatible; GrantBot/1.0)"}
            r = requests.get(self.source_url, headers=headers, timeout=15)
            if r.status_code != 200:
                return []
            soup = BeautifulSoup(r.text, "html.parser")
            # Look for call links / titles on the page
            calls_found = []
            for link in soup.find_all("a", href=True):
                href = link.get("href", "")
                text = link.get_text(strip=True)
                if any(kw in href.lower() or kw in text.lower() for kw in ["edf-2026", "sme", "call", "non-thematic"]):
                    if len(text) > 10 and "http" in href:
                        calls_found.append((text, href))
            if calls_found:
                grants = []
                for title, url in calls_found[:5]:
                    grants.append({
                        "grant_name": f"EDF/EUDIS — {title[:120]}",
                        "url": url,
                        "raw_content": (
                            f"Programme: {self.programme}\n"
                            f"Title: {title}\n"
                            f"Source: {self.source_name} (live fetch)\n"
                            f"URL: {url}\n"
                            f"Track hint: dual_use\n"
                            f"Relevance: EDF/EUDIS defence fund for SMEs, dual-use technology development"
                        ),
                        "source_name": self.source_name,
                        "programme": self.programme,
                    })
                return grants
        except Exception:
            pass
        return []

    def _static_calls(self):
        grants = []
        for call in self.RELEVANT_CALLS:
            raw_content = (
                f"Programme: {self.programme}\n"
                f"Call ID: {call['id']}\n"
                f"Title: {call['title']}\n"
                f"Description: {call['description']}\n"
                f"Deadline: {call['deadline']}\n"
                f"Budget: {call['budget']}\n"
                f"Eligibility: {call['eligibility']}\n"
                f"Track hint: dual_use\n"
                f"Applicant type: SME consortium, min 2 companies, 2 EU/NO countries\n"
                f"Relevance to SEEDiA: AI cameras → military surveillance; jCharge → military EV charging; "
                f"infokiosks → field command systems; incity.io → C2 dashboard\n"
                f"Source: {self.source_name}"
            )
            grants.append({
                "grant_name": f"{call['id']} — {call['title']}",
                "url": call["url"],
                "raw_content": raw_content,
                "source_name": self.source_name,
                "programme": self.programme,
            })
        return grants
