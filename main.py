import os
import asyncio
import threading
from flask import Flask
from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command

from db import init_db, create_pool, add_user
from games import get_today_matches
from odds_fetcher import odds_loop

# Telegram bot token ympäristömuuttujasta
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 8000))  # Render käyttää tätä

# Luo Flask app
app = Flask(__name__)

@app.route("/")
def index():
    return "Bot is running!"

# Luo bot ja dispatcher
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
    if matches:
        msg = "Tämän päivän Allsvenskan-ottelut:\n\n" + "\n".join(matches)
    else:
        msg = "Tänään ei ole Allsvenskan-otteluita."
    await message.answer(msg)

async def start_bot():
    db_pool = await create_pool()
    await init_db(db_pool)
    dp["db_pool"] = db_pool
    dp.include_router(router)

    asyncio.create_task(odds_loop())

    await dp.start_polling(bot)

def run_asyncio_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot())

if __name__ == "__main__":
    # Luo uusi asyncio loop botille Flaskin rinnalle
    new_loop = asyncio.new_event_loop()
    t = threading.Thread(target=run_asyncio_loop, args=(new_loop,))
    t.start()

    # Käynnistä Flask web-palvelin
    app.run(host="0.0.0.0", port=PORT)


