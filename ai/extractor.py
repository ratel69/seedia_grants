import json
from google import genai
from config import GEMINI_API_KEY

_client = None

def get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client

SYSTEM_PROMPT = """You are a grant intelligence analyst for SEEDiA, a Polish smart city technology company.

Company profile:
SEEDiA develops solar-powered urban infrastructure, including:
- jCharge: micromobility (e-bike/e-scooter) charging stations
- Solar shelters: smart bus shelters with solar panels
- e-paper passenger information displays
- Solar infokiosks: smart information points
- AI mobility cameras: traffic/pedestrian counting and analysis
- incity.io: urban infrastructure management platform (SaaS)
- UrbMap: mobile application for urban infrastructure mapping

SEEDiA is a Polish SME. Target customers: cities, municipalities, transport operators, real estate developers.
Strategic goals: R&D funding, pilot projects in cities, EU market expansion, resilience/dual-use infrastructure.

Analyze the grant/call text provided. Return ONLY valid JSON, no markdown, no explanation, no code blocks.

JSON schema:
{
  "grant_name": "string",
  "source_name": "string",
  "programme": "string (Horizon / EIT / PARP / NCBR / LIFE / Interreg / Regional / Other)",
  "deadline": "YYYY-MM-DD or null",
  "opening_date": "YYYY-MM-DD or null",
  "decision_date": "YYYY-MM-DD or null",
  "funding_amount_min": "integer EUR or null",
  "funding_amount_max": "integer EUR or null",
  "funding_rate": "integer percent or null",
  "own_contribution_required": "boolean or null",
  "own_contribution_pct": "integer or null",
  "eligible_applicants": ["array of strings"],
  "eligible_countries": ["array of strings"],
  "project_type": "pilotaż / B+R / demonstrator / scale-up / inne",
  "seedia_products_fit": ["array: jCharge / solar shelter / e-paper / infokiosk / AI camera / incity.io / UrbMap"],
  "fit_smart_city": "integer 0-5",
  "fit_micromobility": "integer 0-5",
  "fit_renewable_energy": "integer 0-5",
  "fit_data_ai": "integer 0-5",
  "fit_urban_infrastructure": "integer 0-5",
  "fit_resilience": "integer 0-5",
  "score_total": "integer 0-100",
  "score_reasoning": "string, max 3 sentences in Polish",
  "risk_level": "niski / średni / wysoki",
  "key_risks": "string in Polish",
  "track": "JST / R&D / EU_DIRECT",
  "recommended_action": "apply / strong watch / watch / reject",
  "suggested_concept": "string, 5 sentences in Polish describing a project concept for SEEDiA",
  "next_action": "string in Polish, concrete next step for the team"
}

Scoring methodology (total 0-100):
- Product fit (25pts): how well SEEDiA products match the call scope
- Thematic fit (20pts): smart city / mobility / renewable energy / resilience / data/AI alignment
- SEEDiA eligibility (15pts): can SEEDiA apply as SME, alone or in consortium
- Financial potential (15pts): budget size, funding rate, viability of own contribution
- Commercialization proximity (10pts): can grant lead to city sales/pilot
- Application difficulty (10pts): consortium requirements, paperwork, formal requirements
- Deadline fit (5pts): is it realistic to prepare application

Strict rules:
- Do NOT invent missing information. Use null for unknown fields.
- Be strict. Prefer rejecting weak grants over false positives.
- Auto-reject if: SEEDiA clearly not eligible, basic research only, own contribution >50% with no end customer, deadline <14 days and complex application.
- Score 80-100 = apply, 65-79 = strong watch, 45-64 = watch, <45 = reject.

Track assignment rules (mandatory):
- JST: grant is for municipalities/local governments (gmina, powiat, miasto, JST), OR allows SME+JST consortium where JST is lead/co-applicant. This is SEEDiA's PRIMARY priority — city pilots, smart city infra, mobility.
- R&D: grant is for SMEs doing research, prototyping, or technology development (B+R, TRL, innovation). SEEDiA applies alone or in business consortium.
- EU_DIRECT: direct EU programme call (LIFE, EIT, Interreg, CEF, Horizon) without JST requirement and not purely R&D-focused.

When in doubt: if JST can be a partner even optionally → assign JST."""


def extract_and_score(raw_content: str, source_name: str = "", url: str = "") -> dict:
    """Send raw grant content to Gemini for extraction and scoring."""
    prompt = f"""{SYSTEM_PROMPT}

Source: {source_name}
URL: {url}

Grant content:
{raw_content[:12000]}"""

    try:
        client = get_client()
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        text = resp.text.strip()
        # Strip markdown code blocks if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"[extractor] JSON parse error: {e}")
        return {}
    except Exception as e:
        print(f"[extractor] API error: {e}")
        return {}


def generate_fiche(grant: dict) -> str:
    """Generate a 1-page grant fiche in Markdown format."""
    prompt = f"""Na podstawie poniższych danych grantu wygeneruj fiszkę w formacie Markdown.
Fiszka musi być w języku polskim, zwięzła, gotowa do wklejenia w Asanę, Notion lub email.

Dane grantu (JSON):
{json.dumps(grant, ensure_ascii=False, indent=2)}

Format fiszki:
# [Nazwa grantu]

**Źródło:** ...  
**Program:** ...  
**Link:** ...  
**Deadline:** ...  
**Budżet:** ...  
**Poziom dofinansowania:** ...%  
**Wkład własny:** tak/nie (X%)  
**Kto może aplikować:** ...  
**Czy SEEDiA może aplikować:** tak/nie/w konsorcjum  

---

## Najlepszy produkt SEEDiA
...

## Potencjalna koncepcja projektu
...

## Partnerzy potrzebni
...

## Ryzyka
...

---

**Ocena SEEDiA fit: X/100**  
**Rekomendacja: APPLY / STRONG WATCH / WATCH / REJECT**  
**Następny krok:** ...
"""
    try:
        client = get_client()
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return resp.text
    except Exception as e:
        print(f"[fiche] Error: {e}")
        return ""
