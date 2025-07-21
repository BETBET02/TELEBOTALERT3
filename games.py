import os
import aiohttp
from datetime import datetime

API_KEY = os.getenv("ODDS_API_KEY")
BASE_URL = "https://api.the-odds-api.com/v4/sports/soccer_sweden_allsvenskan/events"

async def get_today_matches():
    if not API_KEY:
        raise RuntimeError("ODDS_API_KEY ympäristömuuttuja ei ole asetettu!")

    async with aiohttp.ClientSession() as session:
        params = {"apiKey": API_KEY}
        async with session.get(BASE_URL, params=params) as resp:
            if resp.status != 200:
                raise RuntimeError(f"API-kutsu epäonnistui, statuskoodi: {resp.status}")
            data = await resp.json()

    today = datetime.utcnow().date()
    matches = []

    for match in data:
        match_time = datetime.fromisoformat(match["commence_time"].replace("Z", "+00:00"))
        if match_time.date() == today:
            home = match.get("home_team", "Tuntematon")
            away = match.get("away_team", "Tuntematon")
            time_str = match_time.strftime("%H:%M")
            matches.append(f"{home} vs {away} klo {time_str}")

    return matches
