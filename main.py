import os
import requests
import urllib.parse
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
TOKEN = os.getenv("BOT_TOKEN")

def build_newsapi_url(query, from_date, to_date, language):
    enhanced_query = (
        f"({query}) AND "
        "(pelaajakaupat OR loukkaantumiset OR kokoonpano OR siirto OR trade OR injury OR lineup OR transfer OR coach)"
    )
    encoded_query = urllib.parse.quote_plus(enhanced_query)
    return (
        f"https://newsapi.org/v2/everything?"
        f"q={encoded_query}&"
        f"from={from_date}&"
        f"to={to_date}&"
        f"language={language}&"
        f"sortBy=publishedAt&"
        f"apiKey={NEWS_API_KEY}"
    )

async def uutiset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text(
            "Käytä komentoa muodossa:\n"
            "/uutiset <aihe> [päivämäärä]\n"
            "Esim.:\n"
            "/uutiset nhl\n"
            "/uutiset nhl 2025-07-22"
        )
        return

    query = args[0]
    today = datetime.utcnow().date()

    if len(args) == 2:
        date_str = args[1]
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            await update.message.reply_text("Virheellinen päivämäärämuoto. Käytä YYYY-MM-DD.")
            return
        from_date = to_date = date_obj.isoformat()
    else:
        from_date = (today - timedelta(days=10)).isoformat()
        to_date = today.isoformat()

    urls = [
        build_newsapi_url(query, from_date, to_date, "fi"),
        build_newsapi_url(query, from_date, to_date, "en")
    ]

    all_articles = []
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])
            all_articles.extend(articles)

    if not all_articles:
        await update.message.reply_text("Ei löytynyt uutisia haulla.")
        return

    sorted_articles = sorted(
        all_articles,
        key=lambda a: a.get("publishedAt", ""),
        reverse=True
    )[:10]

    reply_text = f"<b>Uutiset aiheesta '{query}' ajalta {from_date} - {to_date}:</b>\n\n"
    for article in sorted_articles:
        title = article.get("title", "Ei otsikkoa")
        url = article.get("url", "")
        reply_text += f"• <a href='{url}'>{title}</a>\n"

    await update.message.reply_text(
        reply_text,
        parse_mode="HTML",
        disable_web_page_preview=True
    )

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("uutiset", uutiset))
    print("Botti käynnissä...")
    app.run_polling()
