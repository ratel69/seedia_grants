"""
Daily Grant Scanner — serce systemu.
Uruchamia wszystkie crawlery, deduplikuje, wysyła do AI extraction i zapisuje do bazy.
"""
import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../crawlers'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../ai'))

from database import (
    get_db, upsert_grant, get_grant_by_url, save_scan_log,
    get_unalerted_high_score_grants, mark_alert_sent, save_fiche
)
from extractor import extract_and_score, generate_fiche
from slack_alerts import send_new_grant_alert, send_deadline_alerts

# Import all crawlers
from parp_crawler import PARPCrawler
from ncbr_crawler import NCBRCrawler
from eit_crawler import EITCrawler
from eu_portal_crawler import EUPortalCrawler
from life_crawler import LIFECrawler
from interreg_crawler import InterregCrawler
from eic_accelerator_crawler import EICAcceleratorCrawler
from eui_crawler import EUICrawler
from parp_smart_crawler import PARPSmartCrawler
from cef_digital_crawler import CEFDigitalCrawler
from fundusze_ue_crawler import FunduszeUECrawler
# JST-focused crawlers
from feniks_crawler import FENiKSCrawler
from fundusze_norweskie_crawler import FunduszeNorweskieCrawler
from horyzont_misja_miast_crawler import HoryzonMisjaMiastCrawler
from atlasdotacji_crawler import AtlasDotacjiCrawler

CRAWLERS = [
    # R&D
    NCBRCrawler(),
    EITCrawler(),
    EICAcceleratorCrawler(),
    PARPCrawler(),
    PARPSmartCrawler(),
    # EU Direct
    EUPortalCrawler(),
    LIFECrawler(),
    InterregCrawler(),
    CEFDigitalCrawler(),
    FunduszeUECrawler(),
    # JST — priorytet
    EUICrawler(),
    FENiKSCrawler(),
    FunduszeNorweskieCrawler(),
    HoryzonMisjaMiastCrawler(),
    AtlasDotacjiCrawler(),
]

def run_daily_scan():
    print(f"\n{'='*60}")
    print(f"SEEDiA Grant Scanner — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    total_new = 0
    total_updated = 0

    for crawler in CRAWLERS:
        source_start = time.time()
        print(f"\n[scan] Crawling: {crawler.source_name}...")

        try:
            grants = crawler.crawl()
            print(f"[scan] Found {len(grants)} items from {crawler.source_name}")

            new_count = 0
            for grant_raw in grants:
                url = grant_raw.get("url", "")
                if not url:
                    continue

                # Deduplication check
                existing = get_grant_by_url(url)
                if existing and existing.get("ai_extracted"):
                    print(f"[scan] Skip (exists): {url[:80]}")
                    continue

                # AI extraction + scoring
                print(f"[scan] Extracting: {grant_raw.get('grant_name', url)[:60]}...")
                extracted = extract_and_score(
                    raw_content=grant_raw.get("raw_content", ""),
                    source_name=grant_raw.get("source_name", ""),
                    url=url
                )

                if not extracted:
                    print(f"[scan] Extraction failed for {url[:60]}")
                    continue

                # Merge raw + extracted data
                grant_data = {
                    "url": url,
                    "source_name": grant_raw.get("source_name", ""),
                    "programme": extracted.get("programme") or grant_raw.get("programme", ""),
                    "raw_content": grant_raw.get("raw_content", "")[:5000],
                    "grant_name": extracted.get("grant_name") or grant_raw.get("grant_name", ""),
                    "deadline": extracted.get("deadline"),
                    "opening_date": extracted.get("opening_date"),
                    "decision_date": extracted.get("decision_date"),
                    "funding_amount_min": extracted.get("funding_amount_min"),
                    "funding_amount_max": extracted.get("funding_amount_max"),
                    "funding_rate": extracted.get("funding_rate"),
                    "own_contribution_required": extracted.get("own_contribution_required"),
                    "own_contribution_pct": extracted.get("own_contribution_pct"),
                    "eligible_applicants": extracted.get("eligible_applicants", []),
                    "eligible_countries": extracted.get("eligible_countries", []),
                    "project_type": extracted.get("project_type"),
                    "seedia_products_fit": extracted.get("seedia_products_fit", []),
                    "fit_smart_city": extracted.get("fit_smart_city"),
                    "fit_micromobility": extracted.get("fit_micromobility"),
                    "fit_renewable_energy": extracted.get("fit_renewable_energy"),
                    "fit_data_ai": extracted.get("fit_data_ai"),
                    "fit_urban_infrastructure": extracted.get("fit_urban_infrastructure"),
                    "fit_resilience": extracted.get("fit_resilience"),
                    "score_total": extracted.get("score_total"),
                    "score_reasoning": extracted.get("score_reasoning"),
                    "risk_level": extracted.get("risk_level"),
                    "key_risks": extracted.get("key_risks"),
                    "recommended_action": extracted.get("recommended_action"),
                    "track": extracted.get("track"),
                    "suggested_concept": extracted.get("suggested_concept"),
                    "next_action": extracted.get("next_action"),
                    "status": "new",
                    "ai_extracted": True,
                    "ai_extracted_at": datetime.utcnow().isoformat(),
                    "alert_sent": False
                }

                # Remove None values to avoid Supabase issues
                grant_data = {k: v for k, v in grant_data.items() if v is not None}

                saved = upsert_grant(grant_data)
                if saved:
                    new_count += 1
                    score = grant_data.get("score_total", 0) or 0
                    print(f"[scan] Saved: {grant_data['grant_name'][:50]} | Score: {score} | {grant_data.get('recommended_action', '?')}")

                    # Generate fiche for score > 45
                    if score > 45 and saved.get("id"):
                        fiche_md = generate_fiche(grant_data)
                        if fiche_md:
                            save_fiche({
                                "grant_id": saved["id"],
                                "content_md": fiche_md
                            })

                time.sleep(1)  # Be polite to APIs

            total_new += new_count
            duration = time.time() - source_start

            save_scan_log({
                "source_name": crawler.source_name,
                "new_grants": new_count,
                "duration_sec": round(duration, 2)
            })

        except Exception as e:
            print(f"[scan] ERROR in {crawler.source_name}: {e}")
            save_scan_log({
                "source_name": crawler.source_name,
                "new_grants": 0,
                "errors": str(e)
            })

    # Send Slack alerts for high-score grants
    print(f"\n[scan] Sending Slack alerts...")
    high_score_grants = get_unalerted_high_score_grants()
    for grant in high_score_grants:
        sent = send_new_grant_alert(grant)
        if sent:
            mark_alert_sent(grant["id"])

    # Send deadline reminders
    send_deadline_alerts()

    print(f"\n{'='*60}")
    print(f"[scan] DONE — New: {total_new}, Updated: {total_updated}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run_daily_scan()
