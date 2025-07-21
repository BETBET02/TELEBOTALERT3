# uutiset.py
import os
import aiohttp
import asyncio
from aiogram import Bot
from datetime import datetime

NEWS_API_KEY = os.getenv("NEWSAPI_KEY")

SPORTS = ["football", "tennis", "ice hockey"]  # voit lisätä lajeja
NEWS_CHAT_ID = os.getenv("NEWS_CHAT_ID")  # vaihtoehtoisesti voit kovakoodata ID:n

async def fetch_news():
    async with aiohttp.ClientSession() as session:
        headlines = []
        for sport in SPORTS:
            url = (
                f"https://newsapi.org/v2/everything?"
                f"q={sport}&"
                f"sortBy=publishedAt&"
                f"language=en&"
                f"pageSize=3&"
                f"apiKey={NEWS_API_KEY}"
            )
            async with session.get(url) as response:
                data = await response.json()
                for article in data.get("articles", []):
                    title = article["title"]
                    source = article["source"]["name"]
                    headlines.append(f"🔹 <b>{title}</b> ({source})")
        return headlines

async def news_loop(bot: Bot, chat_id: int):
    while True:
        news_items = await fetch_news()
        if news_items:
            timestamp = datetime.now().strftime("%H:%M")
            msg = f"<b>📰 Uutiskatsaus ({timestamp})</b>\n\n" + "\n\n".join(news_items)
            await bot.send_message(chat_id=chat_id, text=msg)
        await asyncio.sleep(3600)  # 1h välein
