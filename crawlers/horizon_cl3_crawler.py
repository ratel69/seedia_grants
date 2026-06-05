"""
Horizon Europe — Klaster 3: Civil Security for Society
Ocena dopasowania SEEDiA: 8/10
Tematy: border surveillance, urban security, AI dla bezpieczeństwa, disruptive tech

URL: https://rea.ec.europa.eu/funding-and-grants/horizon-europe-cluster-3-civil-security-society_en
Portal: https://ec.europa.eu/info/funding-tenders/opportunities/portal/
"""
import requests
from bs4 import BeautifulSoup
from .base_crawler import BaseCrawler


class HorizonCL3Crawler(BaseCrawler):
    source_name = "Horizon Europe — Klaster 3 (Civil Security)"
    source_url = "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/calls-for-proposals?programPart=43108390&programmePeriod=2021-2027&status=31094501,31094502"
    programme = "Horizon Europe Cluster 3"

    # Tematy z WP 2026 bezpośrednio relevantne dla SEEDiA
    RELEVANT_CALLS = [
        {
            "id": "HORIZON-CL3-2026-01-BM-01",
            "title": "Advanced border surveillance and situational awareness",
            "url": "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-details/horizon-cl3-2026-01-bm-01",
            "description": "Advanced surveillance systems for border management, AI-based situational awareness, sensor integration for law enforcement. Directly relevant to SEEDiA AI cameras and incity.io platform.",
            "deadline": "2026-11-05",
            "budget": "€350M (Cluster 3 total WP 2026)",
            "eligibility": "Consortium min. 3 entities from 3 EU/associated countries. SMEs as partners welcome.",
        },
        {
            "id": "HORIZON-CL3-2026-01-INFRA-02",
            "title": "Security challenges of green transition in urban areas",
            "url": "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-details/horizon-cl3-2026-01-infra-02",
            "description": "Security implications of green and digital urban infrastructure transformation. Smart city security, EV charging infrastructure protection, urban monitoring. Highly relevant to SEEDiA smart shelters, jCharge and incity.io.",
            "deadline": "2026-11-05",
            "budget": "€32.5M (Disaster Resilient Society component)",
            "eligibility": "Consortium min. 3 entities from 3+ countries.",
        },
        {
            "id": "HORIZON-CL3-2026-01-SSRI-01",
            "title": "Open topic on disruptive technological innovations for civil security",
            "url": "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-details/horizon-cl3-2026-01-ssri-01",
            "description": "Open call for disruptive deep-tech innovations applicable to civil security. No predefined scope — AI, IoT, autonomous systems, advanced sensing all eligible. SEEDiA AI cameras and incity.io fit the sensing/AI security profile.",
            "deadline": "2026-11-05",
            "budget": "Part of €350M CL3 WP 2026",
            "eligibility": "Consortium 3+ entities, 3+ countries. TRL 4-6 preferred.",
        },
        {
            "id": "HORIZON-CL3-2026-01-SSRI-02",
            "title": "Demand-led innovation in security (PPP)",
            "url": "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-details/horizon-cl3-2026-01-ssri-02",
            "description": "Pre-commercial procurement and demand-driven innovation for security. Connects technology providers (SMEs) with public security buyers. SEEDiA can position as supplier to law enforcement, municipalities, border agencies.",
            "deadline": "2026-11-05",
            "budget": "Part of €350M CL3 WP 2026",
            "eligibility": "Consortium including end-users (police, border agencies) + tech providers.",
        },
        {
            "id": "HORIZON-CL3-2026-02-CS-ECCC-02",
            "title": "Enhancing Security, Privacy and Robustness of AI Models",
            "url": "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-details/horizon-cl3-2026-02-cs-eccc-02",
            "description": "Security and privacy of AI systems deployed in critical applications. Adversarial robustness, explainability, privacy-preserving AI. Directly relevant to SEEDiA AI camera systems used in public spaces.",
            "deadline": "2026-09-15",
            "budget": "ECCC cybersecurity component",
            "eligibility": "Consortium 3+ entities. Cybersecurity focus.",
        },
    ]

    def crawl(self):
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
                f"Applicant type: Consortium (SME as partner), min 3 countries EU\n"
                f"Relevance to SEEDiA: AI cameras (incity.io), border/urban surveillance, smart city security\n"
                f"TRL: 4-7\n"
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
