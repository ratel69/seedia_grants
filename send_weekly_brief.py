"""
Jednorazowy skrypt — wysyła weekly brief na Slack.
Używany przez GitHub Actions w poniedziałki po scanie.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scheduler'))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from database import get_grants, get_upcoming_deadlines
from slack_alerts import send_weekly_brief

grants_apply       = get_grants({"recommended_action": "apply"}, limit=10)
grants_watch_strong = get_grants({"recommended_action": "strong watch"}, limit=10)
grants_watch       = get_grants({"recommended_action": "watch"}, limit=10)
deadlines          = get_upcoming_deadlines(days=30)

all_watch = grants_watch_strong + grants_watch
ok = send_weekly_brief(grants_apply, all_watch, deadlines)
print("Weekly brief:", "✅ wysłany" if ok else "❌ błąd")
