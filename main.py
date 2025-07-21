import os
import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from db import init_db, create_pool, add_user
from games import get_today_matches
from odds_fetcher import odds_loop

from flask import Flask
from threading import Thread

# ✅ Flask setup
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

# ✅ Telegram Bot
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

@router.message(lambda msg: not msg.text.startswith("/"))
async def handle_message(message: Message):
    telegram_id = message.from_user.id
    username = message.from_user.username
    pool = dp["db_pool"]
    await add_user(pool, telegram_id, username)
    await message.answer("Terve, olet nyt rekisteröity tietokantaan! 😊")

@router.message(Command("pelit"))
async def pelit_komento(message: Message):
    matches = await get_today_matches()
    msg = "Tämän päivän Allsvenskan-ottelut:\n\n" + "\n".join(matches) if matches else "Tänään ei ole Allsvenskan-otteluita."
    await message.answer(msg)

async def start_bot():
    db_pool = await create_pool()
    await init_db(db_pool)
    dp["db_pool"] = db_pool
    dp.include_router(router)
    asyncio.create_task(odds_loop())
    from uutiset import news_loop

...

async def main():
    db_pool = await create_pool()
    await init_db(db_pool)
    dp["db_pool"] = db_pool

    dp.include_router(router)

    # 🟡 Taustatehtävät
    asyncio.create_task(odds_loop())  # tämä voi jo olla siellä

    # 🆕 Lisää uutislooppi tähän
    chat_id = int(os.getenv("NEWS_CHAT_ID"))  # esim. sun Telegram-käyttäjän ID
    asyncio.create_task(news_loop(bot, chat_id))

    await dp.start_polling(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    
    # Käynnistetään molemmat samassa event loopissa
    async def main():
        # Flask omaksi tehtäväkseen
        loop = asyncio.get_running_loop()
        app_server = loop.run_in_executor(None, lambda: app.run(host="0.0.0.0", port=port, use_reloader=False))
        await start_bot()
    
    asyncio.run(main())
