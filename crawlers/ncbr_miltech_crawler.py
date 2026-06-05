"""
NCBR MilTech — Program akceleracyjny MON + Akces NCBR
Ocena dopasowania SEEDiA: 5/10
Tematyka: AI dla bezpieczeństwa, systemy ochrony obiektów, autonomiczne systemy

URL: https://akces-ncbr.pl/miltech
"""
import requests
from bs4 import BeautifulSoup
from base_crawler import BaseCrawler


class NcbrMiltechCrawler(BaseCrawler):
    source_name = "NCBR MilTech — Program MON + Akces NCBR"
    source_url = "https://akces-ncbr.pl/miltech"
    programme = "MilTech / Akces NCBR + MON"

    KNOWN_CALLS = [
        {
            "id": "MILTECH-2026-OPEN",
            "title": "MilTech — Nabór ciągły 2026 (Akces NCBR + MON)",
            "url": "https://akces-ncbr.pl/miltech",
            "description": (
                "Otwarty nabór do programu akceleracyjnego MilTech dla startupów i wczesnych MŚP z technologiami obronnymi. "
                "Wsparcie: 300,000 zł grantu bezzwrotnego + 100,000 zł w usługach mentoringowych. "
                "Otwarto: 15 grudnia 2025. Nabór ciągły do wyczerpania środków. "
                "Relevantne dla SEEDiA kategorie: "
                "(1) Systemy ochrony obiektów istotnych dla wojska — kamery AI SEEDiA z detekcją osób/pojazdów; "
                "(2) AI wspierające autonomię systemów — platforma incity.io jako system zarządzania sensorami; "
                "(3) Modularne systemy BSP — potencjalna integracja z dronami w incity.io. "
                "Program ma wartość networkingową: kontakty z MON i ścieżka testów wojskowych. "
                "Grant 300k zł jest mały dla dojrzałego MŚP, ale program otwiera drzwi do rynku MON."
            ),
            "deadline": "2026-12-31",
            "budget": "300,000 zł grant + 100,000 zł usługi mentoringowe",
            "eligibility": "Startupy i wczesne MŚP z siedzibą w Polsce. Technologie obronne lub dual-use.",
        },
    ]

    def crawl(self):
        # Try live fetch
        live = self._fetch_miltech_site()
        if live:
            return live
        return self._static_calls()

    def _fetch_miltech_site(self):
        """Fetch current status from NCBR MilTech website."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html",
                "Accept-Language": "pl-PL,pl;q=0.9",
            }
            r = requests.get(self.source_url, headers=headers, timeout=15)
            if r.status_code != 200:
                return []

            soup = BeautifulSoup(r.text, "html.parser")
            page_text = soup.get_text(separator="\n", strip=True)

            # Check if nabór is still open
            open_keywords = ["nabór", "aplikuj", "zgłoś", "rejestracja", "otwart", "trwa"]
            closed_keywords = ["zakończon", "zamknięt", "wyczerpan"]

            is_open = any(kw in page_text.lower() for kw in open_keywords)
            is_closed = any(kw in page_text.lower() for kw in closed_keywords)

            if is_closed and not is_open:
                # Nabór zamknięty — zwróć info ale z odpowiednim statusem
                return [{
                    "grant_name": "NCBR MilTech — Nabór zakończony (monitoruj nowy)",
                    "url": self.source_url,
                    "raw_content": (
                        f"Programme: {self.programme}\n"
                        f"Status: Nabór ZAKOŃCZONY — monitoruj stronę dla nowej edycji\n"
                        f"Source: {self.source_name} (live check)\n"
                        f"Track hint: dual_use\n"
                        f"Budget: 300,000 zł + 100,000 zł usługi\n"
                        f"Note: Poprzedni nabór otwarty od 15.12.2025. Sprawdź nową edycję.\n"
                        f"Relevance: MilTech akcelerator dla MŚP z technologiami obronnymi"
                    ),
                    "source_name": self.source_name,
                    "programme": self.programme,
                }]

            if is_open:
                # Wyciągnij więcej szczegółów
                deadline_text = ""
                for line in page_text.split("\n"):
                    if any(kw in line.lower() for kw in ["termin", "deadline", "do kiedy", "30.", "31.", "2026"]):
                        deadline_text = line.strip()[:200]
                        break

                return [{
                    "grant_name": "NCBR MilTech — Nabór ciągły (Akces NCBR + MON)",
                    "url": self.source_url,
                    "raw_content": (
                        f"Programme: {self.programme}\n"
                        f"Status: NABÓR OTWARTY\n"
                        f"Deadline info: {deadline_text or 'ciągły do wyczerpania'}\n"
                        f"Budget: 300,000 zł grant bezzwrotny + 100,000 zł usługi mentoringowe\n"
                        f"Description: Program akceleracyjny MilTech MON + NCBR dla startupów/MŚP z technologiami obronnymi. "
                        f"Relevantne: kamery AI → ochrona obiektów wojskowych; incity.io → zarządzanie sensorami.\n"
                        f"Track hint: dual_use\n"
                        f"Eligibility: Startupy i MŚP z siedzibą w Polsce\n"
                        f"Source: {self.source_name} (live)"
                    ),
                    "source_name": self.source_name,
                    "programme": self.programme,
                }]
        except Exception:
            pass
        return []

    def _static_calls(self):
        grants = []
        for call in self.KNOWN_CALLS:
            raw_content = (
                f"Programme: {self.programme}\n"
                f"Call ID: {call['id']}\n"
                f"Title: {call['title']}\n"
                f"Description: {call['description']}\n"
                f"Deadline: {call['deadline']}\n"
                f"Budget: {call['budget']}\n"
                f"Eligibility: {call['eligibility']}\n"
                f"Track hint: dual_use\n"
                f"Applicant type: Startup/early MŚP, Polish entity\n"
                f"Relevance to SEEDiA: AI cameras for military object protection; incity.io as sensor management\n"
                f"Note: Small grant amount (300k PLN) but strategic value — MON network and military testing access\n"
                f"Source: {self.source_name}"
            )
            grants.append({
                "grant_name": call["title"],
                "url": call["url"],
                "raw_content": raw_content,
                "source_name": self.source_name,
                "programme": self.programme,
            })
        return grants
