"""
NATO DIANA — Defence Innovation Accelerator for the North Atlantic
Ocena dopasowania SEEDiA: 7/10
Kategorie: Energy & Power (jCharge), Sensing & Surveillance (kamery AI)

URL: https://www.diana.nato.int
Challenges: https://www.diana.nato.int/challenges.html
"""
import requests
from bs4 import BeautifulSoup
from base_crawler import BaseCrawler


class NatoDianaCrawler(BaseCrawler):
    source_name = "NATO DIANA — Defence Innovation Accelerator"
    source_url = "https://www.diana.nato.int/challenges.html"
    programme = "NATO DIANA Accelerator"

    CHALLENGE_AREAS = [
        {
            "id": "DIANA-2027-ENERGY",
            "title": "Energy and Power — 2027 Cohort",
            "url": "https://www.diana.nato.int/challenges.html",
            "description": (
                "NATO DIANA Energy & Power challenge. Focus: reliable energy supply, EV charging for military vehicles, "
                "portable/mobile power solutions, energy resilience for forward operating bases. "
                "SEEDiA jCharge (micromobility/EV charging stations) directly applicable: "
                "adaptation to military EV fleet charging (jeeps, light armoured vehicles, drones). "
                "Phase 1 grant: €100,000. Phase 2 (selected): up to €300,000. "
                "Access to 23 accelerators and 182 test centres across NATO countries including Poland. "
                "Non-dilutive funding. 2027 cohort applications expected June-July 2026."
            ),
            "deadline": "2026-07-15",
            "budget": "€100,000 (Phase 1) + up to €300,000 (Phase 2)",
            "eligibility": "SMEs and start-ups from NATO member countries. No prior defence experience required. Simple 5-page application.",
        },
        {
            "id": "DIANA-2027-SENSING",
            "title": "Sensing and Surveillance — 2027 Cohort",
            "url": "https://www.diana.nato.int/challenges.html",
            "description": (
                "NATO DIANA Sensing & Surveillance challenge. Focus: autonomous sensing systems, "
                "situational awareness, AI-based object detection and recognition, perimeter monitoring, "
                "real-time threat detection. "
                "SEEDiA AI cameras and incity.io platform directly applicable: "
                "AI cameras with object/person detection, incity.io as sensor data aggregation platform. "
                "Adaptation: military perimeter surveillance, base security monitoring, field ISR (intelligence, surveillance, reconnaissance). "
                "2027 cohort expected. Previous cohort (2025): 73 firms selected from 2600+ applications, 15 to Phase 2. "
                "Poland has national contact point through PARP or MON."
            ),
            "deadline": "2026-07-15",
            "budget": "€100,000 (Phase 1) + up to €300,000 (Phase 2)",
            "eligibility": "Any NATO country SME/startup. Single company application. Brak wymogu doświadczenia obronnego.",
        },
        {
            "id": "DIANA-2027-INFRA",
            "title": "Critical Infrastructure and Logistics — 2027 Cohort",
            "url": "https://www.diana.nato.int/challenges.html",
            "description": (
                "NATO DIANA Critical Infrastructure challenge. Focus: protection and monitoring of "
                "critical infrastructure (energy, transport, communications), logistics management systems, "
                "supply chain resilience. "
                "SEEDiA infokiosks and incity.io SaaS relevant for infrastructure monitoring and "
                "logistics information management. Smart shelters as hardened infrastructure nodes."
            ),
            "deadline": "2026-07-15",
            "budget": "€100,000 (Phase 1) + up to €300,000 (Phase 2)",
            "eligibility": "NATO country SME/startup. No consortium required.",
        },
    ]

    def crawl(self):
        # Try live fetch from diana.nato.int
        live_grants = self._fetch_diana_site()
        if live_grants:
            return live_grants
        return self._static_challenges()

    def _fetch_diana_site(self):
        """Fetch current challenge areas from NATO DIANA website."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml",
            }
            r = requests.get(self.source_url, headers=headers, timeout=20)
            if r.status_code != 200:
                return []

            soup = BeautifulSoup(r.text, "html.parser")
            page_text = soup.get_text(separator="\n", strip=True)

            # Check for open cohort information
            grants = []
            if any(kw in page_text.lower() for kw in ["open", "apply", "challenge", "cohort", "2027"]):
                # Extract challenge sections
                sections = soup.find_all(["h2", "h3", "h4"])
                for sec in sections:
                    title = sec.get_text(strip=True)
                    if len(title) > 5:
                        link = sec.find("a")
                        url = link["href"] if link and link.get("href") else self.source_url
                        if not url.startswith("http"):
                            url = f"https://www.diana.nato.int{url}"
                        grants.append({
                            "grant_name": f"NATO DIANA — {title[:100]}",
                            "url": url,
                            "raw_content": (
                                f"Programme: {self.programme}\n"
                                f"Challenge: {title}\n"
                                f"Source: {self.source_name} (live)\n"
                                f"Track hint: dual_use\n"
                                f"Budget: €100,000 Phase 1, up to €300,000 Phase 2\n"
                                f"Eligibility: NATO country SMEs and start-ups, no defence experience required\n"
                                f"Relevance: NATO accelerator for dual-use deep tech"
                            ),
                            "source_name": self.source_name,
                            "programme": self.programme,
                        })
                if grants:
                    return grants[:5]
        except Exception:
            pass
        return []

    def _static_challenges(self):
        grants = []
        for challenge in self.CHALLENGE_AREAS:
            raw_content = (
                f"Programme: {self.programme}\n"
                f"Challenge ID: {challenge['id']}\n"
                f"Title: {challenge['title']}\n"
                f"Description: {challenge['description']}\n"
                f"Expected deadline: {challenge['deadline']}\n"
                f"Budget: {challenge['budget']}\n"
                f"Eligibility: {challenge['eligibility']}\n"
                f"Track hint: dual_use\n"
                f"Applicant type: Single SME/startup, NATO country\n"
                f"Note: 2026 cohort closed (deadline 11.07.2025). Prepare for 2027 cohort now.\n"
                f"Polish contact: PARP or MON (NCP for NATO DIANA Poland)\n"
                f"Relevance to SEEDiA: jCharge (Energy), AI cameras + incity.io (Sensing/Surveillance)\n"
                f"Source: {self.source_name}"
            )
            grants.append({
                "grant_name": f"{challenge['id']} — {challenge['title']}",
                "url": challenge["url"],
                "raw_content": raw_content,
                "source_name": self.source_name,
                "programme": self.programme,
            })
        return grants
