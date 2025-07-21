# games.py
import os
import aiohttp
from datetime import datetime

API_KEY = os.getenv("ODDS_API_KEY")
BASE_URL = "https://api.the-odds-api.com/v4/sports/soccer_sweden_allsvenskan/events"

async def get_today_matches():
    async with aiohttp.ClientSession() as session:
        params = {
            "apiKey": API_KEY
        }
        async with session.get(BASE_URL, params=params) as resp:
            data = await resp.json()

    today = datetime.utcnow().date()
    matches = []

    for match in data:
        match_time = datetime.fromisoformat(match["commence_time"].replace("Z", "+00:00"))
        if match_time.date() == today:
            home = match["home_team"]
            away = match["away_team"]
            time_str = match_time.strftime("%H:%M")
            matches.append(f"{home} vs {away} klo {time_str}")

    return matches
