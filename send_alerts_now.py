"""
Jednorazowy skrypt — wysyła alerty Slack dla wszystkich grantów
z alert_sent=false i score >= 60, następnie oznacza je jako alert_sent=true.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scheduler'))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from database import get_db
from slack_alerts import send_new_grant_alert

def main():
    db = get_db()

    # Pobierz granty z wysokim score, jeszcze niezaalertowane
    result = db.table("grants") \
        .select("*") \
        .eq("alert_sent", False) \
        .gte("score_total", 60) \
        .order("score_total", desc=True) \
        .execute()

    grants = result.data or []
    print(f"Znaleziono {len(grants)} grantów do zaprocentowania:\n")

    sent = 0
    failed = 0

    for g in grants:
        name = g.get("grant_name", "?")
        score = g.get("score_total", 0)
        print(f"  → {name} | {score}/100 ... ", end="", flush=True)

        ok = send_new_grant_alert(g)

        if ok:
            # Oznacz jako alert_sent = true
            db.table("grants").update({"alert_sent": True}).eq("id", g["id"]).execute()
            print("✅ wysłano")
            sent += 1
        else:
            print("❌ błąd")
            failed += 1

    print(f"\nPodsumowanie: {sent} wysłanych, {failed} błędów.")

if __name__ == "__main__":
    main()
