import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from db import create_pool, init_db, add_user

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(token=TELEGRAM_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

db_pool = None  # Tämä pidetään globaalina viitteenä

@dp.message()
async def handle_message(message: Message):
    global db_pool
    telegram_id = message.from_user.id
    username = message.from_user.username

    await add_user(db_pool, telegram_id, username)

    await message.answer("Terve, olet nyt rekisteröity tietokantaan! 😊")

async def main():
    global db_pool
    db_pool = await create_pool()
    await init_db(db_pool)

    print("✅ Bot is running and connected to the database.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

