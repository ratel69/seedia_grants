"""
Slack alerter dla SEEDiA Grant Intelligence System.
Używa Incoming Webhooks (prostsze i bardziej niezawodne niż token API).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

import requests
from datetime import date, timedelta
from database import get_upcoming_deadlines, save_alert, get_db
from config import SLACK_WEBHOOK, SCORE_ALERT_THRESHOLD

ACTION_EMOJI = {
    "apply":        "🚀",
    "strong watch": "👀",
    "watch":        "📋",
    "reject":       "❌"
}

TRACK_BADGE = {
    "JST":       "🏛️ JST",
    "R&D":       "🔬 R&D",
    "EU_DIRECT": "🇪🇺 EU Direct",
}

def _score_bar(score: int) -> str:
    filled = round(score / 10)
    return "█" * filled + "░" * (10 - filled)

def _post(blocks: list, text: str = "") -> bool:
    if not SLACK_WEBHOOK:
        print("[slack] Brak SLACK_WEBHOOK w .env")
        return False
    try:
        r = requests.post(SLACK_WEBHOOK, json={"text": text, "blocks": blocks}, timeout=10)
        if r.status_code != 200:
            print(f"[slack] Error: {r.status_code} {r.text}")
            return False
        return True
    except Exception as e:
        print(f"[slack] Exception: {e}")
        return False


def send_new_grant_alert(grant: dict) -> bool:
    score = grant.get("score_total") or 0
    if score < SCORE_ALERT_THRESHOLD:
        return False

    action = grant.get("recommended_action", "watch")
    emoji = ACTION_EMOJI.get(action, "📋")
    deadline = grant.get("deadline") or "nieznany"
    products = ", ".join(grant.get("seedia_products_fit") or []) or "—"

    bmin = grant.get("funding_amount_min")
    bmax = grant.get("funding_amount_max")
    if bmin and bmax:
        budget = f"{bmin:,}–{bmax:,} EUR"
    elif bmax:
        budget = f"do {bmax:,} EUR"
    else:
        budget = "nieznany"

    rate = grant.get("funding_rate")
    funding_str = f"{rate}% dofinansowania" if rate else "—"

    track = grant.get("track") or ""
    track_badge = TRACK_BADGE.get(track, f"_{track}_" if track else "")

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"{emoji} Nowy grant SEEDiA — {score}/100"}
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*<{grant.get('url','#')}|{grant.get('grant_name','Bez nazwy')}>*\n_{grant.get('programme','')} · {grant.get('source_name','')}_{f'   {track_badge}' if track_badge else ''}"
            }
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Deadline:*\n{deadline}"},
                {"type": "mrkdwn", "text": f"*Budżet:*\n{budget}"},
                {"type": "mrkdwn", "text": f"*Dofinansowanie:*\n{funding_str}"},
                {"type": "mrkdwn", "text": f"*Produkty SEEDiA:*\n{products}"},
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Score:* {_score_bar(score)} {score}/100\n*Rekomendacja:* `{action.upper()}`"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Uzasadnienie:*\n{grant.get('score_reasoning','—')}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Następny krok:*\n{grant.get('next_action','—')}"
            }
        },
        {"type": "divider"}
    ]

    success = _post(blocks, text=f"{emoji} Nowy grant: {grant.get('grant_name')} | {score}/100 | {action.upper()}")

    if success:
        save_alert({
            "grant_id": grant["id"],
            "alert_type": "new_high_score",
            "channel": "slack_webhook",
            "message": f"Score {score} — {action}"
        })

    return success


def send_deadline_alerts():
    THRESHOLDS = [30, 14, 7, 2]
    today = date.today()

    for days in THRESHOLDS:
        grants = get_upcoming_deadlines(days=days)
        for grant in grants:
            deadline_str = grant.get("deadline")
            if not deadline_str:
                continue
            try:
                deadline = date.fromisoformat(deadline_str)
            except:
                continue

            days_left = (deadline - today).days
            if days_left != days:
                continue

            db = get_db()
            existing = db.table("alerts").select("id").eq("grant_id", grant["id"]).eq("alert_type", f"deadline_{days}d").execute()
            if existing.data:
                continue

            score = grant.get("score_total") or 0
            action = grant.get("recommended_action", "watch")
            emoji = "🔴" if days <= 2 else ("🟡" if days <= 7 else "⏰")

            blocks = [
                {"type": "header", "text": {"type": "plain_text", "text": f"{emoji} Deadline za {days} dni!"}},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*<{grant.get('url','#')}|{grant.get('grant_name','Bez nazwy')}>*\n_{grant.get('programme','')} · Score: {score}/100 · `{action.upper()}`_"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Deadline:*\n{deadline_str}"},
                        {"type": "mrkdwn", "text": f"*Pozostało:*\n*{days} dni*"},
                    ]
                },
                {"type": "divider"}
            ]

            _post(blocks, text=f"{emoji} Deadline za {days} dni: {grant.get('grant_name')}")
            save_alert({
                "grant_id": grant["id"],
                "alert_type": f"deadline_{days}d",
                "channel": "slack_webhook",
                "message": f"Deadline za {days} dni — {deadline_str}"
            })


def send_weekly_brief(grants_apply: list, grants_watch: list, deadlines: list) -> bool:
    from datetime import datetime
    week = datetime.now().strftime("%d.%m.%Y")

    def fmt(g):
        score = g.get("score_total", "?")
        dl = g.get("deadline") or "?"
        track = g.get("track") or ""
        badge = TRACK_BADGE.get(track, "")
        badge_str = f" {badge}" if badge else ""
        return f"• <{g.get('url','#')}|{g.get('grant_name','?')[:50]}>{badge_str} — *{score}/100* — deadline: {dl}"

    apply_list  = "\n".join(fmt(g) for g in grants_apply[:5])  or "_brak_"
    watch_list  = "\n".join(fmt(g) for g in grants_watch[:5])  or "_brak_"
    dl_list     = "\n".join(fmt(g) for g in deadlines[:5])     or "_brak_"

    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": f"📊 SEEDiA Grant Brief — {week}"}},
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*🚀 APPLY ({len(grants_apply)})*\n{apply_list}"}},
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*👀 WATCH ({len(grants_watch)})*\n{watch_list}"}},
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*⏰ Deadline w 30 dniach ({len(deadlines)})*\n{dl_list}"}},
        {"type": "divider"},
        {"type": "section", "text": {"type": "mrkdwn", "text": "_SEEDiA Grant Intelligence System_"}}
    ]

    return _post(blocks, text=f"📊 SEEDiA Grant Brief — {week}")
