import os
import asyncio
from telegram.ext import ApplicationBuilder
from telegram.error import TimedOut

# Oletetaan, että BOT_TOKEN ja CHAT_ID on asetettu ympäristömuuttujiin
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))  # Telegram-ryhmän chat ID, esim. -123456789

# Importoi omat moduulit, jotka kirjoitat myöhemmin
from data_fetcher import fetch_odds_changes, fetch_sports_news, fetch_lineup_changes, fetch_props_alerts
from analyzer import analyze_odds_changes, analyze_news, analyze_lineups, analyze_props

async def send_message(app, text):
    try:
        await app.bot.send_message(chat_id=CHAT_ID, text=text)
    except TimedOut:
        print("TimedOut, yritetään uudestaan pian.")
    except Exception as e:
        print(f"Virhe viestin lähetyksessä: {e}")

async def odds_task(app):
    while True:
        try:
            odds_data = await fetch_odds_changes()          # Hae kerroindata API:sta
            alerts = analyze_odds_changes(odds_data)        # Analysoi laskut ja nousut
            for alert in alerts:
                await send_message(app, alert)
        except Exception as e:
            print(f"Virhe kerrointiedon käsittelyssä: {e}")
        await asyncio.sleep(1800)  # 30 min

async def news_lineup_task(app):
    while True:
        try:
            news_data = await fetch_sports_news()
            lineup_data = await fetch_lineup_changes()

            news_alerts = analyze_news(news_data)
            lineup_alerts = analyze_lineups(lineup_data)

            for alert in news_alerts + lineup_alerts:
                await send_message(app, alert)
        except Exception as e:
            print(f"Virhe uutisten/kokoonpanojen käsittelyssä: {e}")
        await asyncio.sleep(2700)  # 45 min

async def props_task(app):
    while True:
        try:
            props_data = await fetch_props_alerts()
            props_alerts = analyze_props(props_data)
            for alert in props_alerts:
                await send_message(app, alert)
        except Exception as e:
            print(f"Virhe props-vedonlyönnin käsittelyssä: {e}")
        await asyncio.sleep(1800)  # 30 min tai muokkaa tarpeen mukaan

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Käynnistä tehtävät taustalle
    asyncio.create_task(odds_task(app))
    asyncio.create_task(news_lineup_task(app))
    asyncio.create_task(props_task(app))

    app.run_polling()

if __name__ == "__main__":
    main()
