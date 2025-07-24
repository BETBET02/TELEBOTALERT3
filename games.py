import requests
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

SPORTSRADAR_API_KEY = "YOUR_SPORTSRADAR_KEY"

async def ottelut(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date = datetime.now().strftime('%Y-%m-%d')
    url = f"https://api.sportradar.com/soccer/trial/v4/en/schedules/{date}/schedule.json?api_key={SPORTSRADAR_API_KEY}"

    r = requests.get(url)
    if r.status_code != 200:
        await update.message.reply_text("Tietojen haku epäonnistui.")
        return

    data = r.json()
    matches = data.get("sport_events", [])[:5]

    if not matches:
        await update.message.reply_text("Tänään ei ole otteluita.")
        return

    message = "Tämän päivän ottelut:\n"
    for m in matches:
        home = m["competitors"][0]["name"]
        away = m["competitors"][1]["name"]
        time = m["scheduled"][11:16]
        message += f"{time}: {home} vs {away}\n"

    await update.message.reply_text(message)
