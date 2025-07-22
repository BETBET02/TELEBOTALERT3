import os
import asyncio
from aiogram import Bot

async def clear_updates():
    TELEGRAM_TOKEN = os.getenv(bot_token)
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    print("Webhook deleted and pending updates cleared!")
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(clear_updates())
