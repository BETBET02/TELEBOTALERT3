import aiohttp
import asyncio
import os
from aiogram import Bot
from datetime import datetime

ODDS_API_KEY = os.getenv("ODDS_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # esim. ryhmän ID

SPORT = "soccer_sweden_allsvenskan"
REGION = "eu"
MARKET = "h2h"

bot = Bot(token=TELEGRAM_TOKEN)

# Tallennetaan viimeisimmät kertoimet muistiin
previous_odds = {}

async def fetch_odds():
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": REGION,
        "markets": MARKET,
        "oddsFormat": "decimal"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                print(f"OddsAPI virhe: {resp.status}")
                return []

            data = await resp.json()
            return data

def calculate_percentage_change(old, new):
    try:
        return ((new - old) / old) * 100
    except ZeroDivisionError:
        return 0

async def check_for_changes():
    global previous_odds
    data = await fetch_odds()

    for match in data:
        match_id = match["id"]
        home_team = match["home_team"]
        away_team = match["away_team"]

        try:
            outcomes = match["bookmakers"][0]["markets"][0]["outcomes"]
        except IndexError:
            continue

        current_odds = {o["name"]: float(o["price"]) for o in outcomes}

        if match_id in previous_odds:
            for team in current_odds:
                old = previous_odds[match_id].get(team)
                new = current_odds[team]
                if old:
                    change = calculate_percentage_change(old, new)
                    if change <= -15 or change >= 20:
                        await bot.send_message(
                            TELEGRAM_CHAT_ID,
                            f"📉 *Kerroinmuutos havaitty!*\n\n"
                            f"{home_team} vs {away_team}\n"
                            f"{team} kerroin muuttui:\n"
                            f"{old:.2f} ➡️ {new:.2f} ({change:.1f}%)",
                            parse_mode="Markdown"
                        )

        previous_odds[match_id] = current_odds

async def odds_loop():
    while True:
        try:
            await check_for_changes()
        except Exception as e:
            print(f"Virhe odds_loopissa: {e}")
        await asyncio.sleep(1800)  # 30 min
