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

# ✅ Bot token
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# ✅ Luo bot ja dispatcher
bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

# ✅ Luo router
router = Router()

# 🟢 Käsittelijä normaalille viestille (ei komento)
@router.message(lambda msg: not msg.text.startswith("/"))
async def handle_message(message: Message):
    telegram_id = message.from_user.id
    username = message.from_user.username

    pool = dp["db_pool"]
    await add_user(pool, telegram_id, username)
    await message.answer("Terve, olet nyt rekisteröity tietokantaan! 😊")

# 🟢 /pelit-komento
@router.message(Command("pelit"))
async def pelit_komento(message: Message):
    matches = await get_today_matches()
    if matches:
        msg = "Tämän päivän Allsvenskan-ottelut:\n\n" + "\n".join(matches)
    else:
        msg = "Tänään ei ole Allsvenskan-otteluita."
    await message.answer(msg)

# ✅ Pääfunktio
async def main():
    db_pool = await create_pool()
    await init_db(db_pool)
    dp["db_pool"] = db_pool

    dp.include_router(router)

    # 🟡 Taustatehtävä esim. odds_loop
    asyncio.create_task(odds_loop())

    await dp.start_polling(bot)

# ✅ Suorita ohjelma
if __name__ == "__main__":
    asyncio.run(main())

