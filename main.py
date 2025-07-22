import os
import requests
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
TOKEN = os.getenv("BOT_TOKEN")

import urllib.parse

def build_newsapi_url(query, from_date, to_date):
    enhanced_query = f"({query}) AND (pelaajakaupat OR loukkaantumiset OR kokoonpanomuutokset OR urheilu)"
    encoded_query = urllib.parse.quote_plus(enhanced_query)
    return (
        f"https://newsapi.org/v2/everything?"
        f"q={encoded_query}&"
        f"from={from_date}&"
        f"to={to_date}&"
        f"language=fi&"
        f"sortBy=publishedAt&"
        f"apiKey={NEWS_API_KEY}"
    )

async def uutiset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Käytä /uutiset <hakusana tai päivämäärä (YYYY-MM-DD)>")
        return

    query = context.args[0]

    try:
        # Yritetään parsia päivämäärä
        date_obj = datetime.strptime(query, "%Y-%m-%d")
        from_date = date_obj.strftime("%Y-%m-%d")
        to_date = from_date
    except ValueError:
        # Ei päivämäärää, käytetään nyt - 14 päivää
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")

    url = build_newsapi_url(query=query + " urheilu", from_date=from_date, to_date=to_date)

    response = requests.get(url)
    if response.status_code != 200:
        await update.message.reply_text("Uutisten hakeminen epäonnistui.")
        return

    data = response.json()
    articles = data.get("articles", [])

    if not articles:
        await update.message.reply_text("Ei löytynyt uutisia annetulla hakusanalla.")
        return

    reply_text = "Uutisia:\n"
    for article in articles[:5]:  # Näytetään max 5 uutista
        title = article.get("title", "Ei otsikkoa")
        url = article.get("url", "")
        reply_text += f"• {title}\n{url}\n\n"

    await update.message.reply_text(reply_text)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("uutiset", uutiset))
    print("Botti käynnissä...")
    app.run_polling()
