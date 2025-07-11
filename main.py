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
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hei! Botin koodi toimii.')

async def main():
    app = ApplicationBuilder().token("TELEGRAM_BOT_TOKEN_HERE").build()
    app.add_handler(CommandHandler("start", start))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
import asyncio
import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

TOKEN = "TELEGRAM_BOT_TOKEN_HERE"
DATABASE_URL = "postgresql://user:password@host:port/dbname"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Yhteys tietokantaan muuttujaan, alustetaan myöhemmin
db_pool = None

async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    # Luodaan taulu, jos ei ole
    async with db_pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                chat_id BIGINT PRIMARY KEY,
                username TEXT
            )
        """)

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    chat_id = message.chat.id
    username = message.from_user.username or message.from_user.full_name

    async with db_pool.acquire() as conn:
        # Lisätään käyttäjä tai päivitetään nimi
        await conn.execute("""
            INSERT INTO users(chat_id, username) VALUES($1, $2)
            ON CONFLICT (chat_id) DO UPDATE SET username = EXCLUDED.username
        """, chat_id, username)
    
    await message.answer(f"Tervetuloa, {username}!")

async def broadcast_message():
    while True:
        await asyncio.sleep(30)  # odota 30 sekuntia

        async with db_pool.acquire() as conn:
            rows = await conn.fetch("SELECT chat_id FROM users")
        
        for row in rows:
            try:
                await bot.send_message(row["chat_id"], "Päivitys: Tämä on testiviesti.")
            except Exception as e:
                print(f"Virhe viestin lähetyksessä chat_id:lle {row['chat_id']}: {e}")

async def on_startup(dp):
    await init_db()
    # Käynnistä taustatehtävä
    asyncio.create_task(broadcast_message())

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
