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
from uutiset import news_loop, fetch_news

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
NEWS_CHAT_ID = int(os.getenv("NEWS_CHAT_ID"))

# 🧠 Bot setup
bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())
router = Router()


# 📩 Viestien käsittely
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
    msg = (
        "Tämän päivän Allsvenskan-ottelut:\n\n" + "\n".join(matches)
        if matches else
        "Tänään ei ole Allsvenskan-otteluita."
    )
    await message.answer(msg)


# 🚀 Käynnistä kaikki
async def main():
    db_pool = await create_pool()
    await init_db(db_pool)
    dp["db_pool"] = db_pool
    dp.include_router(router)

    # 🧪 Lähetä uutiset heti testinä
    news_items = await fetch_news()
    if news_items:
        test_msg = "<b>🧪 Testi-uutiset</b>\n\n" + "\n\n".join(news_items)
        await bot.send_message(chat_id=NEWS_CHAT_ID, text=test_msg)

    # ⏱️ Ajastetut silmukat
    asyncio.create_task(odds_loop())
    asyncio.create_task(news_loop(bot, NEWS_CHAT_ID))

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
