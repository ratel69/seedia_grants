"""
APScheduler — zastępuje Make.com.
Uruchamia daily scan i weekly brief.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seedia-scheduler")

scheduler = BlockingScheduler(timezone="UTC")

def daily_scan_job():
    logger.info(f"[scheduler] Starting daily scan — {datetime.utcnow()}")
    try:
        from scanner import run_daily_scan
        run_daily_scan()
    except Exception as e:
        logger.error(f"[scheduler] Daily scan error: {e}")

def weekly_brief_job():
    logger.info(f"[scheduler] Starting weekly brief — {datetime.utcnow()}")
    try:
        from database import get_grants, get_upcoming_deadlines
        from slack_alerts import send_weekly_brief

        grants_apply = get_grants({"recommended_action": "apply"}, limit=10)
        grants_watch_strong = get_grants({"recommended_action": "strong watch"}, limit=10)
        grants_watch = get_grants({"recommended_action": "watch"}, limit=10)
        deadlines = get_upcoming_deadlines(days=30)

        all_watch = grants_watch_strong + grants_watch
        send_weekly_brief(grants_apply, all_watch, deadlines)
    except Exception as e:
        logger.error(f"[scheduler] Weekly brief error: {e}")

# Scan: poniedziałek i środa o 7:00 UTC (9:00 CEST)
scheduler.add_job(
    daily_scan_job,
    CronTrigger(day_of_week="mon,wed", hour=7, minute=0, timezone="UTC"),
    id="grant_scan",
    name="Grant Scan (Mon/Wed)",
    replace_existing=True
)

# Weekly brief: poniedziałek 7:30 UTC (9:30 CEST) — po scanie
scheduler.add_job(
    weekly_brief_job,
    CronTrigger(day_of_week="mon", hour=7, minute=30, timezone="UTC"),
    id="weekly_brief",
    name="Weekly Grant Brief (Monday)",
    replace_existing=True
)

if __name__ == "__main__":
    logger.info("[scheduler] SEEDiA Grant Scheduler starting...")
    logger.info("[scheduler] Grant scan: Mon & Wed 07:00 UTC (09:00 CEST)")
    logger.info("[scheduler] Weekly brief: Monday 07:30 UTC (09:30 CEST)")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("[scheduler] Scheduler stopped.")
