import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router

from db import init_db, create_pool, add_user

# ✅ Hae Telegram-token ympäristömuuttujista
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# ✅ Luo botti ja dispatcher
bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# ✅ Lisää viestinkäsittelijä
@router.message()
async def handle_message(message: Message):
    telegram_id = message.from_user.id
    username = message.from_user.username

    await add_user(dp["db_pool"], telegram_id, username)
    await message.answer("Terve, olet nyt rekisteröity tietokantaan! 😊")

# ✅ Pääfunktio
async def main():
    db_pool = await create_pool()
    await init_db(db_pool)
    dp["db_pool"] = db_pool  # Tallennetaan pool Dispatcherin kontekstiin
    dp.include_router(router)

    await dp.start_polling(bot)

# ✅ Käynnistys
if __name__ == "__main__":
    asyncio.run(main())
