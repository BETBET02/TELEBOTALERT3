import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from db import create_pool, init_db, add_user
from db import init_db

async def main():
    await init_db()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

from aiogram.client.default import DefaultBotProperties

bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

db_pool = None  # Tämä pidetään globaalina viitteenä

@dp.message()
async def handle_message(message: Message):
    global db_pool
    telegram_id = message.from_user.id
    username = message.from_user.username

    await add_user(db_pool, telegram_id, username)

    await message.answer("Terve, olet nyt rekisteröity tietokantaan! 😊")

    asyncio.run(main())

await init_db()
