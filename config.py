import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
SPORTSRADAR_API_KEY = os.getenv("SPORTSRADAR_API_KEY", "").strip()
THRESHOLD_PERCENT = float(os.getenv("THRESHOLD_PERCENT", "20"))
