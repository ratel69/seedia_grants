import os
from dotenv import load_dotenv

load_dotenv()

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# OpenAI (opcjonalnie)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Slack
SLACK_TOKEN = os.getenv("SLACK_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#grants")
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")

# Scoring thresholds
SCORE_ALERT_THRESHOLD = 65
SCORE_APPLY_THRESHOLD = 80

# Scheduler
SCAN_HOUR_UTC = 6   # codziennie o 6:00 UTC (8:00 CEST)
BRIEF_DAY = "monday"
BRIEF_HOUR_UTC = 7
